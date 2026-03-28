
# Default: list available recipes
default:
    @just --list

# Run all unit tests with coverage
test:
    uv run pytest tests/ --cov=cloudflare_exporter --cov-report=term-missing

# Run unit tests only
unit-test:
    uv run pytest tests/unit/ --cov=cloudflare_exporter --cov-report=term-missing

# Run unit tests with XML coverage report (for CI)
unit-test-report:
    uv run pytest tests/unit/ --cov=cloudflare_exporter --cov-report=xml

# Run integration tests (requires valid Cloudflare token)
integration-test:
    uv run pytest tests/integration/ --cov=cloudflare_exporter --cov-report=term-missing

# Run linting
lint:
    uv run ruff check .

# Format code
format:
    uv run ruff format .

# Check code formatting
format-check:
    uv run ruff format . --check

# Run type checking
typecheck:
    uv run pyright

# Run security checks
security-check:
    uv run bandit -r ./cloudflare_exporter

# Run Trivy vulnerability scan on repo (install: brew install trivy)
trivy-scan:
    trivy fs --severity CRITICAL,HIGH --ignore-unfixed .

# Run Trivy vulnerability scan on Docker image
trivy-image: build-docker-image
    trivy image --severity CRITICAL,HIGH --ignore-unfixed cloudflare-prometheus-exporter:latest

# Validate Helm chart templates
helm-template:
    helm template test helm/cloudflare-prometheus-exporter > /tmp/helm-output.yaml
    yq eval '.' /tmp/helm-output.yaml > /dev/null
    yq eval '.kind + "/" + .metadata.name' /tmp/helm-output.yaml

# Build Helm chart
build-helm-chart:
    helm package helm/cloudflare-prometheus-exporter

# Build Docker image
build-docker-image:
    docker buildx build --platform linux/amd64,linux/arm64 -t cloudflare-prometheus-exporter:latest .
