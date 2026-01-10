use actix_web::{web, App, HttpServer, HttpResponse, Result};

async fn health_check() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "message": "Gateway Service Running"
    })))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("Starting Gateway Service on port 8000");
    
    HttpServer::new(|| {
        App::new()
            .route("/", web::get().to(health_check))
    })
    .bind("127.0.0.1:8000")?
    .run()
    .await
}