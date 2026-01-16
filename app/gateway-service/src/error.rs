use actix_web::{HttpResponse, ResponseError, http::StatusCode};
use serde::Serialize;
use std::fmt;

#[derive(Debug, Serialize)]
pub struct ApiError {
    pub error: String,
    pub message: String,
    pub status_code: u16,
}

impl fmt::Display for ApiError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.error, self.message)
    }
}

impl ResponseError for ApiError {
    fn error_response(&self) -> HttpResponse {
        let status = StatusCode::from_u16(self.status_code).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR);
        HttpResponse::build(status)
            .json(serde_json::json!({
                "error": self.error,
                "message": self.message,
                "status_code": self.status_code
            }))
    }
}

impl ApiError {
    pub fn unauthorized(message: &str) -> Self {
        ApiError {
            error: "Unauthorized".to_string(),
            message: message.to_string(),
            status_code: 401,
        }
    }
    
    pub fn bad_request(message: &str) -> Self {
        ApiError {
            error: "Bad Request".to_string(),
            message: message.to_string(),
            status_code: 400,
        }
    }
    
    pub fn not_found(message: &str) -> Self {
        ApiError {
            error: "Not Found".to_string(),
            message: message.to_string(),
            status_code: 404,
        }
    }
    
    pub fn internal_error(message: &str) -> Self {
        ApiError {
            error: "Internal Server Error".to_string(),
            message: message.to_string(),
            status_code: 500,
        }
    }
    
    pub fn service_unavailable(message: &str) -> Self {
        ApiError {
            error: "Service Unavailable".to_string(),
            message: message.to_string(),
            status_code: 503,
        }
    }
}