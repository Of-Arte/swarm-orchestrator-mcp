# API Reference

Complete reference for all MCP tools and CLI commands.

## MCP Tools

### search_codebase

Hybrid semantic + keyword search for code discovery.

**Signature:**
```python
def search_codebase(query: str, top_k: int = 5, keyword_only: bool = False) -> str
```

**Parameters:**
- `query` (str): Natural language description or exact keywords
- `top_k` (int, optional): Number of results to return (1-50, default 5)
- `keyword_only` (bool, optional): Skip semantic matching for faster literal searches

**Returns:** Formatted search results with file paths, line numbers, scores, and code snippets

**Auto-Pilot Behavior:**
- Automatically detects symbols (CamelCase, snake_case, CONSTANTS)
- Executes keyword search first (~1ms)
- Falls back to semantic search if no results

**Examples:**
```python
# Auto-optimized for symbols
search_codebase("UserModel")
# → ⚡ Auto-optimized to keyword search (~1ms)

# Semantic for concepts
search_codebase("authentication logic")
# → ~240ms, finds OAuth, JWT, sessions

# More results
search_codebase("error handling", top_k=10)
```

---

### index_codebase

Build search index with optional embeddings.

**Signature:**
```python
def index_codebase(path: str = ".", provider: str = "auto") -> str
```

**Parameters:**
- `path` (str, optional): Absolute or relative path to codebase root (default: current directory)
- `provider` (str, optional): Embedding provider - "auto" | "gemini" | "openai" | "local"

**Returns:** Number of indexed code chunks and status message

**Provider Options:**
- `auto` - Auto-detects: GEMINI_API_KEY → OPENAI_API_KEY → Local → Keyword-only
- `gemini` - Google Gemini API embeddings (fast, high quality)
- `openai` - OpenAI API embeddings (alternative to Gemini)
- `local` - Offline sentence-transformers (no API costs)

**Examples:**
```python
# Auto-detect best provider
index_codebase()

# Specific provider
index_codebase(provider="gemini")

# Index specific directory
index_codebase("/path/to/project")
```

---

### retrieve_context

Deep context retrieval via AST graph + PageRank (HippoRAG).

**Signature:**
```python
def retrieve_context(query: str, top_k: int = 10) -> str
```

**Parameters:**
- `query` (str): Natural language description of concept/feature to analyze
- `top_k` (int, optional): Number of context chunks to return (1-50, default 10)

**Returns:** Ranked code chunks with node types, PPR scores, file locations, and content

**When to Use:**
- Understanding code architecture and relationships
- Finding ALL code related to a feature (multi-hop reasoning)
- Analyzing dependencies and call graphs
- Complex refactoring requiring full context
- After `search_codebase()` for deeper analysis

**Examples:**
```python
# Understand architecture
retrieve_context("database models and migrations", top_k=15)

# Find all code involved in a feature
retrieve_context("payment processing pipeline")
```

---

### process_task

Execute a task using Swarm's algorithmic workers.

**Signature:**
```python
def process_task(instruction: str) -> str
```

**Parameters:**
- `instruction` (str): Natural language task description (specific, with context)

**Returns:** Task ID, status, and initial feedback from Swarm workers

**Input Guardrails:**
- Rejects instructions < 3 words
- Encourages specific, contextual instructions

**Task Routing:**
| Instruction Pattern | Algorithm |
|---------------------|-----------|
| "refactor..." | OCC Validator |
| "debug..." | Ochiai SBFL |
| "verify..." | Z3 Verifier |
| "merge..." | CRDT Merger |
| "analyze..." | HippoRAG |

**Examples:**
```python
# Refactoring
process_task("Refactor auth.py to use async/await")

# Debugging
process_task("Debug login failure in test_auth.py")

# Verification
process_task("Verify calculate_tax never returns negative values")
```

---

### get_status

Get current status of all tasks in the Swarm blackboard.

**Signature:**
```python
def get_status(limit: int = 10, show_all: bool = False) -> str
```

**Parameters:**
- `limit` (int, optional): Max number of tasks to return (default: 10)
- `show_all` (bool, optional): If true, ignore limit and show all tasks

**Returns:** Formatted list of tasks with their current status

**Example:**
```python
get_status()
# → 📋 Swarm Blackboard Status (Showing last 10 of 42 tasks):
#   • 3f2a1b4c: [COMPLETED] Refactor auth.py...
#   • 7d8e9f0a: [PENDING] Debug test_login...
#
# ...and 32 older tasks (use show_all=True to see all).
```

---

## CLI Commands

### index

Build search index for the codebase.

```bash
python orchestrator.py index [OPTIONS]
```

**Options:**
- `--path PATH` - Path to codebase root (default: current directory)
- `--provider PROVIDER` - Embedding provider: auto/gemini/openai/local (default: auto)

**Examples:**
```bash
# Auto-detect provider
python orchestrator.py index

# Specific provider
python orchestrator.py index --provider gemini

# Index specific directory
python orchestrator.py index --path /path/to/project
```

---

### search

Search the codebase.

```bash
python orchestrator.py search QUERY [OPTIONS]
```

**Options:**
- `-k, --keyword` - Use keyword-only search (no embeddings)
- `--top-k N` - Number of results to return (default: 5)

**Examples:**
```bash
# Keyword search
python orchestrator.py search "UserModel" --keyword

# Semantic search
python orchestrator.py search "authentication logic"

# More results
python orchestrator.py search "error handling" --top-k 10
```

---

### retrieve

Deep context retrieval via HippoRAG.

```bash
python orchestrator.py retrieve QUERY [OPTIONS]
```

**Options:**
- `--top-k N` - Number of context chunks (default: 10)

**Examples:**
```bash
# Architectural analysis
python orchestrator.py retrieve "database layer"

# More context
python orchestrator.py retrieve "payment processing" --top-k 15
```

---

### task

Process a task with Swarm orchestrator.

```bash
python orchestrator.py task INSTRUCTION
```

**Examples:**
```bash
# Refactoring
python orchestrator.py task "Refactor auth.py to use async/await"

# Debugging
python orchestrator.py task "Debug login failure in test_auth.py"
```

---

### status

Check orchestrator blackboard status.

```bash
python orchestrator.py status
```

---

### validate

Run quality gates and tests.

```bash
python orchestrator.py validate
```

Runs:
- Unit tests
- Coverage checks
- Lint checks

---

### benchmark

Run performance benchmarks.

```bash
python orchestrator.py benchmark
```

Tests search performance across different modes.

---

## MCP Resources

Swarm exposes documentation as discoverable MCP Resources:

| Resource URI | Content |
|--------------|---------|
| `swarm://docs/ai/guide` | Agent decision trees & workflows |
| `swarm://docs/ai/tools` | Tool specifications |
| `swarm://docs/ai/examples` | Workflow examples |
| `swarm://docs/architecture` | System design |
| `swarm://docs/getting-started` | Installation guide |
| `swarm://docs/user-guide` | Feature walkthrough |
| `swarm://docs/api-reference` | This document |
| `swarm://docs/configuration` | Provider setup |
| `swarm://docs/performance` | Benchmarks |
| `swarm://docs/changelog` | Version history |

**Usage:**
```python
# Discover resources
list_resources()

# Read resource
read_resource("swarm://docs/ai/guide")
```

---

## Error Handling

### Common Errors

**"No index found"**
```python
# Solution: Index first
index_codebase()
```

**"Task Rejected: Instruction too short"**
```python
# Solution: Be more specific
process_task("Refactor auth.py to use async/await")  # Good
process_task("fix it")  # Bad
```

**"No API key set, falling back to keyword search"**
```python
# Solution: Set API key or use local
export GEMINI_API_KEY="your-key"
# OR
index_codebase(provider="local")
```

---

## Performance Reference

| Tool | Speed | Best For |
|------|-------|----------|
| `search_codebase` (keyword) | ~1ms | Exact symbols |
| `search_codebase` (semantic) | ~240ms | Concepts |
| `retrieve_context` | ~500ms-2s | Architecture |
| `process_task` | ~1-30s | Modifications |
| `index_codebase` (keyword) | ~0.2s | Fast setup |
| `index_codebase` (API) | ~45s | Quality embeddings |
| `index_codebase` (local) | ~60-120s | Offline |
