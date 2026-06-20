# Stage 1: Builder
FROM python:3.14-slim-bookworm@sha256:a70519002c49552ea0a853de47599cf40479b001bd7a624f1112eaf44dcaccc7 AS builder

COPY --from=ghcr.io/astral-sh/uv@sha256:d0a0a753ab981624b49c97abc98821c1c09f4ca69d1ef5cee69c501be3d88479 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


# Stage 2: Runtime
FROM python:3.14-slim-bookworm@sha256:a70519002c49552ea0a853de47599cf40479b001bd7a624f1112eaf44dcaccc7 AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY cloudflare_exporter/ ./cloudflare_exporter/

RUN useradd -m -r -u 1000 cloudflare && \
    chown -R cloudflare:cloudflare /app

USER cloudflare


CMD ["/app/.venv/bin/python", "-m", "cloudflare_exporter.main"]
