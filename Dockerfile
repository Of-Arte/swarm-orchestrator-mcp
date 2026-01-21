# Use Python as the sole runtime (Swarm v3.0)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (Git is required for Autonomous Git Worker)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Configure Git identity for GitWorker (bot commits)
# Auth via GITHUB_TOKEN associates commits with user's account
RUN git config --global user.name "Swarm Bot" && \
    git config --global user.email "bot@swarm-mcp.dev"

# Install Python dependencies
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .

# Copy the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose MCP server port
EXPOSE 8000

# Verify v3.0 installation works (imports algorithms)
RUN python -c "from mcp_core.algorithms import HippoRAGRetriever; print('Swarm v3.0 Ready')"

# Default command: Run MCP server (bypassing fastmcp CLI to avoid run_stdio_async bug)
CMD ["python", "server.py", "--sse"]
