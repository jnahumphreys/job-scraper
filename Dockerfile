# Build stage - using full Python image which includes build tools
FROM python:3.13-bookworm AS builder

WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .

# Install pip, setuptools, wheel with cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel

# Install Python packages with cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade -r requirements.txt --prefer-binary

# Runtime stage
FROM python:3.13-slim-bookworm AS runtime

# Install runtime dependencies that might be needed for Python extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create non-root user early
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and set ownership in one layer
COPY --chown=appuser:appuser app/ ./app/

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]