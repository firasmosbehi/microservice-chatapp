FROM rust:1.74 as builder
WORKDIR /app
COPY . .
RUN cargo build --release
FROM debian:bookworm-slim
COPY --from=builder /app/target/release/gateway-service /usr/local/bin/gateway-service
EXPOSE 8000
CMD ["gateway-service"]