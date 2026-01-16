use actix_web::{web, App, HttpServer, HttpResponse, Result, middleware, HttpRequest};
use serde::{Serialize};
use serde_json::Value;
use reqwest::Client;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use log::{info, error};
use std::env;

mod auth;
mod error;
mod validation;
mod logging;

use auth::AuthMiddleware;
use error::ApiError;
use validation::{validate_input, AuthRequest};
use logging::setup_logging;

// Configuration structure
#[derive(Debug, Clone)]
struct Config {
    user_service_url: String,
    chat_service_url: String,
    message_service_url: String,
    port: u16,
}

// Service health status
#[derive(Debug, Serialize, Clone)]
struct ServiceStatus {
    name: String,
    url: String,
    status: String,
    last_checked: String,
}

// Gateway state
struct AppState {
    config: Config,
    http_client: Client,
    service_statuses: Arc<RwLock<HashMap<String, ServiceStatus>>>,
}

// Health check response
#[derive(Serialize)]
struct HealthResponse {
    status: String,
    version: String,
    services: Vec<ServiceStatus>,
    timestamp: String,
}

// Proxy function to forward requests to microservices
async fn proxy_request(
    client: &Client,
    service_url: &str,
    path: &str,
    method: &str,
    body: Option<Value>,
) -> Result<HttpResponse> {
    let url = format!("{}{}", service_url, path);
    
    info!("Proxying {} request to: {}", method, url);
    
    let response = match method {
        "GET" => client.get(&url).send().await,
        "POST" => {
            if let Some(json_body) = body {
                client.post(&url).json(&json_body).send().await
            } else {
                client.post(&url).send().await
            }
        },
        "PUT" => {
            if let Some(json_body) = body {
                client.put(&url).json(&json_body).send().await
            } else {
                client.put(&url).send().await
            }
        },
        "DELETE" => client.delete(&url).send().await,
        _ => return Ok(HttpResponse::MethodNotAllowed().finish()),
    };

    match response {
        Ok(resp) => {
            let status = resp.status();
            let json_response: Value = resp.json().await.unwrap_or(Value::Null);
            
            Ok(HttpResponse::build(status).json(json_response))
        }
        Err(e) => {
            error!("Proxy request failed: {}", e);
            Ok(HttpResponse::ServiceUnavailable().json(serde_json::json!({
                "error": "Service temporarily unavailable",
                "details": e.to_string()
            })))
        }
    }
}

// Health check endpoint
async fn health_check(data: web::Data<AppState>) -> Result<HttpResponse> {
    let mut statuses = Vec::new();
    
    // Check user service
    let user_status = check_service_health(&data.http_client, &data.config.user_service_url, "User Service").await;
    statuses.push(user_status);
    
    // Check chat service
    let chat_status = check_service_health(&data.http_client, &data.config.chat_service_url, "Chat Service").await;
    statuses.push(chat_status);
    
    // Check message service
    let message_status = check_service_health(&data.http_client, &data.config.message_service_url, "Message Service").await;
    statuses.push(message_status);
    
    let response = HealthResponse {
        status: "healthy".to_string(),
        version: "1.0.0".to_string(),
        services: statuses,
        timestamp: chrono::Utc::now().to_rfc3339(),
    };
    
    Ok(HttpResponse::Ok().json(response))
}

// Check individual service health
async fn check_service_health(client: &Client, url: &str, name: &str) -> ServiceStatus {
    let health_url = format!("{}/", url.trim_end_matches('/'));
    
    match client.get(&health_url).timeout(std::time::Duration::from_secs(5)).send().await {
        Ok(response) => {
            let status = if response.status().is_success() { "healthy" } else { "unhealthy" };
            ServiceStatus {
                name: name.to_string(),
                url: url.to_string(),
                status: status.to_string(),
                last_checked: chrono::Utc::now().to_rfc3339(),
            }
        }
        Err(_) => ServiceStatus {
            name: name.to_string(),
            url: url.to_string(),
            status: "unhealthy".to_string(),
            last_checked: chrono::Utc::now().to_rfc3339(),
        }
    }
}

// Root endpoint
async fn index() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "message": "Gateway Service Running",
        "version": "1.0.0",
        "description": "API Gateway for Chat Application Microservices",
        "endpoints": {
            "health": "/health",
            "auth": "/api/auth/*",
            "users": "/api/users/*",
            "chat": "/api/chat/*",
            "messages": "/api/messages/*"
        }
    })))
}

// Auth endpoints with validation
async fn validated_auth_handler(
    path: web::Path<(String,)>,
    payload: web::Json<Value>,
    data: web::Data<AppState>,
) -> Result<HttpResponse, ApiError> {
    let (endpoint,) = path.into_inner();
    
    // Extract the JSON value once
    let json_value = payload.into_inner();
    
    // Validate based on endpoint
    match endpoint.as_str() {
        "login" | "register" => {
            let auth_request: AuthRequest = serde_json::from_value(json_value.clone())
                .map_err(|_| ApiError::bad_request("Invalid request format"))?;
            
            validate_input(&auth_request)
                .map_err(|_| ApiError::bad_request("Validation failed"))?;
            
            info!("Validated auth request for endpoint: {}", endpoint);
        }
        _ => {
            // For other auth endpoints, basic validation
            info!("Processing auth request for endpoint: {}", endpoint);
        }
    }
    
    let service_path = format!("/{}", endpoint);
    
    // Convert Result<HttpResponse, ApiError> to Result<HttpResponse>
    match proxy_request(
        &data.http_client,
        &data.config.user_service_url,
        &service_path,
        "POST",
        Some(json_value)
    ).await {
        Ok(response) => Ok(response),
        Err(_) => Err(ApiError::service_unavailable("User service unavailable"))
    }
}

// User endpoints
async fn users_handler(
    req: HttpRequest,
    path: web::Path<(String,)>,
    payload: Option<web::Json<Value>>,
    data: web::Data<AppState>,
) -> Result<HttpResponse> {
    let (endpoint,) = path.into_inner();
    let service_path = format!("/{}", endpoint);
    let method = req.method().as_str();
    
    let body = payload.map(|p| p.into_inner());
    
    proxy_request(
        &data.http_client,
        &data.config.user_service_url,
        &service_path,
        method,
        body
    ).await
}

// Chat endpoints
async fn chat_handler(
    req: HttpRequest,
    path: web::Path<(String,)>,
    payload: Option<web::Json<Value>>,
    data: web::Data<AppState>,
) -> Result<HttpResponse> {
    let (endpoint,) = path.into_inner();
    let service_path = format!("/{}", endpoint);
    let method = req.method().as_str();
    
    let body = payload.map(|p| p.into_inner());
    
    proxy_request(
        &data.http_client,
        &data.config.chat_service_url,
        &service_path,
        method,
        body
    ).await
}

// Messages endpoints
async fn messages_handler(
    req: HttpRequest,
    path: web::Path<(String,)>,
    payload: Option<web::Json<Value>>,
    data: web::Data<AppState>,
) -> Result<HttpResponse> {
    let (endpoint,) = path.into_inner();
    let service_path = format!("/{}", endpoint);
    let method = req.method().as_str();
    
    let body = payload.map(|p| p.into_inner());
    
    proxy_request(
        &data.http_client,
        &data.config.message_service_url,
        &service_path,
        method,
        body
    ).await
}

// Authenticated chat endpoints (require JWT token)
async fn authenticated_chat_handler(
    req: HttpRequest,
    path: web::Path<(String,)>,
    payload: Option<web::Json<Value>>,
    data: web::Data<AppState>,
) -> Result<HttpResponse> {
    // Validate JWT token
    match AuthMiddleware::validate_token(&req) {
        Ok(claims) => {
            info!("Authenticated user: {} accessing chat endpoint", claims.username);
            
            let (endpoint,) = path.into_inner();
            let service_path = format!("/{}", endpoint);
            let method = req.method().as_str();
            
            let body = payload.map(|p| p.into_inner());
            
            proxy_request(
                &data.http_client,
                &data.config.chat_service_url,
                &service_path,
                method,
                body
            ).await
        }
        Err(error_response) => Ok(error_response)
    }
}

// Authenticated messages endpoints (require JWT token)
async fn authenticated_messages_handler(
    req: HttpRequest,
    path: web::Path<(String,)>,
    payload: Option<web::Json<Value>>,
    data: web::Data<AppState>,
) -> Result<HttpResponse> {
    // Validate JWT token
    match AuthMiddleware::validate_token(&req) {
        Ok(claims) => {
            info!("Authenticated user: {} accessing messages endpoint", claims.username);
            
            let (endpoint,) = path.into_inner();
            let service_path = format!("/{}", endpoint);
            let method = req.method().as_str();
            
            let body = payload.map(|p| p.into_inner());
            
            proxy_request(
                &data.http_client,
                &data.config.message_service_url,
                &service_path,
                method,
                body
            ).await
        }
        Err(error_response) => Ok(error_response)
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    setup_logging();
    
    // Load configuration from environment
    let config = Config {
        user_service_url: env::var("USER_SERVICE_URL").unwrap_or("http://user-service:3001".to_string()),
        chat_service_url: env::var("CHAT_SERVICE_URL").unwrap_or("http://chat-service:3002".to_string()),
        message_service_url: env::var("MESSAGE_SERVICE_URL").unwrap_or("http://message-service:3003".to_string()),
        port: env::var("PORT").unwrap_or("8000".to_string()).parse().unwrap_or(8000),
    };
    
    info!("Starting Gateway Service with config: {:?}", config);
    
    let http_client = Client::builder()
        .timeout(std::time::Duration::from_secs(30))
        .build()
        .expect("Failed to create HTTP client");
    
    let app_state = AppState {
        config: config.clone(),
        http_client,
        service_statuses: Arc::new(RwLock::new(HashMap::new())),
    };
    
    let app_state_data = web::Data::new(app_state);
    
    HttpServer::new(move || {
        App::new()
            .app_data(app_state_data.clone())
            .wrap(middleware::Logger::default())
            .route("/", web::get().to(index))
            .route("/health", web::get().to(health_check))
            // Auth routes (validated)
            .service(
                web::scope("/api/auth")
                    .route("/{endpoint}", web::post().to(validated_auth_handler))
            )
            // User routes
            .service(
                web::scope("/api/users")
                    .route("/{endpoint}", web::get().to(users_handler))
                    .route("/{endpoint}", web::post().to(users_handler))
                    .route("/{endpoint}", web::put().to(users_handler))
                    .route("/{endpoint}", web::delete().to(users_handler))
            )
            // Chat routes (authenticated)
            .service(
                web::scope("/api/chat")
                    .route("/{endpoint}", web::get().to(authenticated_chat_handler))
                    .route("/{endpoint}", web::post().to(authenticated_chat_handler))
                    .route("/{endpoint}", web::put().to(authenticated_chat_handler))
                    .route("/{endpoint}", web::delete().to(authenticated_chat_handler))
            )
            // Messages routes (authenticated)
            .service(
                web::scope("/api/messages")
                    .route("/{endpoint}", web::get().to(authenticated_messages_handler))
                    .route("/{endpoint}", web::post().to(authenticated_messages_handler))
                    .route("/{endpoint}", web::put().to(authenticated_messages_handler))
                    .route("/{endpoint}", web::delete().to(authenticated_messages_handler))
            )
    })
    .bind(("0.0.0.0", config.port))?
    .run()
    .await
}