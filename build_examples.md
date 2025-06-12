# Docker Build and Push Examples

This document provides examples of how to use the `build_and_push.py` script to build and push the GitHub Actions Runner with kubectl Docker image.

## Prerequisites

1. **Docker installed** and running on your system
2. **Python 3.6+** installed
3. **Registry credentials** (for pushing images)

## Basic Usage

### 1. Build and Push to GitHub Container Registry (ghcr.io)

```bash
# Set environment variables
export REGISTRY_USERNAME="mylesberueda"
export REGISTRY_PASSWORD="your_github_token"

# Build and push with default settings
python build_and_push.py
```

### 2. Build and Push to Docker Hub

```bash
# Build and push to Docker Hub
python build_and_push.py \
    --registry-url "docker.io" \
    --username "your_dockerhub_username" \
    --password "your_dockerhub_password"
```

### 3. Build Only (No Push)

```bash
# Build the image locally without pushing
python build_and_push.py --no-push
```

### 4. Build with Multiple Tags

```bash
# Build and push with multiple tags
python build_and_push.py \
    --tags latest v1.0.0 stable \
    --username "mylesberueda" \
    --password "your_token"
```

### 5. Build with Custom Image Name

```bash
# Use a custom image name
python build_and_push.py \
    --image-name "my-custom-runner" \
    --tags latest
```

## Environment Variables

You can set these environment variables instead of using command-line arguments:

```bash
export REGISTRY_URL="ghcr.io"                    # Default registry
export REGISTRY_USERNAME="mylesberueda"          # Your username
export REGISTRY_PASSWORD="your_token_here"       # Your token/password
export IMAGE_NAME="github-actions-runner-kubectl" # Image name
export IMAGE_TAG="latest"                        # Default tag
export DOCKERFILE_PATH="./Dockerfile"            # Dockerfile location
```

## GitHub Container Registry Setup

### 1. Create a Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Create a new token with `write:packages` permission
3. Use your GitHub username and the token as password

### 2. Example with GitHub Container Registry

```bash
# Using environment variables
export REGISTRY_USERNAME="mylesberueda"
export REGISTRY_PASSWORD="ghp_your_token_here"

python build_and_push.py --tags latest v1.0.0
```

The resulting image will be available at:
- `ghcr.io/mylesberueda/github-actions-runner-kubectl:latest`
- `ghcr.io/mylesberueda/github-actions-runner-kubectl:v1.0.0`

## Docker Hub Setup

### 1. Create Docker Hub Account and Access Token

1. Create account at hub.docker.com
2. Go to Account Settings → Security → New Access Token
3. Use your Docker Hub username and the access token

### 2. Example with Docker Hub

```bash
python build_and_push.py \
    --registry-url "docker.io" \
    --username "your_dockerhub_username" \
    --password "your_access_token" \
    --tags latest v1.0.0
```

## Build Arguments

You can pass build arguments to the Docker build process:

```bash
python build_and_push.py \
    --build-args "KUBECTL_VERSION=v1.28.0" "HELM_VERSION=v3.12.0"
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your username and password/token
   - Ensure the token has the correct permissions

2. **Dockerfile Not Found**
   - Check the `--dockerfile` path
   - Ensure you're running from the correct directory

3. **Build Failed**
   - Check Docker is running
   - Verify Dockerfile syntax
   - Check available disk space

### Debug Mode

Add verbose logging by modifying the script or checking Docker logs:

```bash
# Check Docker daemon logs
docker system events

# Check built images
docker images | grep github-actions-runner-kubectl
```

## Security Notes

- Never commit passwords or tokens to version control
- Use environment variables or secure secret management
- Consider using Docker credential helpers for production use
- Regularly rotate access tokens

## Integration with CI/CD

This script can be easily integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Build and Push Docker Image
  env:
    REGISTRY_USERNAME: ${{ github.actor }}
    REGISTRY_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python build_and_push.py --tags latest ${{ github.sha }}
```
