# Dev Container Configuration

This directory contains the configuration for GitHub Codespaces and VS Code Dev Containers.

## What is this?

The `devcontainer.json` file defines a complete development environment for this project, including:

- **Python 3.12** runtime
- **Home Assistant 2025.1.4** and all test dependencies
- **Development tools** (ruff, mypy, pytest)
- **VS Code extensions** for Python development
- **Pre-configured settings** for linting and formatting

## Quick Start

### Using GitHub Codespaces

1. Click the **Code** button on GitHub
2. Select **Codespaces** tab
3. Click **Create codespace on main**
4. Wait for the environment to build (first time: ~3-5 minutes, with prebuilds: ~30 seconds)

### Using VS Code Locally

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open this repository in VS Code
3. Click "Reopen in Container" when prompted
4. Wait for the container to build

## What Happens on Creation

When a new Codespace or Dev Container is created:

1. Python 3.12 container is started
2. Git and GitHub CLI are installed
3. The `scripts/setup-test-env.sh` script runs automatically:
   - Creates a virtual environment
   - Installs Home Assistant 2025.1.4
   - Installs pytest and test dependencies
   - Installs development tools (ruff, mypy)

## Prebuilds

GitHub Codespaces Prebuilds speed up environment creation significantly:

- **Without prebuild**: 3-5 minutes to create a new Codespace
- **With prebuild**: 10-30 seconds to create a new Codespace

Prebuilds are automatically triggered:
- When `.devcontainer/` files change
- When `requirements*.txt` files change
- When setup scripts change
- Weekly on Sundays to keep the environment fresh

## Development Workflow

Once your environment is ready:

```bash
# Run tests
./scripts/run-tests.sh

# Lint code
ruff check custom_components/

# Type checking
mypy custom_components/violet_pool_controller/

# Activate test environment manually (if needed)
source activate-test-env.sh
```

## VS Code Extensions Included

- **Python** - Python language support
- **Pylance** - Fast Python language server
- **Ruff** - Fast Python linter and formatter
- **Black Formatter** - Code formatting
- **GitHub Copilot** - AI pair programming
- **YAML** - YAML language support

## Port Forwarding

Port 8123 is automatically forwarded, allowing you to access Home Assistant if you run a development instance.

## Troubleshooting

### Environment not activating

If the virtual environment isn't activated automatically:

```bash
source activate-test-env.sh
```

### Dependencies not installed

Re-run the setup script:

```bash
bash scripts/setup-test-env.sh
```

### Prebuild not working

Check the [Codespaces Prebuild workflow](../.github/workflows/codespaces-prebuild.yml) status in GitHub Actions.

## Learn More

- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [GitHub Codespaces](https://github.com/features/codespaces)
- [Codespaces Prebuilds](https://docs.github.com/en/codespaces/prebuilding-your-codespaces)
