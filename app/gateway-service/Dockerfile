# Multi-stage build for optimized Rust binary
FROM rust:1.75 as builder

WORKDIR /app

# Copy all source files
COPY . .

# Build the application
RUN cargo build --release

# Production stage
FROM debian:bookworm-slim

# Install ca-certificates for HTTPS requests
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the compiled binary from builder stage
COPY --from=builder /app/target/release/gateway-service .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["./gateway-service"]