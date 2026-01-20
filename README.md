<div align="center">

```
███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗
██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║
███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║
╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║
███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
```

### 🐝 **Algorithmic Intelligence Meets Autonomous Development**

---

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![MCP](https://img.shields.io/badge/MCP-Compatible-00ADD8?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMiA3TDEyIDEyTDIyIDdMMTIgMloiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik0yIDEyTDEyIDE3TDIyIDEyIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiLz4KPC9zdmc+)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[![CI](https://github.com/agentagony/swarm/actions/workflows/ci.yml/badge.svg)](https://github.com/agentagony/swarm/actions)
[![Security](https://github.com/agentagony/swarm/actions/workflows/security.yml/badge.svg)](https://github.com/agentsagony/swarm/actions)

</div>

---

## 🌟 What Makes Swarm Different?

> [!IMPORTANT]
> **Swarm isn't just another MCP server.** While most MCP servers simply wrap APIs or provide basic file operations, Swarm brings **deterministic algorithms** from computer science research into AI agent workflows.

<table>
<tr>
<td width="50%">

### 🧠 **Algorithmic Intelligence**
- **HippoRAG**: AST-based knowledge graphs with Personalized PageRank
- **Ochiai SBFL**: Statistical fault localization for debugging
- **Z3 Verifier**: Formal verification using SMT solving
- **CRDT Merger**: Conflict-Free Replicated Data Types

</td>
<td width="50%">

### ⚡ **Performance-First Design**
- **Auto-Pilot Search**: Symbol queries execute at ~1ms (200x faster than semantic)
- **Multi-Language AST**: Python, JavaScript, TypeScript support
- **Hybrid Search**: Semantic + keyword with multiple embedding providers
- **Rolling Memory**: LLM-native context management

</td>
</tr>
</table>

### 📊 Swarm vs Standard MCP Servers

| Feature | Standard MCP | Swarm MCP |
|---------|-------------|-----------|
| **Search Method** | Basic keyword/regex | Hybrid semantic + keyword with auto-optimization |
| **Code Understanding** | Text parsing | AST-based knowledge graphs with PageRank |
| **Conflict Resolution** | Manual review | Automated OCC validation |
| **Debugging** | Stack trace reading | Statistical fault localization (Ochiai) |
| **Language Support** | Single or limited | Python, JavaScript, TypeScript (extensible) |
| **Memory Management** | Stateless | Rolling memory with active/archive tiers |
| **Verification** | None | Z3 SMT solver integration |

---

## 🚀 Quick Start

<details open>
<summary><b>🐳 Docker Installation (Recommended)</b></summary>

```bash
# Clone and launch
git clone https://github.com/yourusername/swarm.git
cd swarm
docker compose up -d --build

# Server available at http://localhost:8000
```

**Configure your IDE:**
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

</details>

<details>
<summary><b>💻 Local Installation</b></summary>

```bash
git clone https://github.com/yourusername/swarm.git
cd swarm
pip install -r requirements.txt

# Run as MCP server
python server.py

# Or use CLI directly
python orchestrator.py status
```

</details>

> [!TIP]
> **First time setup?** Set your `GEMINI_API_KEY` in `.env` for best performance. Swarm supports multiple embedding providers (Gemini, OpenAI, local).

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "AI Agent Interface"
        IDE[IDE/Client]
    end
    
    subgraph "MCP Layer"
        FastMCP{FastMCP Server}
    end
    
    subgraph "Core Intelligence"
        Orchestrator[Orchestrator Engine]
        Blackboard[(Project State)]
    end
    
    subgraph "Algorithmic Workers"
        HippoRAG[🧠 HippoRAG<br/>AST + PageRank]
        OCC[🔒 OCC Validator<br/>Conflict Detection]
        SBFL[🐛 Ochiai SBFL<br/>Fault Localization]
        Z3[✅ Z3 Verifier<br/>Formal Proof]
        CRDT[🔄 CRDT Merger<br/>Concurrent Edits]
    end
    
    subgraph "External Services"
        Gemini[Google Gemini API]
        Search[Hybrid Search Engine]
        Git[Autonomous Git]
    end
    
    IDE --> FastMCP
    FastMCP --> Orchestrator
    Orchestrator --> Blackboard
    
    Orchestrator --> HippoRAG
    Orchestrator --> OCC
    Orchestrator --> SBFL
    Orchestrator --> Z3
    Orchestrator --> CRDT
    
    Orchestrator --> Gemini
    Orchestrator --> Search
    Orchestrator --> Git
    
    style HippoRAG fill:#9b59b6
    style OCC fill:#3498db
    style SBFL fill:#e74c3c
    style Z3 fill:#2ecc71
    style CRDT fill:#f39c12
```

### 🔍 How It Works

```mermaid
flowchart LR
    A[Agent Query] --> B{Query Type?}
    
    B -->|Symbol: UserModel| C[⚡ Keyword Search<br/>~1ms]
    B -->|Concept: auth logic| D[🧠 Semantic Search<br/>~240ms]
    B -->|Architecture: payment flow| E[🔬 HippoRAG<br/>~1-2s]
    
    C --> F{Found?}
    D --> F
    
    F -->|Yes| G[Return Results]
    F -->|No Results| H[Suggest Alternatives]
    
    E --> I[AST Graph Analysis]
    I --> J[PageRank Scoring]
    J --> K[Return Context Map]
    
    style C fill:#2ecc71
    style D fill:#3498db
    style E fill:#9b59b6
```

---

## ✨ Features Deep Dive

### 🧠 **HippoRAG: Deep Code Understanding**

Unlike traditional semantic search, HippoRAG builds an Abstract Syntax Tree (AST) knowledge graph of your codebase and uses **Personalized PageRank** to find architecturally relevant code.

```python
# Traditional search finds the function name
search_codebase("UserModel")  # ✓ Fast but shallow

# HippoRAG finds everything connected to the concept
retrieve_context("user authentication flow")
# → Returns: UserModel, AuthService, TokenManager, 
#            SessionStore, LoginController
# → Includes: Call graphs, import chains, usage patterns
```

**Supported Languages:**
- 🐍 **Python** (built-in `ast` module)
- 📜 **JavaScript/JSX** (via Tree-sitter)
- 🔷 **TypeScript/TSX** (via Tree-sitter)
- 🔜 **Go, Rust, Java** (plugin system ready)

> [!NOTE]
> HippoRAG is **200-2000x slower** than keyword search (~1-2s vs ~1ms) but provides deep architectural context. Use it when you need to understand relationships, not just find text.

---

### ⚡ **Auto-Pilot Search Optimization**

Swarm automatically detects if you're searching for a symbol or a concept and optimizes accordingly:

```python
# Automatically uses keyword search (1ms)
search_codebase("UserModel")
search_codebase("calculate_tax")
search_codebase("API_KEY")

# Automatically uses semantic search (240ms)
search_codebase("authentication logic")
search_codebase("database connection pooling")
search_codebase("error handling patterns")
```

**Performance Comparison:**

| Search Type | Speed | Use When |
|------------|-------|----------|
| **Keyword** | ~1ms | You know the exact name (class, function, variable) |
| **Semantic** | ~240ms | You know the concept but not the implementation |
| **HippoRAG** | ~1-2s | You need to understand architecture and relationships |

---

### 🔒 **OCC Validator: Conflict-Free Editing**

Optimistic Concurrency Control ensures your edits won't conflict with concurrent changes:

```python
# Swarm automatically validates edits before applying
process_task("Refactor auth.py to use async/await")
# → OCC checks: Has auth.py changed since we read it?
# → If conflict: Suggests merge strategy
# → If clean: Applies atomically
```

---

### 🐛 **Ochiai SBFL: Automated Fault Localization**

Statistical fault localization pinpoints bugs faster than manual debugging:

```bash
# Traditional debugging: read stack traces, guess locations
pytest tests/test_payment.py  # ❌ 3 tests fail

# Ochiai debugging: statistically identifies suspicious code
python orchestrator.py debug --test-cmd "pytest tests/test_payment.py"
# → payment.py:127 (Suspiciousness: 0.89)
# → payment.py:145 (Suspiciousness: 0.76)
# → utils.py:23 (Suspiciousness: 0.34)
```

---

### 📝 **Rolling Memory System**

LLM-native context management prevents prompt bloat:

```
memory/
├── active/           # Current session context
│   ├── task_001.md   # In-progress refactoring
│   └── context_auth.md
└── archive/          # Completed work (compressed)
    └── 2026-01-19.md
```

**Memory Skills:**
- `orient_context`: Session initialization and context loading
- `refresh_memory`: Prune completed tasks to archive
- `roadmap_sync`: Track long-term project goals

---

## 🎯 Tool Selection Guide

**Which tool should your agent use?**

```mermaid
flowchart TD
    Start([I need...]) --> Q1{What do you need?}
    
    Q1 -->|Find specific code| Q2{Do you know the name?}
    Q1 -->|Understand architecture| HippoRAG[retrieve_context]
    Q1 -->|Make changes| Process[process_task]
    Q1 -->|Debug failing tests| SBFL[debug command]
    
    Q2 -->|Yes: UserModel| Keyword[search_codebase<br/>keyword_only=true<br/>~1ms]
    Q2 -->|No: user auth stuff| Semantic[search_codebase<br/>default mode<br/>~240ms]
    
    Semantic --> Q3{Found enough?}
    Q3 -->|Yes| Done[✓]
    Q3 -->|No/incomplete| HippoRAG
    
    Keyword --> Q4{Found it?}
    Q4 -->|Yes| Done
    Q4 -->|No| Semantic
    
    style Keyword fill:#2ecc71
    style Semantic fill:#3498db
    style HippoRAG fill:#9b59b6
    style Process fill:#e67e22
    style SBFL fill:#e74c3c
```

---

## 📖 Documentation

<table>
<tr>
<td width="50%">

### 👨‍💻 For Humans
- [Getting Started](docs/human/getting-started.md)
- [User Guide](docs/human/user-guide.md)
- [Algorithm Workers](docs/human/workers.md)
- [API Reference](docs/human/api-reference.md)
- [Configuration](docs/human/configuration.md)
- [Performance](docs/human/performance.md)

</td>
<td width="50%">

### 🤖 For AI Agents
- [Agent Guide](docs/ai/agent-guide.md)
- [Tool Reference](docs/ai/tool-reference.md)
- [Examples](docs/ai/examples.md)
- [Decision Trees](docs/ai/agent-guide.md#decision-trees)

</td>
</tr>
</table>

---

## 🛠️ Usage Examples

### Example 1: Deep Architectural Analysis

```python
# Step 1: Quick search to find entry point
search_codebase("PaymentProcessor", keyword_only=True)
# → Found: payment/processor.py:PaymentProcessor

# Step 2: Deep dive into the architecture
retrieve_context("payment processing pipeline")
# → Returns knowledge graph:
#   - PaymentProcessor (entry point)
#   - StripeClient (external API)
#   - TransactionLogger (observability)
#   - PaymentQueue (async processing)
#   - RefundHandler (error recovery)
#   - Call graph with dependencies
```

### Example 2: Conflict-Free Refactoring

```python
# Let Swarm handle the complexity
process_task("""
Refactor payment/processor.py to:
1. Use async/await instead of callbacks
2. Add retry logic with exponential backoff
3. Ensure thread-safety
""")

# Swarm will:
# ✓ Route to OCC Validator to detect conflicts
# ✓ Analyze AST to understand current structure
# ✓ Apply changes atomically
# ✓ Verify no concurrent edits occurred
```

### Example 3: Automated Debugging

```bash
# Tests are failing, but where's the bug?
python orchestrator.py debug --test-cmd "pytest tests/test_auth.py::TestLogin"

# Output:
# 🐛 Ochiai Fault Localization Results:
# 
# Suspiciousness Rankings:
# 1. auth/login.py:89  (0.92) ← Check here first!
# 2. auth/session.py:45 (0.78)
# 3. utils/crypto.py:12 (0.34)
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required for best performance
GEMINI_API_KEY=your_key_here

# Optional: Alternative embedding providers
OPENAI_API_KEY=your_key_here

# Optional: Ollama for local models
OLLAMA_BASE_URL=http://localhost:11434
```

### Embedding Provider Options

```python
# Auto-detect best available (recommended)
index_codebase()  # Tries: Gemini → OpenAI → Local → Keyword-only

# Force specific provider
index_codebase(provider="gemini")  # Fast API calls (~2-5s)
index_codebase(provider="openai")  # Alternative fast option
index_codebase(provider="local")   # Offline, no API costs (~60-120s)
```

> [!WARNING]
> Local embeddings require ~400MB model download on first run and are significantly slower. Use API providers for production.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### 🎯 Areas We Need Help
- [ ] Parser plugins for Go, Rust, Java
- [ ] Performance benchmarks for large codebases (>100k files)
- [ ] Integration guides for other IDEs
- [ ] Additional algorithm workers (BERT-based search, neural bug localization)

---

## 📊 Performance Metrics

| Operation | Swarm | Alternative | Speedup |
|-----------|-------|-------------|---------|
| **Symbol Search** | ~1ms | ~240ms (semantic only) | **240x** |
| **Codebase Indexing** (Gemini) | ~45s (150 chunks) | N/A | - |
| **Codebase Indexing** (Local) | ~60-120s | N/A | - |
| **HippoRAG Retrieval** | ~1-2s | N/A (unique feature) | - |
| **OCC Validation** | ~50ms | Manual review | **∞** |

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🔗 Resources

<table>
<tr>
<td align="center" width="25%">

### 📚 Docs
[Documentation](docs/)

</td>
<td align="center" width="25%">

### 📝 Changelog
[CHANGELOG.md](CHANGELOG.md)

</td>
<td align="center" width="25%">

### 🔒 Security
[SECURITY.md](SECURITY.md)

</td>
<td align="center" width="25%">

### 🏗️ Architecture
[ARCHITECTURE.md](ARCHITECTURE.md)

</td>
</tr>
</table>

<div align="center">

---

### 🌐 Learn More

[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-00ADD8?style=flat-square)](https://modelcontextprotocol.io)
[![HippoRAG Paper](https://img.shields.io/badge/HippoRAG-Research-9b59b6?style=flat-square)](https://arxiv.org/)
[![Ochiai SBFL](https://img.shields.io/badge/SBFL-Ochiai-e74c3c?style=flat-square)](https://en.wikipedia.org/wiki/Fault_localization)

---

**Built with 💜 for autonomous AI development**

*Where algorithms meet intelligence*

</div>
