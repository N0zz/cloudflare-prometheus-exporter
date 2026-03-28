# Stage 1: Builder
FROM python:3.13-slim-bookworm@sha256:20080e807bfc404f8450b185cf0fc95d553462673598549613735f70a5b4d5d0 AS builder

COPY --from=ghcr.io/astral-sh/uv@sha256:c4f5de312ee66d46810635ffc5df34a1973ba753e7241ce3a08ef979ddd7bea5 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


# Stage 2: Runtime
FROM python:3.13-slim-bookworm@sha256:20080e807bfc404f8450b185cf0fc95d553462673598549613735f70a5b4d5d0 AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY cloudflare_exporter/ ./cloudflare_exporter/

RUN useradd -m -r -u 1000 cloudflare && \
    chown -R cloudflare:cloudflare /app

USER cloudflare


CMD ["/app/.venv/bin/python", "-m", "cloudflare_exporter.main"]
