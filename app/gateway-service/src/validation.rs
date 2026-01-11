use serde::Deserialize;
use validator::Validate;

#[derive(Debug, Deserialize, Validate)]
pub struct AuthRequest {
    #[validate(length(min = 3, max = 50))]
    pub username: String,
    
    #[validate(length(min = 6))]
    pub password: String,
}

#[derive(Debug, Deserialize, Validate)]
pub struct CreateUserRequest {
    #[validate(length(min = 3, max = 50))]
    pub username: String,
    
    #[validate(email)]
    pub email: String,
    
    #[validate(length(min = 6))]
    pub password: String,
}

#[derive(Debug, Deserialize, Validate)]
pub struct CreateRoomRequest {
    #[validate(length(min = 1, max = 100))]
    pub name: String,
    
    #[validate(length(max = 500))]
    pub description: Option<String>,
    
    pub is_private: bool,
}

#[derive(Debug, Deserialize, Validate)]
pub struct SendMessageRequest {
    #[validate(length(min = 1, max = 1000))]
    pub content: String,
    
    pub room_id: u32,
    pub sender_id: u32,
}

pub fn validate_input<T: Validate>(input: &T) -> Result<(), validator::ValidationErrors> {
    input.validate()
}