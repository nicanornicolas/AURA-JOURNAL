# ---- Base Stage ----
# Use a specific version of the official `uv` image as a base.
# This stage gives us Python and a pre-installed `uv`.
# Using a specific digest (`@sha256:...`) is best for reproducible builds, but `latest` is fine for development.
FROM ghcr.io/astral-sh/uv:0.5.5-python3.12-slim as base
# Or stick to 3.11 if your project requires it:
# FROM ghcr.io/astral-sh/uv:0.5.5-python3.11-slim as base

# Set the working directory
WORKDIR /opt/app


# ---- Builder Stage ----
# This stage builds the virtual environment with all dependencies.
FROM base as builder

# Copy only the dependency definition files.
# This leverages Docker's layer caching. The layer only rebuilds if these files change.
COPY pyproject.toml ./

# Create the virtual environment and install dependencies using uv sync.
# `uv sync` is the canonical way to install from a pyproject.toml or lock file.
# It's faster and more direct than `uv venv && uv pip install`.
RUN uv sync --system-site-packages

# ---- Final Stage ----
# This stage creates the final, lean production image.
FROM base as final

# 1. Install System Dependencies & Create a Non-Root User
# - Install only necessary runtime libraries (like for psycopg2).
# - Create a non-root user for security. Running containers as root is a major risk.
# - Clean up apt cache in the same layer to keep the image small.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --system --create-home --shell /bin/bash appuser

# 2. Copy Artifacts from the Builder Stage
# Copy the entire virtual environment created by the builder.
COPY --from=builder /opt/app/.venv ./.venv

# 3. Copy Application Code
# Copy your application source code into the container.
COPY ./app ./app

# This `PYTHONPATH` line suggests you might have shared modules.
# Ensure your COPY commands above match this structure if needed.
# For example, if you have a `shared` folder at the root: `COPY ./shared ./shared`
ENV PYTHONPATH="/opt/app:$PYTHONPATH"

# 4. Set Ownership and User
# Change the ownership of all application files to the non-root user.
RUN chown -R appuser:appuser /opt/app
# Switch to the non-root user. From this point on, all commands run as `appuser`.
USER appuser

# 5. Configure the Environment
# Set the PATH to include the virtual environment's binaries.
ENV PATH="/opt/app/.venv/bin:$PATH"
# Let Python know not to write .pyc files.
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to the terminal without buffering.
ENV PYTHONUNBUFFERED 1

# 6. Expose Port and Define Healthcheck
# Expose the port the application will run on.
EXPOSE 8000

# The healthcheck is great practice! It requires `requests` to be in pyproject.toml.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 7. Run the Application
# Use the uvicorn executable from the virtual environment.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]