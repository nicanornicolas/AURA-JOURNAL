# ---- Base Stage ----
# Use the new official standard base image for uv + Python.
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim as base

# Set the working directory for all subsequent stages.
WORKDIR /app


# ---- Builder Stage ----
# This stage securely builds the application and all dependencies.
FROM base as builder

# 1. Install any build-time system dependencies if needed (none for this service).

# 2. Install Python dependencies into a virtual environment.
# This uses BuildKit's advanced mounting to keep layers clean and leverage caching.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-install-project --no-dev

# 3. Copy all project code into the builder.
COPY . .

# 4. Install the project code itself into the virtual environment.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


# ---- Final Stage ----
# This stage creates the final, lean, and secure production image.
FROM base as final

# 1. Install RUNTIME system dependencies and create a non-root user.
# ca-certificates is often needed for making secure HTTPS requests to external APIs.
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    useradd --system --create-home --shell /bin/bash appuser

# 2. Copy the fully built application (code + .venv) from the builder stage.
COPY --from=builder /app /app

# 3. Set ownership and switch to the non-root user for security.
RUN chown -R appuser:appuser /app
USER appuser

# 4. Configure the runtime environment.
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 5. Expose port, define healthcheck, and run the application.
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]