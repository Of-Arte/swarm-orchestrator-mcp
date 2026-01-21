# Getting Started with Project Swarm

This guide will help you install and configure **Project Swarm v3.2** for your development environment.

## Prerequisites

- **Python 3.11+**
- **Docker** (recommended)
- **Google Gemini API Key** (Optional, for semantic search)
  - *Get one here: [Google AI Studio](https://aistudio.google.com/app/apikey)*

### Optional
- **OpenAI API Key** (Alternative to Gemini)
- **Git**

---

## Installation Methods

### Option 1: Docker with Stdio (Recommended for Local Development)

Docker with Stdio transport provides the most stable local development experience.

```bash
# Clone the repository
git clone https://github.com/yourusername/swarm.git
cd swarm

# Create .env file (optional, for semantic search)
echo "GEMINI_API_KEY=your_key_here" > .env

# Start the container
docker compose up -d --build

# Verify it's running
docker ps | grep swarm-mcp-server
```

**MCP Client Connection (Stdio via Docker Exec):**

```json
{
  "mcpServers": {
    "swarm-orchestrator": {
      "command": "docker",
      "args": ["exec", "-i", "swarm-mcp-server", "fastmcp", "run", "server.py"]
    }
  }
}
```

### Option 2: Docker with SSE (For Production/Remote)

For production deployments or remote access:

```bash
# Same setup as above
docker compose up -d --build

# Server available at http://localhost:8000/sse
```

**MCP Client Connection (SSE):**

```json
{
  "mcpServers": {
    "swarm-orchestrator": {
      "serverUrl": "http://localhost:8000/sse"
    }
  }
}
```

### Option 3: Local Python Installation

For development or direct CLI usage:

```bash
# Clone the repository
git clone https://github.com/yourusername/swarm.git
cd swarm

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the MCP server (Stdio Mode - default)
python server.py

# Or run in SSE mode
python server.py --sse
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Gemini API (Features: Search, Reasoning, Git Writer)
GEMINI_API_KEY=your-gemini-key-here

# Optional: Local Fallback (Ollama)
# Must point to OpenAI-compatible endpoint (/v1)
LOCAL_LLM_URL=http://localhost:11434/v1
```

### Embedding Providers

Swarm v3.2 is **Gemini-First**:
- **Gemini**: `models/text-embedding-004` (Default, Fast, High Quality)
- **Local**: `sentence-transformers` (Offline fallback)
- **Keyword**: BM25-like (No API needed)

See [configuration.md](configuration.md) for detailed provider setup.

---

## Quick Start: First Run

### 1. Validate Environment

```bash
python orchestrator.py check
```

This checks your dependencies and API key validity.

### 2. Index Your Codebase

```bash
# Auto-detects Gemini > Local > Keyword
python orchestrator.py index
```

**Performance**: ~45s for 100 files (Gemini Embeddings).

### 3. Search for Code

```bash
# Semantic search (understands concepts)
python orchestrator.py search "authentication logic"

# Keyword search (exact symbols)
python orchestrator.py search "UserModel" --keyword
```

### 4. Process Tasks (The "Swarm")

The Orchestrator routes complex tasks to specialized algorithmic workers:

```bash
# Git Task (Routes to Autonomous Git Team)
python orchestrator.py task "Create a new feature branch for user auth"

# Debugging Task (Routes to Ochiai SBFL)
python orchestrator.py task "Debug login failure in test_auth.py"
```

---

## MCP Integration

### Antigravity IDE / Generic Client

**Stdio Mode (Recommended for Local Development):**

```json
{
  "mcpServers": {
    "swarm-orchestrator": {
      "command": "docker",
      "args": ["exec", "-i", "swarm-mcp-server", "fastmcp", "run", "server.py"]
    }
  }
}
```

**SSE Mode (For Production/Remote):**

```json
{
  "mcpServers": {
    "swarm-orchestrator": {
      "serverUrl": "http://localhost:8000/sse"
    }
  }
}
```

**Transport Mode Comparison:**

| Mode | Use Case | Pros | Cons |
|------|----------|------|------|
| **Stdio** | Local development | No port conflicts, faster, no network stack | Requires running container |
| **SSE** | Production, remote access | HTTP-based, firewall-friendly | Port management, IPv4/IPv6 issues on Windows |

---

## Troubleshooting

### "Server not found" in MCP Client

**Cause**: Container not running or MCP client needs restart.
**Solution**:
```bash
# Verify container is running
docker ps | grep swarm-mcp-server

# If not running, start it
docker compose up -d

# Restart your IDE/MCP client to reload config
```

### "Connection Closed" or "EOF" Errors

**Cause**: Using wrong transport mode or container name mismatch.
**Solution**:
1. Verify your `mcp_config.json` uses the correct container name (`swarm-mcp-server`)
2. Ensure `docker exec -i` includes the `-i` (interactive) flag
3. Restart your IDE after config changes

### Port Conflicts (SSE Mode)

**Cause**: Port 8000 already in use.
**Solution**:
```bash
# Kill orphan processes
taskkill /F /IM python.exe  # Windows
pkill -f python  # Linux/Mac

# Or change port in docker-compose.yml
```

### "No index found" Error

**Solution**: Run `index_codebase()` or `python orchestrator.py index`.

### Memory/Context Issues

**Cause**: Memory files growing too large or stale.
**Solution**: Use the Memory Refresh Skill to consolidate `active/` into `archive/`.

---

## Next Steps

- **[User Guide](user-guide.md)** - Learn all features in depth
- **[Configuration](configuration.md)** - Advanced setup options
- **[Workers Guide](workers.md)** - Deep dive into Swarm algorithms

---

## Quick Reference

| Task | Command |
|------|---------|
| Validate environment | `python orchestrator.py check` |
| Index codebase | `python orchestrator.py index` |
| Index (keyword-only) | `python orchestrator.py index --provider keyword` |
| Search (keyword) | `python orchestrator.py search "term" --keyword` |
| Search (semantic) | `python orchestrator.py search "concept"` |
| Deep analysis | `python orchestrator.py retrieve "feature"` |
| Process task | `python orchestrator.py task "instruction"` |
| Check status | `python orchestrator.py status` |
| Run tests | `pytest tests/` |

