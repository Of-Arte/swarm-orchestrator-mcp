# Configuration

Complete configuration guide for Project Swarm v3.2 (Gemini-First).

## Environment Variables

### Core Configuration

```bash
# Gemini API Key (Required for all operations)
GEMINI_API_KEY=your-gemini-api-key-here

# Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8000
PYTHONUNBUFFERED=1
```

### Optional Configuration

```bash
# Ollama (Local Fallback)
# Defaults to http://localhost:11434/v1 if not set
# NOTE: Must include /v1 for OpenAI compatibility
LOCAL_LLM_URL=http://localhost:11434/v1

# System-Wide Lite Mode
# Set to 'true' to force keyword-only search and skip heavy parsers
SWARM_LITE_MODE=false
```

---

## Provider Configuration

### Gemini (Primary)

Project Swarm v3.2 is built to run natively on the Google Gemini API.

**Setup:**
```bash
export GEMINI_API_KEY="your-key-here"
```

**Capabilities:**
- **Inference**: Uses `gemini-3-flash-preview` (Primary), `gemini-2.5-flash` (Stable), `gemini-2.5-pro` (Reasoning).
- **Embeddings**: Uses `models/text-embedding-004` (768 dimensions).
- **Cost**: Free tier available, then pay-per-use.

### Ollama (Local Fallback)

Used for offline operations or privacy-critical tasks if `GEMINI_API_KEY` is unavailable or rate-limited.

**Setup:**
1. Install Ollama: https://ollama.ai/
2. Pull required models:
   ```bash
   ollama pull llama3
   ollama pull mxbai-embed-large
   ```
3. Swarm will auto-detect running Ollama instance.

---

## Docker Configuration

### docker-compose.yml

```yaml
version: '3.8'

services:
  swarm-orchestrator:
    build: .
    container_name: swarm-mcp-server
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - .:/app
      - .swarm-cache:/app/.swarm-cache
    restart: unless-stopped
```

### .env File

Create `.env` in project root:

```bash
GEMINI_API_KEY=your-actual-api-key
```

---

## MCP Client Configuration

**CRITICAL**: Swarm v3.2 uses **SSE (Server-Sent Events)** transport. Do NOT use `docker exec` (stdio) for MCP connection, as it causes immediate disconnection.

### Connection Details
- **Type**: SSE (Server-Sent Events)
- **URL**: `http://localhost:8000/sse`

### Antigravity IDE / Generic MCP Client

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

### Troubleshooting Connection

1. **"Connection Refused"**: Ensure Docker container is running (`docker compose ps`).
2. **"EOF" / "Client Closing"**: You are likely using `command: docker` (stdio). Switch to `serverUrl: http://localhost:8000/sse`.
3. **"404 Not Found"**: Verify you are hitting the `/sse` endpoint, not just `/`.

---

## Index Configuration

### File Extensions

**Indexed by default:**
- Python: `.py`
- JavaScript/Web: `.js`, `.ts`, `.jsx`, `.tsx`, `.html`, `.css`
- Native: `.go`, `.rs`, `.java`, `.cpp`, `.c`

**Not indexed:**
- Assets: `.png`, `.jpg`, `.svg`
- Build artifacts: `.min.js`, `.map`

### Excluded Directories

**Automatically excluded:**
- `node_modules/`
- `.git/`
- `.venv/`, `venv/`
- `dist/`, `build/`
- `__pycache__/`
- `.swarm-cache/`

### Cache Location

Index cached in `.swarm-cache/index.json`. Delete this directory to force a full re-index.

---

## Security Considerations

### API Keys
- Usage of `GEMINI_API_KEY` sends code snippets to Google Cloud for embedding and inference.
- **Enterprise Users**: Ensure your Google Cloud project has appropriate data privacy settings enabled.

### Network
- The FastMCP server binds to `0.0.0.0:8000` inside the container.
- Map this port only to `127.0.0.1:8000` in `docker-compose.yml` if you want to prevent external network access.

```yaml
    ports:
      - "127.0.0.1:8000:8000"
```
