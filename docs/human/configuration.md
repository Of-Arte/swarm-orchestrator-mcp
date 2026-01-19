# Configuration

Complete configuration guide for Project Swarm.

## Environment Variables

### Embedding Providers

```bash
# Gemini (recommended)
GEMINI_API_KEY=your-gemini-api-key-here

# OpenAI (alternative)
OPENAI_API_KEY=your-openai-api-key-here

# Legacy alias for Gemini
GOOGLE_API_KEY=your-google-api-key-here
```

### Docker Configuration

```bash
# Python output buffering (recommended for Docker)
PYTHONUNBUFFERED=1

# MCP server host/port (Docker only)
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

---

## Provider Configuration

### Auto-Detection (Recommended)

```python
index_codebase()  # Auto-detects best available provider
```

**Detection order:**
1. `GEMINI_API_KEY` → Gemini embeddings
2. `OPENAI_API_KEY` → OpenAI embeddings
3. `sentence-transformers` installed → Local embeddings
4. None available → Keyword-only search

### Gemini Configuration

**Setup:**
```bash
export GEMINI_API_KEY="your-key-here"
```

**Get API Key:**
1. Visit https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy and set as environment variable

**Specifications:**
- Model: `models/embedding-001`
- Dimensions: 768
- Rate limit: 60 requests/minute (free tier)
- Cost: Free tier available, then pay-per-use

### OpenAI Configuration

**Setup:**
```bash
export OPENAI_API_KEY="your-key-here"
```

**Get API Key:**
1. Visit https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and set as environment variable

**Specifications:**
- Model: `text-embedding-3-small`
- Dimensions: 1536
- Rate limit: Tier-based
- Cost: Pay-per-use ($0.02 per 1M tokens)

### Local Configuration

**Setup:**
```bash
# Uncomment in requirements.txt
# sentence-transformers>=2.2.0

# Install
pip install sentence-transformers

# Use
index_codebase(provider="local")
```

**Specifications:**
- Model: `all-MiniLM-L6-v2`
- Dimensions: 384
- Download size: ~400MB (first run)
- RAM usage: ~1GB
- No API calls, fully offline

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
      - GEMINI_API_KEY=${GEMINI_API_KEY:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
    volumes:
      - .:/app
      - .swarm-cache:/app/.swarm-cache
    restart: unless-stopped
```

### .env File

Create `.env` in project root:

```bash
GEMINI_API_KEY=your-key-here
# OR
OPENAI_API_KEY=your-key-here
```

---

## MCP Client Configuration

### Antigravity IDE

**Docker setup:**
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

**Local setup:**
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

### Cursor IDE

```json
{
  "mcpServers": {
    "swarm": {
      "command": "docker",
      "args": ["exec", "-i", "swarm-mcp-server", "python", "server.py"]
    }
  }
}
```

See [examples/mcp-configs/](../../examples/mcp-configs/) for more examples.

---

## Optional Dependencies

### Z3 Solver (Verification)

```bash
pip install z3-solver>=4.12.0
```

**Size:** ~100MB  
**Use case:** Formal verification with `process_task("Verify...")`

### Coverage (SBFL Debugging)

```bash
pip install coverage>=7.0
```

**Use case:** Automated fault localization with `process_task("Debug...")`



---

## Index Configuration

### File Extensions

**Indexed by default:**
- Python: `.py`
- JavaScript/TypeScript: `.js`, `.ts`, `.jsx`, `.tsx`
- Go: `.go`
- Rust: `.rs`
- Java: `.java`
- C/C++: `.cpp`, `.c`

**Not indexed:**
- Documentation: `.md`, `.txt`
- Data: `.json`, `.yaml`, `.xml`
- Config: `.ini`, `.toml`

**Note:** Use `grep_search` (built-in tool) for non-code files.

### Excluded Directories

**Automatically excluded:**
- `node_modules/`
- `.git/`
- `.venv/`, `venv/`
- `dist/`, `build/`
- `__pycache__/`
- `.pytest_cache/`

### Cache Location

Index cached in `.swarm-cache/index.json`

**Persistence:**
- Survives restarts
- Invalidated on re-index
- Can be deleted to force rebuild

---

## Performance Tuning

### For Large Codebases (>10k files)

1. **Use keyword-only search when possible**
2. **Index subdirectories separately**
3. **Increase cache size** (modify `IndexConfig` in code)

### For Speed

1. **Use Auto-Pilot** (automatic keyword optimization)
2. **Use Gemini/OpenAI** (faster than local embeddings)
3. **Reduce `top_k`** (fewer results = faster)

### For Offline Use

1. **Use local embeddings** (`provider="local"`)
2. **Pre-index before going offline**
3. **Cache persists** (no re-indexing needed)

---

## Troubleshooting

### API Key Not Working

**Gemini:**
```bash
# Test API key
curl -H "x-goog-api-key: YOUR_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models
```

**OpenAI:**
```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

### Docker Container Issues

```bash
# Check logs
docker compose logs swarm-orchestrator

# Restart
docker compose restart swarm-orchestrator

# Rebuild
docker compose down
docker compose up -d --build
```

### Permission Errors

```bash
# Fix cache permissions
chmod -R 755 .swarm-cache/

# Fix Docker volume permissions
docker compose down
sudo chown -R $USER:$USER .swarm-cache/
docker compose up -d
```

---

## Advanced Configuration

### Custom Index Config

Modify `mcp_core/search_engine.py`:

```python
class IndexConfig:
    root_path: str = "."
    extensions: list = [".py", ".js", ".ts"]  # Customize
    exclude_dirs: list = ["node_modules", ".git"]  # Customize
    chunk_size: int = 500  # Customize
```

### Custom Embedding Provider

Implement `EmbeddingProvider` interface:

```python
class CustomEmbedding(EmbeddingProvider):
    def embed(self, texts: list[str]) -> list[list[float]]:
        # Your implementation
        pass
```

---

## Security Considerations

### API Keys

- **Never commit** API keys to version control
- Use `.env` files (add to `.gitignore`)
- Use environment variables in production
- Rotate keys periodically

### Docker

- Use secrets for API keys in production
- Don't expose port 8000 publicly
- Use reverse proxy (nginx) for HTTPS

### Local Embeddings

- No data sent externally
- Fully offline operation
- Privacy-preserving

---

## Production Deployment

### Docker Compose (Production)

```yaml
version: '3.8'

services:
  swarm-orchestrator:
    build: .
    container_name: swarm-mcp-server
    ports:
      - "127.0.0.1:8000:8000"  # Localhost only
    environment:
      - PYTHONUNBUFFERED=1
    secrets:
      - gemini_api_key
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

secrets:
  gemini_api_key:
    external: true
```

### Systemd Service

```ini
[Unit]
Description=Swarm MCP Server
After=network.target

[Service]
Type=simple
User=swarm
WorkingDirectory=/opt/swarm
Environment="GEMINI_API_KEY=your-key"
ExecStart=/opt/swarm/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Next Steps

- **[Performance](performance.md)** - Benchmarks and optimization
- **[API Reference](api-reference.md)** - Tool specifications
- **[User Guide](user-guide.md)** - Feature walkthrough
