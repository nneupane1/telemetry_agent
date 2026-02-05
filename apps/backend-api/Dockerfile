# ------------------------------------------------------------
# GenAI Predictive Interpreter Backend
# Production-grade Dockerfile
# ------------------------------------------------------------

FROM python:3.11-slim AS runtime

# ------------------------------------------------------------
# System hardening & base setup
# ------------------------------------------------------------

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install minimal OS dependencies (no bloat)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Python dependencies
# ------------------------------------------------------------

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ------------------------------------------------------------
# Application code
# ------------------------------------------------------------

COPY app ./app

# ------------------------------------------------------------
# Runtime configuration
# ------------------------------------------------------------

EXPOSE 8000

# Do NOT use --reload in containers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
