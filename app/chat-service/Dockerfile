# Multi-stage build for optimized image
FROM python:3.13-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY poetry.lock pyproject.toml ./

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry export -f requirements.txt --without-hashes --only main > requirements.txt
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.13-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Expose port
EXPOSE 3002

# Run the application
CMD ["python", "-m", "uvicorn", "chat_app.app:app", "--host", "0.0.0.0", "--port", "3002"]