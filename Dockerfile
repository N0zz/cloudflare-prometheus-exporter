# Stage 1: Builder
FROM python:3.13-slim-bookworm AS builder

ENV PIPENV_VENV_IN_PROJECT=1

WORKDIR /app

COPY Pipfile ./
RUN pip install --no-cache-dir pipenv && \
    pipenv install --deploy --ignore-pipfile


# Stage 2: Runtime
FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY cloudflare_exporter/ ./cloudflare_exporter/

RUN useradd -m -r -u 1000 cloudflare && \
    chown -R cloudflare:cloudflare /app

USER cloudflare

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${CF_LISTEN_PORT:-8080}/metrics || exit 1

CMD ["/app/.venv/bin/python", "-m", "cloudflare_exporter.main"]
