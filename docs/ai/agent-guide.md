# Agent Guide

Optimized documentation for AI agents using Project Swarm via MCP.

## Quick Decision Tree

```
Need to find code?
├─ Exact symbol (UserModel, calculate_tax)?
│  └─ search_codebase(query)  # Auto-Pilot handles optimization
│
├─ Conceptual query (authentication logic)?
│  └─ search_codebase(query)  # Semantic search
│
└─ Need full architecture?
   └─ retrieve_context(query)  # AST + PageRank

Need to modify code?
├─ Simple, know what to change?
│  └─ Use built-in file tools
│
└─ Complex refactoring/debugging?
   └─ process_task(instruction)  # Routes to algorithms
```

---

## Tool Selection Matrix

| Task Type | Recommended Tool | Speed | Why |
|-----------|------------------|-------|-----|
| Find symbol: `UserModel` | `search_codebase(query)` | ~1ms | Auto-Pilot optimization |
| Find concept: "auth logic" | `search_codebase(query)` | ~240ms | Semantic understanding |
| Understand architecture | `retrieve_context(query)` | ~500ms-2s | AST graphs + dependencies |
| Refactor code | `process_task("Refactor...")` | ~1-30s | OCC conflict detection |
| Debug failing tests | `process_task("Debug...")` | ~1-30s | Ochiai SBFL |
| Verify correctness | `process_task("Verify...")` | ~1-30s | Z3 symbolic execution |

---

## Auto-Pilot Behavior

**Automatic Optimization:** `search_codebase` detects symbols and auto-executes keyword search.

**Symbol Patterns Detected:**
- CamelCase: `UserModel`, `HttpClient`
- snake_case: `calculate_tax`, `user_id`
- Functions: `authenticate()`
- Constants: `MAX_SIZE`, `API_KEY`
- Methods: `.validate`

**Example:**
```python
# You call (without optimization)
search_codebase("UserModel")

# Swarm executes
# 1. Detects symbol pattern
# 2. Tries keyword search (~1ms)
# 3. If results found: returns immediately
# 4. If no results: falls back to semantic search

# Response
"⚡ Auto-optimized to keyword search (~1ms) for symbol 'UserModel'.
Found 3 results:..."
```

**Key Insight:** You don't need to specify `keyword_only=True` for symbols. Swarm handles it automatically.

---

## Input Guardrails

`process_task` enforces quality:

**Rejected:**
```python
process_task("fix it")
# → ❌ Task Rejected: Instruction too short. Please be specific.
```

**Accepted:**
```python
process_task("Refactor auth.py to use async/await")
# → ✅ Routed to OCC Validator
```

**Requirements:**
- Minimum 3 words
- Specific target (file/function)
- Clear intent (refactor/debug/verify)

---

## Escalation Patterns

### Pattern 1: Search → Escalate

```python
# 1. Quick search
results = search_codebase("authentication")

# 2. If incomplete, escalate
if len(results) <= 2:
    context = retrieve_context("authentication flow")
```

**Swarm helps:** Sparse results trigger automatic escalation hints.

### Pattern 2: Keyword → Semantic

```python
# 1. Try keyword
results = search_codebase("NonExistentClass", keyword_only=True)

# 2. If no results, try semantic
if "No exact matches" in results:
    results = search_codebase("similar concept")
```

**Swarm helps:** Provides fallback suggestions automatically.

---

## Performance Optimization

### Use Auto-Pilot

**Don't:**
```python
search_codebase("UserModel", keyword_only=True)  # Manual optimization
```

**Do:**
```python
search_codebase("UserModel")  # Auto-Pilot handles it
```

### Choose Right Tool

| Speed Priority | Tool |
|----------------|------|
| Fastest | `search_codebase` (keyword) ~1ms |
| Fast | `search_codebase` (semantic) ~240ms |
| Deep | `retrieve_context` ~500ms-2s |

### Batch Operations

**Don't:**
```python
for symbol in ["UserModel", "AuthHandler", "Database"]:
    search_codebase(symbol)  # 3 separate calls
```

**Do:**
```python
# Use semantic search for multiple concepts
search_codebase("user authentication database models", top_k=15)
```

---

## Common Workflows

### Workflow 1: Code Discovery

```python
# 1. Quick overview
search_codebase("authentication")

# 2. Deep analysis
retrieve_context("authentication flow")

# 3. Modify
process_task("Refactor auth.py to use async/await")
```

### Workflow 2: Debugging

```python
# 1. Identify failure
# (Run tests, see test_login fails)

# 2. Locate fault
process_task("Debug test_login failure in test_auth.py")
# → Ochiai SBFL finds suspicious lines

# 3. Fix code
# (Use built-in file tools to apply fix)

# 4. Verify
# (Re-run tests)
```

### Workflow 3: Verification

```python
# 1. Find function
search_codebase("calculate_tax")

# 2. Verify correctness
process_task("Verify calculate_tax never returns negative values")
# → Z3 generates verification guide

# 3. Review proof
# (Check Z3 output for edge cases)
```

---

## Error Recovery

### "No index found"

**Error:**
```
⚠️ No index found. Please run 'index' command first.
```

**Solution:**
```python
index_codebase()
```

### "Task Rejected"

**Error:**
```
❌ Task Rejected: Instruction too short.
```

**Solution:** Be more specific:
```python
process_task("Refactor auth.py to use async/await")  # Good
```

### "No results found"

**Keyword search failed:**
```
🔍 No exact matches found.
💡 Tip: Try semantic search (remove keyword_only=True)
```

**Semantic search failed:**
```
🔍 No results found.
💡 Tip: Try retrieve_context() for deeper analysis
```

---

## Best Practices

### ✅ Do

- Let Auto-Pilot optimize symbol searches
- Use specific instructions for `process_task`
- Escalate from search to `retrieve_context` when needed
- Check `get_status()` for task progress

### ❌ Don't

- Manually specify `keyword_only=True` for obvious symbols
- Use vague instructions ("fix it")
- Call `index_codebase()` before every search
- Poll `get_status()` in tight loops

---

## Performance Reference

| Operation | Time | Notes |
|-----------|------|-------|
| Symbol search (Auto-Pilot) | ~1ms | Automatic keyword optimization |
| Semantic search | ~240ms | API embeddings (Gemini/OpenAI) |
| Semantic search (local) | ~50-100ms | Offline, no API |
| HippoRAG retrieval | ~500ms-2s | AST graph + PageRank |
| Task processing | ~1-30s | Varies by algorithm |
| Indexing (keyword) | ~0.2s | No embeddings |
| Indexing (API) | ~45s | 150 chunks |
| Indexing (local) | ~60-120s | 150 chunks |

---

## Multi-Tool Coordination

Swarm works alongside other MCP servers:

```
Search Phase:     search_codebase() → Find code
Context Phase:    retrieve_context() → Understand architecture
Modification:     process_task() → Refactor with OCC
Execution:        Docker MCP → Test in container
Version Control:  GitHub MCP → Create PR
Memory:           Memory MCP → Remember decisions
```

**Key Insight:** Use Swarm for code intelligence, other tools for execution/deployment.

---

## Advanced Features

### Custom top_k

```python
# More results for broad queries
search_codebase("error handling", top_k=15)

# Deeper context
retrieve_context("database layer", top_k=20)
```

### Provider Selection

```python
# Auto-detect best provider
index_codebase()

# Force specific provider
index_codebase(provider="gemini")  # Fast API
index_codebase(provider="local")   # Offline
```

### Task Routing

Swarm automatically routes based on instruction keywords:

| Keyword | Algorithm | Use Case |
|---------|-----------|----------|
| "refactor" | OCC Validator | Conflict-free edits |
| "debug" | Ochiai SBFL | Fault localization |
| "verify" | Z3 Verifier | Formal proof |
| "merge" | CRDT Merger | Concurrent edits |
| "analyze" | HippoRAG | Deep context |

---

## Troubleshooting

### Slow Searches

**Symptom:** Semantic searches taking >1s

**Solutions:**
1. Use Auto-Pilot for symbols (automatic)
2. Switch to Gemini/OpenAI (faster than local)
3. Use keyword search explicitly if needed

### Poor Results

**Symptom:** Search returns irrelevant code

**Solutions:**
1. Try semantic search (remove `keyword_only`)
2. Escalate to `retrieve_context()`
3. Increase `top_k` for more results

### Task Failures

**Symptom:** `process_task` returns errors

**Solutions:**
1. Check instruction specificity (>= 3 words)
2. Include file/function context
3. Use clear action verbs (refactor/debug/verify)
