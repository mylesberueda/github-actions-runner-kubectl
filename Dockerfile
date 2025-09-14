# Custom GitHub Actions Runner with kubectl and additional tools
FROM ghcr.io/actions/actions-runner:latest

# Switch to root to install packages
USER root

# Install kubectl and other useful tools
RUN apt-get update && apt-get install -y \
  build-essential \
  curl \
  wget \
  unzip \
  jq \
  && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
  && chmod +x kubectl \
  && mv kubectl /usr/local/bin/

# Install helm (useful for your infrastructure)
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installations
RUN kubectl version --client \
  && helm version

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV MISE_DATA_DIR="/mise"
ENV MISE_CONFIG_DIR="/mise"
ENV MISE_CACHE_DIR="/mise/cache"
ENV MISE_INSTALL_PATH="/usr/local/bin/mise"
ENV PATH="/mise/shims:$PATH"

# Install mise globally (as root)
RUN curl https://mise.run | sh 
RUN mise use --global node@latest python@latest pnpm@latest

# Fix permissions for mise directory so runner user can access tools
RUN chown -R runner:runner /mise

USER runner
