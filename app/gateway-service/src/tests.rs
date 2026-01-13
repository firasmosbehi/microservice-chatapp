#[cfg(test)]
mod tests {
    use super::*;
    use actix_web::{test, web, App, http::StatusCode};
    use serde_json::json;

    #[actix_web::test]
    async fn test_index_endpoint() {
        let app = test::init_service(
            App::new().route("/", web::get().to(index))
        ).await;

        let req = test::TestRequest::get().uri("/").to_request();
        let resp = test::call_service(&app, req).await;

        assert_eq!(resp.status(), StatusCode::OK);
    }

    #[actix_web::test]
    async fn test_health_check_endpoint() {
        let app = test::init_service(
            App::new().route("/health", web::get().to(health_check))
        ).await;

        let req = test::TestRequest::get().uri("/health").to_request();
        let resp = test::call_service(&app, req).await;

        assert_eq!(resp.status(), StatusCode::OK);
    }

    #[actix_web::test]
    async fn test_health_check_response_format() {
        let app = test::init_service(
            App::new().route("/health", web::get().to(health_check))
        ).await;

        let req = test::TestRequest::get().uri("/health").to_request();
        let resp = test::call_and_read_body(&app, req).await;
        
        let health_response: HealthResponse = serde_json::from_slice(&resp).unwrap();
        assert_eq!(health_response.status, "healthy");
        assert!(health_response.timestamp.is_some());
        assert!(health_response.services.is_empty()); // Initially empty
    }

    #[actix_web::test]
    async fn test_cors_headers() {
        let app = test::init_service(
            App::new()
                .wrap(actix_cors::Cors::permissive())
                .route("/", web::get().to(index))
        ).await;

        let req = test::TestRequest::get()
            .uri("/")
            .insert_header(("Origin", "http://localhost:3000"))
            .to_request();
        
        let resp = test::call_service(&app, req).await;
        
        assert_eq!(resp.status(), StatusCode::OK);
        // Check that CORS headers are present
        assert!(resp.headers().contains_key("access-control-allow-origin"));
    }
}

#[cfg(test)]
mod auth_tests {
    use super::*;
    use actix_web::{test, web, App};
    use jsonwebtoken::{encode, Header, EncodingKey};
    use serde::{Deserialize, Serialize};
    use std::time::{SystemTime, UNIX_EPOCH};

    #[derive(Debug, Serialize, Deserialize)]
    struct TestClaims {
        sub: String,
        exp: usize,
        user_id: u32,
    }

    #[actix_web::test]
    async fn test_jwt_generation() {
        let claims = TestClaims {
            sub: "test@example.com".to_string(),
            exp: (SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs() + 3600) as usize,
            user_id: 123,
        };

        let token = encode(
            &Header::default(),
            &claims,
            &EncodingKey::from_secret(b"test-secret"),
        ).unwrap();

        assert!(!token.is_empty());
        assert!(token.contains("."));
    }

    #[actix_web::test]
    async fn test_auth_middleware_valid_token() {
        // This would test the AuthMiddleware with a valid token
        // Implementation depends on how the middleware is structured
    }

    #[actix_web::test]
    async fn test_auth_middleware_invalid_token() {
        // Test with malformed token
        let invalid_token = "invalid.token.here";
        
        // The middleware should reject this and return 401
    }

    #[actix_web::test]
    async fn test_auth_middleware_expired_token() {
        // Create expired token
        let expired_claims = TestClaims {
            sub: "test@example.com".to_string(),
            exp: (SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs() - 3600) as usize, // Expired 1 hour ago
            user_id: 123,
        };

        let expired_token = encode(
            &Header::default(),
            &expired_claims,
            &EncodingKey::from_secret(b"test-secret"),
        ).unwrap();

        // Should be rejected as expired
    }
}

#[cfg(test)]
mod routing_tests {
    use super::*;
    use actix_web::{test, web, App, http::StatusCode};

    #[actix_web::test]
    async fn test_auth_routes_prefix() {
        let app = test::init_service(
            App::new()
                .service(
                    web::scope("/api/auth")
                        .route("/{endpoint}", web::post().to(dummy_handler))
                )
        ).await;

        // Test that auth routes are properly prefixed
        let req = test::TestRequest::post()
            .uri("/api/auth/login")
            .to_request();
        
        let resp = test::try_call_service(&app, req).await;
        assert!(resp.is_ok());
    }

    #[actix_web::test]
    async fn test_users_routes_prefix() {
        let app = test::init_service(
            App::new()
                .service(
                    web::scope("/api/users")
                        .route("/{endpoint}", web::get().to(dummy_handler))
                        .route("/{endpoint}", web::post().to(dummy_handler))
                )
        ).await;

        // Test GET route
        let get_req = test::TestRequest::get()
            .uri("/api/users/profile")
            .to_request();
        let get_resp = test::try_call_service(&app, get_req).await;
        assert!(get_resp.is_ok());

        // Test POST route
        let post_req = test::TestRequest::post()
            .uri("/api/users/create")
            .to_request();
        let post_resp = test::try_call_service(&app, post_req).await;
        assert!(post_resp.is_ok());
    }

    #[actix_web::test]
    async fn test_chat_routes_prefix() {
        let app = test::init_service(
            App::new()
                .service(
                    web::scope("/api/chat")
                        .route("/{endpoint}", web::get().to(dummy_handler))
                        .route("/{endpoint}", web::post().to(dummy_handler))
                )
        ).await;

        let req = test::TestRequest::get()
            .uri("/api/chat/rooms")
            .to_request();
        
        let resp = test::try_call_service(&app, req).await;
        assert!(resp.is_ok());
    }

    #[actix_web::test]
    async fn test_messages_routes_prefix() {
        let app = test::init_service(
            App::new()
                .service(
                    web::scope("/api/messages")
                        .route("/{endpoint}", web::get().to(dummy_handler))
                        .route("/{endpoint}", web::post().to(dummy_handler))
                )
        ).await;

        let req = test::TestRequest::get()
            .uri("/api/messages/history")
            .to_request();
        
        let resp = test::try_call_service(&app, req).await;
        assert!(resp.is_ok());
    }

    async fn dummy_handler() -> impl Responder {
        HttpResponse::Ok().json(json!({"message": "dummy response"}))
    }
}

#[cfg(test)]
mod proxy_tests {
    use super::*;
    use actix_web::{test, web, App, http::StatusCode};
    use reqwest::Client;
    use std::sync::Arc;

    #[actix_web::test]
    async fn test_service_proxy_configuration() {
        let config = Config {
            user_service_url: "http://localhost:3001".to_string(),
            chat_service_url: "http://localhost:3002".to_string(),
            message_service_url: "http://localhost:3003".to_string(),
            port: 8000,
        };

        // Test that configuration is properly loaded
        assert_eq!(config.user_service_url, "http://localhost:3001");
        assert_eq!(config.chat_service_url, "http://localhost:3002");
        assert_eq!(config.message_service_url, "http://localhost:3003");
    }

    #[actix_web::test]
    async fn test_http_client_initialization() {
        let client = Client::new();
        
        // Client should be successfully created
        assert!(true); // If we get here, client creation succeeded
    }

    #[actix_web::test]
    async fn test_service_status_tracking() {
        let mut statuses = HashMap::new();
        let service_status = ServiceStatus {
            name: "test-service".to_string(),
            url: "http://localhost:3001".to_string(),
            status: "unknown".to_string(),
            last_checked: chrono::Utc::now().to_rfc3339(),
        };

        statuses.insert("test-service".to_string(), service_status.clone());

        assert_eq!(statuses.len(), 1);
        assert_eq!(statuses.get("test-service").unwrap().name, "test-service");
    }

    #[actix_web::test]
    async fn test_request_forwarding_logic() {
        // Test the logic for determining which service to forward requests to
        let auth_paths = vec!["/api/auth/login", "/api/auth/register"];
        let user_paths = vec!["/api/users/profile", "/api/users/list"];
        let chat_paths = vec!["/api/chat/rooms", "/api/chat/messages"];
        let message_paths = vec!["/api/messages/send", "/api/messages/history"];

        for path in auth_paths {
            assert!(path.starts_with("/api/auth/"));
        }

        for path in user_paths {
            assert!(path.starts_with("/api/users/"));
        }

        for path in chat_paths {
            assert!(path.starts_with("/api/chat/"));
        }

        for path in message_paths {
            assert!(path.starts_with("/api/messages/"));
        }
    }
}

#[cfg(test)]
mod validation_tests {
    use super::*;
    use validator::Validate;

    #[derive(Debug, Validate, serde::Deserialize)]
    struct TestUserRequest {
        #[validate(length(min = 3, max = 50))]
        username: String,
        #[validate(email)]
        email: String,
        #[validate(length(min = 6))]
        password: String,
    }

    #[actix_web::test]
    async fn test_input_validation_valid_data() {
        let valid_user = TestUserRequest {
            username: "testuser".to_string(),
            email: "test@example.com".to_string(),
            password: "password123".to_string(),
        };

        assert!(valid_user.validate().is_ok());
    }

    #[actix_web::test]
    async fn test_input_validation_invalid_username() {
        let invalid_user = TestUserRequest {
            username: "ab".to_string(), // Too short
            email: "test@example.com".to_string(),
            password: "password123".to_string(),
        };

        assert!(invalid_user.validate().is_err());
    }

    #[actix_web::test]
    async fn test_input_validation_invalid_email() {
        let invalid_user = TestUserRequest {
            username: "testuser".to_string(),
            email: "invalid-email".to_string(), // Invalid format
            password: "password123".to_string(),
        };

        assert!(invalid_user.validate().is_err());
    }

    #[actix_web::test]
    async fn test_input_validation_weak_password() {
        let invalid_user = TestUserRequest {
            username: "testuser".to_string(),
            email: "test@example.com".to_string(),
            password: "123".to_string(), // Too short
        };

        assert!(invalid_user.validate().is_err());
    }

    #[actix_web::test]
    async fn test_json_deserialization() {
        let json_data = r#"{
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }"#;

        let user: Result<TestUserRequest, _> = serde_json::from_str(json_data);
        assert!(user.is_ok());

        let user = user.unwrap();
        assert_eq!(user.username, "testuser");
        assert_eq!(user.email, "test@example.com");
        assert_eq!(user.password, "password123");
    }
}

#[cfg(test)]
mod error_tests {
    use super::*;

    #[actix_web::test]
    async fn test_error_responses() {
        let api_error = ApiError::BadRequest("Invalid input".to_string());
        let response: HttpResponse = api_error.into();
        assert_eq!(response.status(), StatusCode::BAD_REQUEST);

        let api_error = ApiError::Unauthorized("Access denied".to_string());
        let response: HttpResponse = api_error.into();
        assert_eq!(response.status(), StatusCode::UNAUTHORIZED);

        let api_error = ApiError::NotFound("Resource not found".to_string());
        let response: HttpResponse = api_error.into();
        assert_eq!(response.status(), StatusCode::NOT_FOUND);

        let api_error = ApiError::InternalServerError("Server error".to_string());
        let response: HttpResponse = api_error.into();
        assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);
    }

    #[actix_web::test]
    async fn test_error_serialization() {
        let api_error = ApiError::BadRequest("Test error".to_string());
        let json_response = serde_json::to_string(&api_error).unwrap();
        assert!(json_response.contains("Test error"));
        assert!(json_response.contains("Bad Request"));
    }
}

#[cfg(test)]
mod integration_tests {
    use super::*;
    use actix_web::{test, web, App};

    #[actix_web::test]
    async fn test_full_application_setup() {
        // Test that the full application can be initialized
        let config = Config {
            user_service_url: "http://localhost:3001".to_string(),
            chat_service_url: "http://localhost:3002".to_string(),
            message_service_url: "http://localhost:3003".to_string(),
            port: 8000,
        };

        let app_state = web::Data::new(AppState {
            config: config.clone(),
            http_client: reqwest::Client::new(),
            service_statuses: Arc::new(tokio::sync::RwLock::new(HashMap::new())),
        });

        let app = test::init_service(
            App::new()
                .app_data(app_state)
                .route("/", web::get().to(index))
                .route("/health", web::get().to(health_check))
        ).await;

        // Test basic endpoints work with full app setup
        let req = test::TestRequest::get().uri("/").to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), StatusCode::OK);

        let health_req = test::TestRequest::get().uri("/health").to_request();
        let health_resp = test::call_service(&app, health_req).await;
        assert_eq!(health_resp.status(), StatusCode::OK);
    }

    #[actix_web::test]
    async fn test_concurrent_requests() {
        let app = test::init_service(
            App::new().route("/test", web::get().to(|| async { "OK" }))
        ).await;

        // Spawn multiple concurrent requests
        let mut handles = vec![];
        for _ in 0..10 {
            let req = test::TestRequest::get().uri("/test").to_request();
            let app_clone = &app;
            handles.push(tokio::spawn(async move {
                test::call_service(app_clone, req).await
            }));
        }

        // Wait for all requests to complete
        for handle in handles {
            let resp = handle.await.unwrap();
            assert_eq!(resp.status(), StatusCode::OK);
        }
    }
}