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

# Install dependencies directly with Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Production stage
FROM python:3.13-slim

WORKDIR /app

# Copy application code
COPY . .

# Expose port
EXPOSE 3002

# Run the application
CMD ["python", "-m", "uvicorn", "chat_app.app:app", "--host", "0.0.0.0", "--port", "3002"]