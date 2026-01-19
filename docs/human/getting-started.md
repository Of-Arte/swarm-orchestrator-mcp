# Getting Started with Project Swarm

This guide will help you install and configure Project Swarm for your development environment.

## Prerequisites

- **Python 3.11+**
- **Docker** (recommended for MCP server deployment)
- **Git**

### Optional
- **Gemini API Key** or **OpenAI API Key** (for semantic search)
- **sentence-transformers** (for offline semantic search)

---

## Installation Methods

### Option 1: Docker (Recommended)

Docker provides the easiest setup with full isolation:

```bash
# Clone the repository
git clone https://github.com/yourusername/swarm.git
cd swarm

# Start the MCP server
docker compose up -d --build

# Verify it's running
docker compose logs -f swarm-orchestrator

# Server will be available at http://localhost:8000
```

**Advantages:**
- No Python environment setup needed
- Isolated dependencies
- Easy to update and redeploy
- Works on Windows, macOS, Linux

### Option 2: Local Python Installation

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

# Run the MCP server
python server.py

# Or use the CLI directly
python orchestrator.py status
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Optional: Embedding providers (choose one)
GEMINI_API_KEY=your-gemini-key-here
# OR
OPENAI_API_KEY=your-openai-key-here

# Docker-specific
PYTHONUNBUFFERED=1
```

### Embedding Providers

Swarm works with **keyword-only search** by default (no API keys needed). For semantic search:

- **Gemini** (recommended): Fast, high-quality, free tier available
- **OpenAI**: Alternative to Gemini, similar quality
- **Local**: Offline, no API costs, requires `sentence-transformers` (~400MB download)

See [configuration.md](configuration.md) for detailed provider setup.

---

## First Steps

### 1. Index Your Codebase

```bash
# Using CLI
python orchestrator.py index

# Or via MCP (from AI agent)
index_codebase()
```

This creates a searchable index of your code. Takes ~0.2s for keyword-only, ~45s with API embeddings.

### 2. Search for Code

```bash
# Keyword search (fast)
python orchestrator.py search "UserModel" --keyword

# Semantic search (understands concepts)
python orchestrator.py search "authentication logic"
```

**From AI Agent:**
```python
# Auto-optimized for symbols
search_codebase("UserModel")
# → ⚡ Auto-optimized to keyword search (~1ms)

# Semantic for concepts
search_codebase("error handling patterns")
# → ~240ms, finds try/catch, Result types, etc.
```

### 3. Deep Code Analysis

```bash
# HippoRAG retrieval with AST graphs
python orchestrator.py retrieve "database layer"
```

**From AI Agent:**
```python
retrieve_context("authentication flow")
# → Returns ranked code chunks with call graph relationships
```

### 4. Process Tasks

```bash
# CLI task processing
python orchestrator.py task "Refactor auth.py to use async/await"
```

**From AI Agent:**
```python
process_task("Debug login failure in test_auth.py")
# → Routes to Ochiai SBFL for fault localization
```

---

## MCP Integration

### Antigravity IDE

Add to your MCP configuration file:

```json
{
  "mcpServers": {
    "swarm-orchestrator": {
      "command": "docker",
      "args": ["exec", "-i", "swarm-mcp-server", "python", "server.py"],
      "enabled": true,
      "autoAllow": ["search_codebase", "get_status", "retrieve_context"]
    }
  }
}
```

### Local (Non-Docker) Setup

```json
{
  "mcpServers": {
    "swarm-local": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/swarm",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "GEMINI_API_KEY": "your-key-here"
      }
    }
  }
}
```

See [examples/mcp-configs/](../../examples/mcp-configs/) for more examples.

---

## Troubleshooting

### "No index found" Error

**Solution:** Run `python orchestrator.py index` first.

### Slow Semantic Search

**Solution:** Use keyword search for symbols (`keyword_only=True`) or switch to Gemini/OpenAI for faster API embeddings.

### Docker Container Won't Start

**Solution:**
```bash
# Check logs
docker compose logs swarm-orchestrator

# Rebuild
docker compose down
docker compose up -d --build
```

### Import Errors

**Solution:** Ensure you're in the virtual environment and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## Next Steps

- **[User Guide](user-guide.md)** - Learn all features in depth
- **[API Reference](api-reference.md)** - Explore MCP tools and CLI commands
- **[Configuration](configuration.md)** - Advanced setup options
- **[Performance](performance.md)** - Optimization tips and benchmarks

---

## Quick Reference

| Task | Command |
|------|---------|
| Index codebase | `python orchestrator.py index` |
| Search (keyword) | `python orchestrator.py search "term" --keyword` |
| Search (semantic) | `python orchestrator.py search "concept"` |
| Deep analysis | `python orchestrator.py retrieve "feature"` |
| Process task | `python orchestrator.py task "instruction"` |
| Check status | `python orchestrator.py status` |
| Run tests | `pytest tests/` |
