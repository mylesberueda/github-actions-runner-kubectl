# GitHub Actions Runner with kubectl

Custom GitHub Actions runner image with `kubectl` pre-installed for Kubernetes-native CI/CD workflows.

## What's Included

| Tool | Purpose |
|------|---------|
| `kubectl` | Kubernetes CLI for deploying test infrastructure |
| `build-essential` | C compiler for native npm dependencies |
| `mise` + `node` + `pnpm` | Pre-installed for faster CI startup |

Base image: [`ghcr.io/actions/actions-runner`](https://github.com/actions/runner/pkgs/container/actions-runner)

## Usage in Workflows

```yaml
jobs:
  build:
    runs-on: arc-runner-set  # Your ARC scale set name
    steps:
      - uses: actions/checkout@v4
      # kubectl is available immediately
      - run: kubectl get pods -n test-services
```

## Building & Publishing

### Prerequisites

1. Install [mise](https://mise.jdx.dev/)
2. Create `mise.local.toml` with your credentials:

```toml
[env]
REGISTRY_USERNAME = "<your-github-username>"
REGISTRY_PASSWORD = "<github-personal-access-token>"
```

> **Note**: Generate a PAT at https://github.com/settings/tokens with `write:packages` scope.

### Commands

```bash
# Build with :latest tag
mise run build

# Build and push :latest
mise run release

# Build and push with specific tag
TAG=v1.0.0 mise run release:tagged
```

### All Available Tasks

| Task | Description |
|------|-------------|
| `mise run build` | Build image with `:latest` tag |
| `mise run login` | Login to container registry |
| `mise run push` | Push `:latest` (runs login first) |
| `mise run release` | Build and push `:latest` |
| `mise run build:tagged` | Build with `$TAG` (requires TAG env var) |
| `mise run release:tagged` | Build and push with `$TAG` |

## Configuration

Environment variables (set in `mise.local.toml` or export):

| Variable | Default | Description |
|----------|---------|-------------|
| `REGISTRY_URL` | `ghcr.io` | Container registry URL |
| `REGISTRY_USERNAME` | - | Registry username |
| `REGISTRY_PASSWORD` | - | Registry password/token |
| `IMAGE_NAME` | `github-actions-runner-kubectl` | Image name |
| `TAG` | `latest` | Image tag (for tagged builds) |
