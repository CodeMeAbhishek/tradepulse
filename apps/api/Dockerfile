# TradePulse API — build from repo root:
#   docker build -f apps/api/Dockerfile -t tradepulse-api .
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Shared contracts package first
COPY packages/contracts /tmp/contracts
RUN pip install /tmp/contracts && rm -rf /tmp/contracts

COPY apps/api/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt \
    && pip uninstall -y pytest ruff mypy || true

COPY apps/api /app
# Jury sample library (SYNTHETIC_DEMO packs) — Canva-style cloud picker source
COPY data/fixtures/synthetic-trade-docs /app/demo_samples

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${PORT}/healthz" || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
