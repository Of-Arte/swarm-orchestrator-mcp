# Getting Started with Project Swarm

This guide will help you install and configure **Project Swarm v3.1** (Gemini-First Architecture) for your development environment.

## Prerequisites

- **Python 3.11+**
- **Docker** (recommended)
- **Google Gemini API Key** (Required for v3.1 full functionality)
  - *Get one here: [Google AI Studio](https://aistudio.google.com/app/apikey)*

### Optional
- **Ollama** (for local fallback)
- **Git**

---

## Installation Methods

### Option 1: Docker (Recommended)

Docker provides the easiest setup with full isolation.

**IMPORTANT**: Swarm v3.1 requires **SSE (Server-Sent Events)** for MCP communication. Do not use stdio.

```bash
# Clone the repository
git clone https://github.com/yourusername/swarm.git
cd swarm

# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Start the MCP server
docker compose up -d --build

# Verify it's running
docker compose logs -f swarm-orchestrator
```

**MCP Client Connection (SSE):**
- **URL**: `http://localhost:8000/sse`
- **Transport**: SSE (Server-Sent Events)

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

# Run the MCP server (SSE Mode)
python server.py
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

Swarm v3.1 is **Gemini-First**:
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
# Refactoring Task (Routes to OCC Validator)
python orchestrator.py task "Refactor auth.py to use async/await"

# Debugging Task (Routes to Ochiai SBFL)
python orchestrator.py task "Debug login failure in test_auth.py"
```

---

## MCP Integration

### Antigravity IDE / Generic Client

Add to your MCP configuration file:

```json
{
  "mcpServers": {
    "swarm-orchestrator": {
      "serverUrl": "http://localhost:8000/sse",
      "enabled": true,
      "autoAllow": ["search_codebase", "get_status", "retrieve_context", "process_task"]
    }
  }
}
```

**CRITICAL**: ensure you use `"serverUrl"` (SSE) and NOT `"command": "docker"` (stdio). Stdio is not supported in Docker mode for Swarm v3.1.

---

## Troubleshooting

### "EOF" or "Connection Closed" in MCP Client

**Cause**: You are likely using stdio transport (`docker exec ...`) instead of SSE.
**Solution**: Change your client config to use `http://localhost:8000/sse`.

### "No index found" Error

**Solution**: Run `index_codebase()` or `python orchestrator.py index`.

### Docker Container Won't Start

**Solution**:
```bash
# Check logs
docker compose logs swarm-orchestrator

# Rebuild
docker compose down
docker compose up -d --build
```

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

