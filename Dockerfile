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

# Install mise, for managing language versions
RUN curl https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh
RUN mise use --global node@latest python@latest

# Verify installations
RUN kubectl version --client \
  && helm version

# Switch back to runner user
USER runner

# Set working directory
WORKDIR /home/runner
