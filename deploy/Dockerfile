ARG PYTHON_VERSION=3.12
ARG BASE_IMAGE=python:${PYTHON_VERSION}-slim

# ---------- Builder stage ----------
FROM python:3.12-slim AS builder
LABEL stage="builder"

ENV PIP_NO_CACHE_DIR=1 \
	PIP_DISABLE_PIP_VERSION_CHECK=1 \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential curl \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Only copy dependency definition first for better layer caching
COPY pyproject.toml poetry.lock* ./

RUN pip install --upgrade pip "poetry==2.1.3" "poetry-plugin-export" \
	&& poetry --version \
	&& poetry export --format=requirements.txt --output requirements.txt --without-hashes \
	&& poetry export --with dev --format=requirements.txt --output requirements-dev.txt --without-hashes

# Install only runtime dependencies to /install
RUN pip install --prefix /install --no-cache-dir --upgrade --ignore-installed -r requirements.txt
# Install dev (test/tooling) dependencies to a separate prefix (optional layer for future test images)
RUN pip install --prefix /install-dev --no-cache-dir --upgrade --ignore-installed -r requirements-dev.txt

# Copy project metadata needed for build (README, license) and application source, then install
COPY README.md LICENSE ./
COPY src ./src
# Editable install for faster iterative rebuilds (code changes don't require reinstalling deps).
RUN pip install --prefix /install -e . --no-deps

# ---------- Runtime stage ----------
FROM python:3.12-slim AS runtime
LABEL authors="kamilrybacki"

ENV APP_HOME=/app \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR ${APP_HOME}

# Add non-root user
RUN useradd -u 10001 -m appuser

# Copy installed site-packages and application code
COPY --from=builder /install /usr/local
# (Dev dependencies kept out intentionally; can be copied from /install-dev if needed for debugging.)
# Copy source for introspection / debugging (optional)
COPY --from=builder /app/src ./src

# Expose the port the app runs on
EXPOSE 8000

USER root

# Lightweight curl for healthcheck
RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl \
	&& rm -rf /var/lib/apt/lists/*

COPY deploy/healthcheck.sh /app/healthcheck.sh
RUN chmod +x /app/healthcheck.sh

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 CMD curl -f http://127.0.0.1:8000/docs || exit 1

CMD ["python", "-m", "uvicorn", "mtgapi.entrypoint:API", "--host", "0.0.0.0", "--port", "8000"]
