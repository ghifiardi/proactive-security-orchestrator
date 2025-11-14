# Dockerfile for Proactive Security Orchestrator

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Semgrep
RUN pip install --no-cache-dir semgrep

# Install Gitleaks (download from GitHub releases)
RUN GITLEAKS_VERSION=8.29.0 && \
    curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz | \
    tar -xz -C /usr/local/bin && \
    chmod +x /usr/local/bin/gitleaks

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install package in development mode
RUN pip install --no-cache-dir -e .

# Verify tools are installed
RUN semgrep --version && gitleaks version

# Set entrypoint
ENTRYPOINT ["python", "-m", "src.cli"]

# Default command
CMD ["--help"]

