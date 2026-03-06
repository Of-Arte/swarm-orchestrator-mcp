# Build stage
FROM python:3.14-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from pyproject.toml
# Note: Pin dependencies in production by generating requirements.lock inside the container
ENV PYTHONPATH=/app/pkgs
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir --target=/app/pkgs .

# Runtime stage
FROM python:3.14-slim-bookworm

WORKDIR /app

# Install system dependencies required for runtime
# Git is required for Autonomous Git Worker
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22 LTS via NodeSource (Debian apt ships old/vulnerable version)
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub MCP Server globally (latest to get patched @modelcontextprotocol/sdk)
RUN npm install -g @modelcontextprotocol/server-github@latest
# Create non-root user
RUN useradd -m -u 1000 swarm && \
    chown -R swarm:swarm /app

# Copy dependencies from builder
ENV PYTHONPATH=/app/pkgs
COPY --from=builder /app/pkgs /app/pkgs

# Copy the application
COPY . .

# Ensure swarm user owns all files
RUN chown -R swarm:swarm /app

# Switch to non-root user
USER swarm

# Configure Git identity for GitWorker (bot commits)
RUN git config --global user.name "Swarm Bot" && \
    git config --global user.email "bot@swarm-mcp.dev"

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose MCP server port
EXPOSE 8000

# Verify v3.0 installation works (imports algorithms)
RUN python -c "from mcp_core.algorithms import HippoRAGRetriever; print('Swarm v3.0 Ready')"

# Default command: Run MCP server
CMD ["python", "server.py", "--sse"]

