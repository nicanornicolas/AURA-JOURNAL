# ---- Base Stage ----
# Use the official uv image (consistent with your other services)
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim as base

# 1. Move Virtual Environment OUTSIDE /app
# This prevents docker-compose volumes (mounted at /app) from hiding dependencies.
ENV UV_PROJECT_ENVIRONMENT="/venv"
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

# ---- Builder Stage ----
FROM base as builder

# 2. Copy dependency files from Project Root
# (Assumes build context is set to project root in docker-compose)
COPY pyproject.toml uv.lock ./

# 3. Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ---- Final Stage ----
FROM base as final

# 4. Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 5. Copy the installed Virtual Environment
COPY --from=builder /venv /venv

# 6. Copy the specific Auth Service code
# Note: We copy from ./services/auth_service because we are running from Root Context
COPY ./services/auth_service /app

# If this service also needs the 'shared' folder, uncomment the next line:
# COPY ./shared /app/shared

# 7. Create and switch to non-root user
RUN useradd --system --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# 8. Configuration
# Set PYTHONPATH so imports work correctly (especially if you use shared folder later)
ENV PYTHONPATH="/app"
EXPOSE 8001

# 9. Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# 10. Run
# Direct usage of uvicorn is fine because /venv/bin is in PATH
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]