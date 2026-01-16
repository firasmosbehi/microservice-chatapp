# Multi-stage build for optimized Rust binary
FROM rust:1.84 as builder

WORKDIR /app

# Copy manifest first to leverage Docker cache for dependencies
COPY Cargo.toml ./

# Create a dummy main.rs to build dependencies only
RUN mkdir src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Copy actual source code
COPY . .

# Build the application (should be much faster now due to cached dependencies)
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