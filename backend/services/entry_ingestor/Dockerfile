# ---- Base Stage ----
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

# 1. Define the environment location OUTSIDE of /app
# This ensures docker-compose volumes (mounted at /app) don't hide your installed packages.
ENV UV_PROJECT_ENVIRONMENT="/venv"
ENV PATH="/venv/bin:$PATH"

# 2. Set working directory
WORKDIR /app

# ---- Builder Stage ----
FROM base as builder

# 3. Install system-level dependencies required by Python packages (e.g., for psycopg2).
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 4. Copy dependency definitions
# (Assumes build context is the project root, per your docker-compose)
# Create directory structure to match path references in pyproject.toml
# The pyproject.toml references ../../shared, so we need services/entry_ingestor/ structure
RUN mkdir -p /app/services/entry_ingestor
# Copy service-specific pyproject.toml and uv.lock (contains loguru and other deps)
COPY ./services/entry_ingestor/pyproject.toml ./services/entry_ingestor/uv.lock /app/services/entry_ingestor/
# Copy shared directory for the aura-journal-shared dependency (at /app/shared to match ../../shared path)
COPY ./shared /app/shared

# 5. Install dependencies from the service directory
# We use --no-install-project because we just want the libs in /venv
WORKDIR /app/services/entry_ingestor
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev
WORKDIR /app

# ---- Final Stage ----
FROM base as final

# 6. Install Runtime Dependencies (Curl is needed for the healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 ca-certificates curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    useradd --system --create-home --shell /bin/bash appuser

# 7. Copy the installed Virtual Environment from builder
COPY --from=builder /venv /venv

# 8. Copy Application Code
# FIX: You must copy the code into the image, even if using volumes for dev.
# Adjust these source paths if your Dockerfile location changes.
# These paths assume 'docker build' is run from the PROJECT ROOT.
COPY ./services/entry_ingestor/app /app/app
COPY ./shared /app/shared

# 9. Set ownership
# We chown /app so the user can write temp files if needed.
# We chown /venv so the user could theoretically update it (optional, but safe).
RUN chown -R appuser:appuser /app /venv

# 10. Switch User
USER appuser

# 11. Environment Config
# We inherit PATH="/venv/bin:$PATH" from the Base stage.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Ensure Python finds the shared module and app module
ENV PYTHONPATH="/app"

# 12. Run
EXPOSE 8100

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8100/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
