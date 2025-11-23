# ---- Base Stage ----
# Use the official uv image (consistent with your other services)
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

# 1. Move Virtual Environment OUTSIDE /app
# This prevents docker-compose volumes (mounted at /app) from hiding dependencies.
ENV UV_PROJECT_ENVIRONMENT="/venv"
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

# ---- Builder Stage ----
FROM base as builder

# 2. Copy dependency files from service directory
# (Assumes build context is set to project root in docker-compose)
# Copy service-specific pyproject.toml (auth_service doesn't use shared module)
COPY ./services/auth_service/pyproject.toml ./

# 3. Install dependencies
# Note: auth_service may not have uv.lock, so we don't use --frozen
# uv will resolve and install dependencies from pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev

# ---- Final Stage ----
FROM base as final

# 4. Install Runtime Dependencies (Curl is needed for the healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    useradd --system --create-home --shell /bin/bash appuser

# 5. Copy the installed Virtual Environment
COPY --from=builder /venv /venv

# 6. Copy the specific Auth Service code
# Note: We copy from ./services/auth_service because we are running from Root Context
COPY ./services/auth_service /app

# If this service also needs the 'shared' folder, uncomment the next line:
# COPY ./shared /app/shared

# 7. Set ownership
# We chown /app so the user can write temp files if needed.
# We chown /venv so the user could theoretically update it (optional, but safe).
RUN chown -R appuser:appuser /app /venv

# 8. Switch User
USER appuser

# 9. Environment Config
# We inherit PATH="/venv/bin:$PATH" from the Base stage.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set PYTHONPATH so imports work correctly
ENV PYTHONPATH="/app"

# 10. Run
EXPOSE 8300

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8300/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8300"]