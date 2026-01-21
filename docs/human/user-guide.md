# User Guide

Complete guide to using Project Swarm's features for code search, analysis, and task processing.

## Table of Contents

1. [Search Strategies](#search-strategies)
2. [Task Processing](#task-processing)
3. [Deep Code Analysis](#deep-code-analysis)
4. [Indexing Best Practices](#indexing-best-practices)
5. [Provider Configuration](#provider-configuration)
6. [Algorithm Workers](workers.md) - Detailed worker documentation

---

## Search Strategies

Swarm provides three search modes, each optimized for different use cases.

### Keyword Search (~1ms)

**Best for:** Exact symbols, class names, function names

```bash
# CLI
python orchestrator.py search "UserModel" --keyword

# MCP
search_codebase("UserModel", keyword_only=True)
```

**Auto-Pilot:** Swarm automatically uses keyword search for detected symbols:
```python
search_codebase("UserModel")  # No keyword_only flag needed
# → ⚡ Auto-optimized to keyword search (~1ms)
```

### Semantic Search (~240ms)

**Best for:** Conceptual queries, finding patterns

```bash
# CLI
python orchestrator.py search "authentication logic"

# MCP
search_codebase("authentication logic")
```

**Finds:**
- `OAuth2Handler` - conceptually related
- `JWTValidator` - conceptually related
- `session_manager` - conceptually related

### HippoRAG Retrieval (~500ms-2s)

**Best for:** Architectural analysis, call graphs, dependencies

```bash
# CLI
python orchestrator.py retrieve "database layer"

# MCP
retrieve_context("database layer", top_k=15)
```

**Returns:** AST-based knowledge graph with Personalized PageRank scores.

---

## Task Processing

### Basic Usage

```python
process_task("Refactor auth.py to use async/await")
```

### Task Routing

Swarm automatically routes tasks to specialized algorithms:

| Instruction Pattern | Algorithm | Purpose |
|---------------------|-----------|---------|

| "debug..." / "why is failing..." | Ochiai SBFL | Fault localization |
| "verify..." / "prove..." | Z3 Verifier | Formal verification |

| "analyze..." / "understand..." | HippoRAG | Deep context |

### Input Guardrails

Swarm rejects vague instructions:

```python
process_task("fix it")
# → ❌ Task Rejected: Instruction too short. Please be specific.

process_task("Refactor auth.py to use async/await")
# → ✅ Accepted and routed to General Worker
```

### Best Practices

✅ **Good Instructions:**
- "Refactor auth.py to use async/await"
- "Debug login failure in test_auth.py"
- "Verify calculate_tax never returns negative values"

❌ **Bad Instructions:**
- "fix auth"
- "help"
- "broken"

---

## Deep Code Analysis

### HippoRAG Features

HippoRAG builds an Abstract Syntax Tree (AST) knowledge graph and uses Personalized PageRank to find related code.

**When to use:**
- Understanding code architecture
- Finding ALL code related to a feature
- Analyzing dependencies and call graphs
- Complex refactoring requiring full context

**Example:**
```python
retrieve_context("authentication flow", top_k=10)
```

**Returns:**
```
🔍 Retrieved 10 context chunks for: authentication flow

1. [function] handle_oauth_callback
   auth/handlers.py:45-67
   PPR Score: 0.8734
   def handle_oauth_callback(request):...

2. [class] OAuthProvider
   auth/models.py:12-28
   PPR Score: 0.8123
   class OAuthProvider:...
```

### Context Isolation & Memory

When working in complex sessions, use the Orienting Protocol to stay focused:

```python
orient_context(session_id="auth-refactor")
# → 🧠 Swarm Orienting Protocol Results (Session: auth-refactor):
#   📍 Roadmap Snapshot (docs/sessions/auth-refactor/PLAN.md):
#   # Auth Refactor
#   - [x] Initial research
#   - [/] Implement async
#   ...
#
#   🔥 Active Task Files (2 total):
#     • task_123.md: Implement async support...
#     • task_456.md: Update tests...
```

### Escalation Pattern

Start with search, escalate if needed:

```python
# 1. Quick search
search_codebase("authentication")  # ~1ms or ~240ms

# 2. If results incomplete, escalate
retrieve_context("authentication flow")  # ~1s, full architecture
```

---

## Indexing Best Practices

### When to Index

✅ **Do index:**
- First-time setup
- After adding >10 new files
- After major refactoring
- When switching projects

❌ **Don't index:**
- Before every search (wasteful)
- After minor edits (index persists)

### Indexing Commands

```bash
# Auto-detect best provider
python orchestrator.py index

# Specific provider
python orchestrator.py index --provider gemini
python orchestrator.py index --provider openai
python orchestrator.py index --provider local

# Index specific directory
python orchestrator.py index --path /path/to/project
```

### Performance

| Provider | Indexing Time (150 chunks) | Search Time | Cost |
|----------|---------------------------|-------------|------|
| Keyword-only | ~0.2s | ~1ms | Free |
| Gemini API | ~45s | ~240ms | Free tier + pay-per-use |
| OpenAI API | ~45s | ~240ms | Pay-per-use |
| Local (offline) | ~60-120s | ~50-100ms | Free (400MB download) |

---

## Provider Configuration

### Gemini (Recommended)

```bash
# Set API key
export GEMINI_API_KEY="your-key-here"

# Index with Gemini
python orchestrator.py index --provider gemini
```

**Advantages:**
- Fast API calls (~2-5s for 150 chunks)
- Best quality semantic understanding
- Free tier available

### OpenAI

```bash
# Set API key
export OPENAI_API_KEY="your-key-here"

# Index with OpenAI
python orchestrator.py index --provider openai
```

**Advantages:**
- Alternative to Gemini
- Similar quality and speed

### Local (Offline)

```bash
# Uncomment in requirements.txt:
# sentence-transformers>=2.2.0

# Install
pip install sentence-transformers

# Index with local model
python orchestrator.py index --provider local
```

**Advantages:**
- Works offline
- No API costs
- Privacy (no data sent externally)

**Disadvantages:**
- Slower indexing (60-120s)
- ~400MB model download on first run
- Requires ~1GB RAM

### Auto-Detection

```bash
# Tries: GEMINI_API_KEY → OPENAI_API_KEY → Local → Keyword-only
python orchestrator.py index --provider auto
```

---

## Advanced Features

### Batch Operations

```bash
# Index multiple projects
for dir in project1 project2 project3; do
    python orchestrator.py index --path $dir
done
```

### Custom Filters

Swarm indexes these file extensions by default:
- `.py`, `.js`, `.ts`, `.jsx`, `.tsx`
- `.go`, `.rs`, `.java`, `.cpp`, `.c`

**Note:** Non-code files (`.md`, `.txt`, `.json`) are NOT indexed. Use `grep_search` for those.

### Performance Tuning

**For large codebases (>10k files):**
- Use keyword-only search when possible
- Increase `top_k` for broader results
- Consider indexing subdirectories separately

**For speed:**
- Use Auto-Pilot (automatic keyword optimization)
- Cache index files (`.swarm-cache/`)
- Use Gemini/OpenAI for faster semantic search than local

---

## Troubleshooting

### Search Returns No Results

1. **Check index exists:** `python orchestrator.py status`
2. **Try semantic search:** Remove `keyword_only=True`
3. **Escalate to HippoRAG:** Use `retrieve_context()`

### Slow Performance

1. **Use keyword search for symbols:** Auto-Pilot handles this automatically
2. **Switch to API embeddings:** Gemini/OpenAI faster than local
3. **Reduce `top_k`:** Fewer results = faster

### Task Rejected

Ensure instructions are:
- At least 3 words
- Specific about target file/function
- Include context about the issue



---

## Next Steps

- **[API Reference](api-reference.md)** - Detailed tool specifications
- **[Configuration](configuration.md)** - Advanced setup options
- **[Performance](performance.md)** - Benchmarks and optimization
