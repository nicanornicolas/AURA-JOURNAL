# Wellness Engine image. Build from backend/:
#   docker build -f services/wellness_engine/Dockerfile -t wellness-engine .
# Lexicon-only (tiny, no model downloads):
#   docker build --build-arg EARS_EXTRAS=none ...
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ARG EARS_EXTRAS=hf
ENV UV_SYSTEM_PYTHON=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HF_HOME=/models

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --create-home appuser

WORKDIR /app
COPY ./shared /app/shared
COPY ./services/wellness_engine/pyproject.toml /app/services/wellness_engine/pyproject.toml

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install fastapi "uvicorn[standard]" pydantic pydantic-settings pyyaml loguru \
        sqlalchemy psycopg2-binary \
    && if [ "$EARS_EXTRAS" = "hf" ]; then \
        uv pip install torch --index-url https://download.pytorch.org/whl/cpu \
        && uv pip install "transformers>=4.46,<5" sentencepiece sacremoses ; \
    fi

COPY ./services/wellness_engine/app /app/services/wellness_engine/app
RUN mkdir -p /models && chown -R appuser:appuser /app /models
USER appuser

EXPOSE 8300
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8300/health || exit 1

# One worker: the models are loaded once and shared (RAM matters on the homelab).
CMD ["uvicorn", "services.wellness_engine.app.main:app", "--host", "0.0.0.0", "--port", "8300", "--workers", "1"]
