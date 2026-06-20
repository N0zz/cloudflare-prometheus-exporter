# CHANGELOG

<!-- version list -->

## v0.2.8 (2026-06-20)

### Bug Fixes

- Pin actions/checkout to commit SHA in dockerhub-description workflow
  ([#58](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/58),
  [`0ce7f85`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/0ce7f856f5e1a49210eb45ee948a4ee6fb56f5c8))

### Chores

- **deps**: Update astral-sh/setup-uv action to v8
  ([#51](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/51),
  [`6696b68`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/6696b681ec45e3d0ad7fd0b455f254189223dd19))

- **deps**: Update dependency ruff to v0.15.18
  ([#62](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/62),
  [`12dd6be`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/12dd6be55a62e37191af25f0327c5f7283f88df9))

- **deps**: Update dependency ruff to v0.15.9
  ([#20](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/20),
  [`b3a3415`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/b3a3415e856b93e6e1b1851b56979f8d3a304f54))

- **deps**: Update docker/login-action action to v4.1.0
  ([#55](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/55),
  [`b58b4aa`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/b58b4aafa94cb19f89067d47c7d63cc92094ee8a))

- **deps**: Update ghcr.io/astral-sh/uv docker digest to 90bbb3c
  ([#54](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/54),
  [`1a4f676`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/1a4f67670ca4269019106aaf89a9c4b5cada6d51))

- **deps**: Update github actions
  ([#57](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/57),
  [`9b9f43b`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/9b9f43b728667c31ef21c4b3b14d0f41f2cf58ac))

- **deps**: Update github actions (major)
  ([#57](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/57),
  [`9b9f43b`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/9b9f43b728667c31ef21c4b3b14d0f41f2cf58ac))

### Continuous Integration

- Add top-level permissions to dockerhub-description workflow
  ([#60](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/60),
  [`b7a76e6`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/b7a76e6846691d229643b0b3f66aa5e9eb34c0f5))

- Add workflow to sync README to Docker Hub description
  ([#56](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/56),
  [`62cf75f`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/62cf75fb47cc72b7dc96514112601629189ba1b2))

- Add workflow_dispatch trigger and pin action to commit hash
  ([#56](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/56),
  [`62cf75f`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/62cf75fb47cc72b7dc96514112601629189ba1b2))

- Add zizmor workflow audit and rename dockerhub description workflow
  ([#59](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/59),
  [`cd45b61`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/cd45b61279ee2577dfb009bc9b5574695e15ef5c))

- Add zizmor workflow audit and rename dockerhub workflow
  ([#59](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/59),
  [`cd45b61`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/cd45b61279ee2577dfb009bc9b5574695e15ef5c))

- Bump codecov-action to v6.0.2 to fix GPG key fetch
  ([#63](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/63),
  [`623fa9e`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/623fa9ef87312048ed4aa0b50080fff80c3e7bd0))

- Fix Codecov upload failing on GPG signature verification
  ([#63](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/63),
  [`623fa9e`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/623fa9ef87312048ed4aa0b50080fff80c3e7bd0))

- Sync README to Docker Hub description
  ([#56](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/56),
  [`62cf75f`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/62cf75fb47cc72b7dc96514112601629189ba1b2))

- Tighten workflow permissions (add to dockerhub, remove checks:write from tests)
  ([#60](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/60),
  [`b7a76e6`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/b7a76e6846691d229643b0b3f66aa5e9eb34c0f5))

### Documentation

- Mention zizmor in security section of README
  ([#59](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/59),
  [`cd45b61`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/cd45b61279ee2577dfb009bc9b5574695e15ef5c))


## v0.2.7 (2026-03-31)

### Bug Fixes

- **deps**: Update dependency requests to v2.33.1
  ([#53](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/53),
  [`b6741bd`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/b6741bd918338106ed18039366476487bc4b659e))


## v0.2.6 (2026-03-30)

### Bug Fixes

- Remove Chart.yaml appVersion from semantic-release
  ([#52](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/52),
  [`4ed1b8c`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/4ed1b8c847908c5316b1c7b58220473b34ec800d))

- Remove Chart.yaml appVersion from semantic-release variables
  ([#52](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/52),
  [`4ed1b8c`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/4ed1b8c847908c5316b1c7b58220473b34ec800d))


## v0.2.5 (2026-03-29)

### Bug Fixes

- **deps**: Update dependency python-json-logger to v4.1.0
  ([#50](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/50),
  [`89fded0`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/89fded041049d013b6e534027962f453c88d56a6))


## v0.2.4 (2026-03-28)

### Bug Fixes

- **helm**: Improve chart configuration and conventions
  ([#43](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/43),
  [`97b8f4a`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/97b8f4a02ce56169a9a2e385cd317880596aa47d))

### Chores

- **helm**: Bump chart version to 0.2.1
  ([#45](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/45),
  [`8b2bafa`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/8b2bafab8c9821942a11d765f8ed071be33d6909))

### Continuous Integration

- Trigger chart release on helm file changes
  ([#44](https://github.com/N0zz/cloudflare-prometheus-exporter/pull/44),
  [`fa891d9`](https://github.com/N0zz/cloudflare-prometheus-exporter/commit/fa891d9ccf5ea2fb034ca1dc5c83ae69d9283d5f))


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
