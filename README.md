# Cloudflare Prometheus Exporter

A Prometheus exporter for Cloudflare Analytics metrics, providing real-time HTTP and DNS analytics data from your Cloudflare zones.

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com/)
[![Release](https://github.com/n0zz/cloudflare-prometheus-exporter/actions/workflows/release.yml/badge.svg)](https://github.com/n0zz/cloudflare-prometheus-exporter/actions/workflows/release.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/nulltix/cloudflare-prometheus-exporter)](https://hub.docker.com/r/nulltix/cloudflare-prometheus-exporter)
[![Security: CodeQL](https://github.com/n0zz/cloudflare-prometheus-exporter/actions/workflows/codeql.yml/badge.svg)](https://github.com/n0zz/cloudflare-prometheus-exporter/actions/workflows/codeql.yml)
[![Security: Trivy](https://github.com/n0zz/cloudflare-prometheus-exporter/actions/workflows/security.yml/badge.svg)](https://github.com/n0zz/cloudflare-prometheus-exporter/actions/workflows/security.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/n0zz/cloudflare-prometheus-exporter/badge)](https://api.securityscorecards.dev/projects/github.com/n0zz/cloudflare-prometheus-exporter)

## Features

- **Multi-Zone Support**: Monitor multiple Cloudflare zones.
- **Thread-Safe Metric Collection**: Ensures safe data handling in multi-threaded environments.
- **Structured JSON Logging**: Provides logs in a structured format for easier analysis.
- **Configurable via Environment Variables**: Flexible configuration options for deployment.
- **Prometheus Metrics Exposure**: Exposes HTTP, firewall, and quota metrics for monitoring.
- **Error Handling**: Robust handling of API errors during metrics collection.
- **Health Checks**: Monitors the status of the metrics server.

## Data Sampling

> [!IMPORTANT]  
> Due to Cloudflare data sampling on Analytics GraphQL API, numbers reported by exporter are not exact, but rather close approximation.
> You could still rely on this data with high degree of confidence, but your dashboards and alerts should rely more on ratios and percentages, rather than on exact numbers (e.g. cache hit/miss ratio, [45]xx errors ratio).
>
> Read more here: https://developers.cloudflare.com/analytics/graphql-api/sampling/

## Configuration

Configuration is handled via environment variables or `.env` file:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CF_API_TOKEN` | Yes | - | Cloudflare API token |
| `CF_LISTEN_PORT` | No | `8080` | Port to expose Prometheus metrics on (range: 1024-65535) |
| `CF_LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CF_MAX_WORKERS` | No | `5` | Maximum number of concurrent worker threads (range: 3-10) |
| `CF_API_URL` | No | `https://api.cloudflare.com/client/v4/graphql` | Cloudflare GraphQL API endpoint |
| `CF_CMB_REGION` | No | `global` | Region for CMB compliance ('global', 'eu', or 'us') |
| `CF_SCRAPE_DELAY` | No | `60` | Scrape interval in seconds (60-300, must be multiple of 60) |
| `CF_ZONES` | No | - | Comma-separated list of zone IDs to monitor |
| `CF_EXCLUDE_ZONES` | No | - | Comma-separated list of zone IDs to exclude |
| `CF_EXCLUDE_DATASETS` | No | - | Comma-separated list of datasets to exclude |

> [!NOTE]
> Zone IDs can be found in the [Cloudflare dashboard Overview page](https://developers.cloudflare.com/fundamentals/setup/find-account-and-zone-ids/) under the API section. They are 32-character hexadecimal strings.

### Cloudflare Metadata Boundary (CMB) Compliance

This exporter supports Cloudflare's data residency requirements through CMB regions. For a complete list of available datasets and their regional availability, see [Cloudflare CMB GraphQL Datasets documentation](https://developers.cloudflare.com/data-localization/metadata-boundary/graphql-datasets/).

Choose the appropriate `CF_CMB_REGION` based on your compliance requirements.

### Required Permissions

The Cloudflare API token needs the following permissions:

Account:

- Analytics:Read
- Account Settings:Read
- Billing:Read

Zone:

- Analytics:Read
- Firewall Services:Read

## Supported Metrics

**Generic Labels for All Metrics:**

- `zone` - Cloudflare zone name
- `account` - Cloudflare account name
- `account_id` - Cloudflare account ID

| Metric Name                                   | Custom Labels Set                                                                                     | Description                                                                 |
|-----------------------------------------------|-------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| `cloudflare_requests_total`                   | `country`, `status`                                                                                  | Total number of HTTP requests made to the Cloudflare service.              |
| `cloudflare_bytes_total`                      | `country`, `status`                                                                                  | Total amount of data (in bytes) transferred through the Cloudflare service. |
| `cloudflare_cached_requests_total`            | `country`, `status`                                                                                  | Total number of HTTP requests that were served from the cache.              |
| `cloudflare_cached_bytes_total`               | `country`, `status`                                                                                  | Total amount of data (in bytes) transferred from the cache.                |
| `cloudflare_firewall_events_total`            | `action`, `rule_id`, `source`                                                                         | Total number of events triggered by the firewall rules.                     |
| `cloudflare_enterprise_zone_quota_max`       | `None`                                                                                               | Maximum quota allowed for the enterprise zone.                              |
| `cloudflare_enterprise_zone_quota_current`    | `None`                                                                                               | Current usage of the enterprise zone quota.                                 |
| `cloudflare_enterprise_zone_quota_available`  | `None`                                                                                               | Remaining quota available for use in the enterprise zone.                   |

## Usage

```bash
# Start the exporter
pipenv run python cloudflare_exporter/main.py
```

The exporter will start serving metrics on `http://localhost:8080/metrics` (or configured port).

### Docker

```bash
# Build the image
docker buildx build --platform linux/amd64,linux/arm64 -t cloudflare-exporter:latest .

# Run the container
docker run -p 8080:8080 --env-file .env cloudflare-exporter
```

## Helm Chart

The Cloudflare Prometheus Exporter Helm chart is available for download from our GitHub Pages repository:

- [Download Helm Chart](https://n0zz.github.io/cloudflare-prometheus-exporter/charts/index.yaml)

You can install the chart using the following command:

```bash
helm repo add cloudflare-exporter https://n0zz.github.io/cloudflare-prometheus-exporter/charts
helm install my-release cloudflare-exporter/cloudflare-prometheus-exporter
```

## Development

```bash
# Install development dependencies
pipenv install --dev

# Run unit tests
pipenv run unit-test

# Run integration tests - only running locally, requires valid Cloudflare token
pipenv run integration-test

# Run type checking
pipenv run typecheck

# Format code
pipenv run format

# Run linting
pipenv run lint

# Run security checks (dependencies and code analysis)
pipenv run security-check

# Build the Helm chart
pipenv run build-helm-chart

# Build Docker image
pipenv run build-docker-image
```

## Security

This project includes several security scanning tools:

1. **Trivy** - Scans for:
   - Container vulnerabilities
   - Infrastructure as Code issues
   - Git repository secrets
   - Software composition analysis (SCA)

2. **Bandit** - Static application security testing (SAST) for Python code

Security scans run:

- On every push to main
- On every pull request
- Weekly (scheduled) for the main branch
- Manually via `pipenv run security-check`

Results are available in the GitHub Security tab.

## Prometheus Configuration

Add the following to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'cloudflare'
    static_configs:
      - targets: ['localhost:8080/metrics']
    scrape_interval: 60s
```

## Grafana Dashboard

// TODO : no grafana dashboard exists yet

A sample Grafana dashboard is available in the `dashboards` directory.

## Further Reading

- [Cloudflare Analytics API](https://developers.cloudflare.com/analytics/graphql-api) documentation
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Python Cloudflare](https://github.com/cloudflare/python-cloudflare) library
- [Cloudflare CMB GraphQL Datasets](https://developers.cloudflare.com/data-localization/metadata-boundary/graphql-datasets/) - Official documentation of available datasets and their regional availability

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests and linting
4. Commit your changes following the commit lint guidelines (`git commit -m 'feat: add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.
