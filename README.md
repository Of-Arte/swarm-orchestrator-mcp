# 🐝 Project Swarm

**An algorithmically-augmented MCP server for autonomous AI software engineering**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

- **⚡ Auto-Pilot Search** - Automatically optimizes symbol queries to ~1ms (200x faster than semantic)
- **🧠 HippoRAG Retrieval** - AST-based knowledge graphs with Personalized PageRank for deep code analysis
- **🔍 Hybrid Search** - Semantic + keyword search with optional embeddings (Gemini/OpenAI/Local)
- **🛡️ Active Guardrails** - Enforces best practices and rejects vague instructions
- **🐛 Ochiai SBFL** - Automated fault localization for debugging
- **🔒 OCC Validator** - Optimistic Concurrency Control for conflict-free edits
- **✅ Z3 Verifier** - Symbolic execution and formal verification
- **🐳 Docker Ready** - Runs as an MCP server locally or in containers

---

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/yourusername/swarm.git
cd swarm
docker compose up -d --build

# Server available at http://localhost:8000
```

### Local Installation

```bash
git clone https://github.com/yourusername/swarm.git
cd swarm
pip install -r requirements.txt

# Run as MCP server
python server.py

# Or use CLI directly
python orchestrator.py status
```

---

## Usage Example

```python
# AI Agent using Swarm via MCP

# 1. Search for code (auto-optimized for symbols)
search_codebase("UserModel")
# → ⚡ Auto-optimized to keyword search (~1ms)

# 2. Deep architectural analysis
retrieve_context("authentication flow")
# → Returns AST graph with call relationships

# 3. Process complex tasks
process_task("Refactor auth.py to use async/await")
# → Routes to OCC Validator for conflict-free editing
```

---

## Documentation

- **[Getting Started](docs/human/getting-started.md)** - Installation & first steps
- **[User Guide](docs/human/user-guide.md)** - Complete feature walkthrough
- **[Architecture](docs/human/architecture.md)** - System design & components
- **[API Reference](docs/human/api-reference.md)** - MCP tools & CLI commands
- **[Configuration](docs/human/configuration.md)** - Environment setup & providers
- **[Performance](docs/human/performance.md)** - Benchmarks & optimization

### For AI Agents

- **[Agent Guide](docs/ai/agent-guide.md)** - Decision trees & tool selection
- **[Tool Reference](docs/ai/tool-reference.md)** - Detailed specifications
- **[Examples](docs/ai/examples.md)** - Common workflows

---

## Integration

### Antigravity IDE

Add to your MCP configuration:

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

See [examples/mcp-configs/](examples/mcp-configs/) for more configurations.

---

## Contributing

See [docs/human/contributing.md](docs/human/contributing.md) for guidelines.

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Resources

- **MCP Protocol**: https://modelcontextprotocol.io
- **Documentation**: [docs/](docs/)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Security**: [SECURITY.md](SECURITY.md)

---

**Built with 💜 for autonomous AI development**
