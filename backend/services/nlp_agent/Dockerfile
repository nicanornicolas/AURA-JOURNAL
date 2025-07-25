# Stage 1: Builder stage with uv for fast dependency installation
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /opt/app

# Install uv for fast package management
RUN pip install uv

# Copy dependency files first for better caching
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv && uv pip install --no-cache .

# ---

# Stage 2: Final runtime stage
FROM python:3.11-slim

# Set working directory
WORKDIR /opt/app

# Install system dependencies for Google Cloud services
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from builder stage
COPY --from=builder /opt/app/.venv ./.venv

# Copy application code
COPY ./app ./app

# Add the backend directory to Python path for shared module access
ENV PYTHONPATH="/opt/backend:$PYTHONPATH"

# Set PATH to use the virtual environment
ENV PATH="/opt/app/.venv/bin:$PATH"

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
