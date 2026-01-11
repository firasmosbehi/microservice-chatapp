use actix_web::{HttpRequest, HttpResponse, Result};
use jsonwebtoken::{decode, DecodingKey, Validation, Algorithm};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String, // user ID
    pub username: String,
    pub exp: usize,
}

pub struct AuthMiddleware;

impl AuthMiddleware {
    pub fn validate_token(req: &HttpRequest) -> Result<Claims, HttpResponse> {
        // Get JWT secret from environment
        let jwt_secret = env::var("JWT_SECRET").unwrap_or_else(|_| "super-secret-gateway-key".to_string());
        
        // Extract token from Authorization header
        let auth_header = req.headers().get("Authorization");
        
        if auth_header.is_none() {
            return Err(HttpResponse::Unauthorized().json(serde_json::json!({
                "error": "Authorization header missing"
            })));
        }
        
        let auth_str = auth_header.unwrap().to_str().map_err(|_| {
            HttpResponse::BadRequest().json(serde_json::json!({
                "error": "Invalid authorization header format"
            }))
        })?;
        
        if !auth_str.starts_with("Bearer ") {
            return Err(HttpResponse::Unauthorized().json(serde_json::json!({
                "error": "Bearer token required"
            })));
        }
        
        let token = &auth_str[7..]; // Skip "Bearer "
        
        // Decode and validate token
        let decoding_key = DecodingKey::from_secret(jwt_secret.as_bytes());
        let validation = Validation::new(Algorithm::HS256);
        
        match decode::<Claims>(token, &decoding_key, &validation) {
            Ok(token_data) => Ok(token_data.claims),
            Err(_) => Err(HttpResponse::Unauthorized().json(serde_json::json!({
                "error": "Invalid or expired token"
            }))),
        }
    }
    
    pub fn extract_user_id(req: &HttpRequest) -> Option<i32> {
        match Self::validate_token(req) {
            Ok(claims) => claims.sub.parse::<i32>().ok(),
            Err(_) => None,
        }
    }
}