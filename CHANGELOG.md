# CHANGELOG

<!-- version list -->

## v0.2.3 (2026-03-28)

### Bug Fixes

- Increment scrape error counter on fetch failures
  ([#42](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/42),
  [`706b85e`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/706b85eb2c47a3afd0eb554b57a051974526d6ec))


## v0.2.2 (2026-03-28)

### Bug Fixes

- Atomic metrics swap to eliminate gaps between cleanup and fetch
  ([#41](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/41),
  [`9a34c4f`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/9a34c4fbd02fefda646898c9e305aa3ede3cfff3))


## v0.2.1 (2026-03-28)

### Bug Fixes

- Regenerate uv.lock during semantic-release version bump
  ([#39](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/39),
  [`9226b3d`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/9226b3df9a6245c32313e06589b2a339dbe6ca80))

- Update python version badge to match requires-python
  ([#38](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/38),
  [`77611a8`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/77611a8f6bd84b8d1b02468405c76f8ec23502a7))

### Chores

- Add docker and helm info to release notes
  ([#34](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/34),
  [`e6f1f6b`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/e6f1f6b4f81f48b6d7b89d3698e1fa0fc4052220))

- Add path filter to release workflow
  ([#36](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/36),
  [`e647903`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/e647903726b153a19acabcc17058dbbc8c70c2d8))

- Consolidate pytest config into pyproject.toml
  ([#37](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/37),
  [`b3b003e`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/b3b003e4c179dbca8bfdb1123bcb2597d6c4020c))

- Remove pr docker image build
  ([#35](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/35),
  [`80fe0c5`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/80fe0c555d2f90e65f3809583045b58346c858d1))

- Remove redundant main push triggers from ci workflows
  ([#33](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/33),
  [`8f33da4`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/8f33da4afe835fadfe20f869d0591acc9154810b))


## v0.2.0 (2026-03-28)

### Features

- Rc release workflow with manual promotion
  ([#32](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/32),
  [`3fcd4b7`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/3fcd4b7c4e42c977467aa0f351147232d3668440))


## v0.1.5 (2026-03-28)

### Bug Fixes

- Update cloudflare SDK subscription API call for v4.3.x
  ([#31](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/31),
  [`0ebb339`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/0ebb3392e5fca1b22730cf439eb261da18bcbbc5))


## v0.1.4 (2026-03-28)

### Bug Fixes

- Bump ruff to v0.15.8 and python-json-logger to v4
  ([#30](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/30),
  [`da9fd2b`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/da9fd2b27951d6b3984f7c2fc0f5de74fdc670ed))


## v0.1.3 (2026-03-28)

### Bug Fixes

- Correct helm chart repository URLs in README
  ([#29](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/29),
  [`1dc2dd7`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/1dc2dd70b44a74fd38b12c8c62cad8364bd99284))

### Chores

- **deps**: Update dependency pytest to v9
  ([#25](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/25),
  [`81ce40c`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/81ce40cee6f5a25e3bcea3cc5c3dc96119b4b0a5))

- **deps**: Update dependency pytest-cov to v7
  ([#26](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/26),
  [`33786d3`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/33786d3a612839aa23f4582e209fadd7336395e2))

- **deps**: Update python docker tag to v3.14
  ([#22](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/22),
  [`6284c54`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/6284c54bde85ca8e9da2afc9f5dfafc3c9ecaf56))

- **deps**: Update python docker tag to v3.14
  ([#21](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/21),
  [`49c6ec4`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/49c6ec4e07efb91cf71015fca4df29634a5963e5))


## v0.1.2 (2026-03-28)

### Bug Fixes

- **deps**: Update python dependencies
  ([#24](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/24),
  [`015dd16`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/015dd1625df56b6d259fc5642b10ec367a308104))

### Chores

- Automerge patch updates via renovate
  ([#28](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/28),
  [`01daeb4`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/01daeb4d4ec9ea3efbefc6c90a9b54a7d801bc05))


## v0.1.1 (2026-03-28)

### Bug Fixes

- **deps**: Update dependency prometheus-client to v0.24.1
  ([#23](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/23),
  [`1e07fad`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/1e07fadd031df5f13094752d365bf1c6416019b0))

### Chores

- Group renovate updates by type
  ([#18](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/18),
  [`3e24d31`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/3e24d3174f67bee628cd51b23e01e9544e88246d))

- **config**: Migrate config renovate.json
  ([#19](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/19),
  [`16394a6`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/16394a64a989f155049e95fed87aeb0b6142334a))


## v0.1.0 (2026-03-28)

- Initial Release
