# Tool Reference

Detailed specifications for AI agents using Swarm MCP tools.

## search_codebase `[Scope: General]`

### Input Validation

- `query`: string, required, non-empty
- `top_k`: integer, 1-50, default 5
- `keyword_only`: boolean, default false

### Output Format

```
[Optional: Auto-Pilot message]
🔍 Found {count} results for: {query}

1. {file_path}:{start_line}-{end_line}
   Score: {score}
   {content_preview}...

[Optional: Escalation hint]
```

### Auto-Pilot Triggers

Symbol patterns (regex):
- `^[A-Z][a-zA-Z0-9]+$` - CamelCase
- `^[a-z_][a-z0-9_]+$` - snake_case
- `^[a-z_][a-z0-9_]*\(\)$` - function()
- `^\.\w+$` - .method
- `^[A-Z][A-Z_0-9]+$` - CONSTANTS

### Fallback Messages

**Keyword search, no results:**
```
🔍 No exact matches found.
💡 Tip: Try semantic search (remove keyword_only=True)
```

**Semantic search, no results:**
```
🔍 No results found.
💡 Tip: Try retrieve_context() for deeper analysis
```

**Semantic search, sparse results (≤2):**
```
💡 Few results found. Consider retrieve_context() for deeper analysis
```

---

## index_codebase `[Scope: General]`

### Input Validation

- `path`: string, valid directory path, default "."
- `provider`: enum ["auto", "gemini", "openai", "local"], default "auto"

### Provider Auto-Detection

1. Check `GEMINI_API_KEY` → use Gemini
2. Check `OPENAI_API_KEY` → use OpenAI
3. Check `sentence-transformers` installed → use Local
4. Fallback → Keyword-only (no embeddings)

### Output Format

```
✅ Indexed {count} chunks from {path}
```

### Error Cases

- Invalid path: `❌ Error: Path not found`
- API key invalid: Falls back to next provider
- No provider available: Uses keyword-only

---

## retrieve_context `[Scope: General]`

### Input Validation

- `query`: string, required, non-empty
- `top_k`: integer, 1-50, default 10

### Output Format

```
🔍 Retrieved {count} context chunks for: {query}

1. [{node_type}] {node_name}
   {file_path}:{start_line}-{end_line}
   PPR Score: {ppr_score}
   {content_preview}...
```

### Node Types

- `function` - Function definitions
- `class` - Class definitions
- `method` - Class methods
- `import` - Import statements

### Error Cases

- No Python files: `❌ Error: No Python files found`
- Graph build failure: `❌ Error: Failed to build AST graph`

---

## process_task `[Scope: General]`

### Input Validation

**Guardrails:**
- Minimum length: 3 words
- Rejects if `len(instruction.split()) < 3`

**Rejection message:**
```
❌ Task Rejected: Instruction too short. Please be specific (e.g., 'Refactor auth.py to use async').
```

### Task Routing

Automatic routing based on instruction keywords:

| Keyword | Algorithm | Trigger Pattern |
|---------|-----------|-----------------|

| debug | Ochiai SBFL | `"debug" in instruction.lower()` |
| verify, prove | Z3 Verifier | `"verify" or "prove" in instruction.lower()` |

| analyze, understand | HippoRAG | `"analyze" or "understand" in instruction.lower()` |

### Output Format

```
✅ Task {task_id} created and processed.
Status: {status}
Feedback: {feedback}
```

### Error Cases

- Vague instruction: Guardrail rejection
- Orchestrator failure: `❌ Error: {error_message}`

---

## get_status `[Scope: General]`

### Input Validation

None (no parameters)

### Output Format

**With tasks:**
```
📋 Swarm Blackboard Status:

  • {task_id}: [{status}] {description}...
  • {task_id}: [{status}] {description}...
```

**No tasks:**
```
📋 No tasks found in the blackboard.
```

### Task Statuses

- `PENDING` - Awaiting processing
- `IN_PROGRESS` - Currently processing
- `COMPLETED` - Finished successfully
- `FAILED` - Error occurred

---

## check_health `[Scope: Internal]`

**Requires**: `SWARM_INTERNAL_TOOLS=true`

### Input Validation
None (no parameters)

### Output Format
```
🏥 Swarm System Health Check

✅ Telemetry DB: 0.11 MB
✅ All tools performing well (>70% success)
✅ PostgreSQL: Connected

📊 Environment:
   Container: No
   Debug Mode: Off
```

### Usage Heuristics
- Use when debugging system stability.
- Use if tools return "Connection Refused" or unexpected errors.

---

## debug_mcp_transport `[Scope: Internal]`

**Requires**: `SWARM_INTERNAL_TOOLS=true`

### Input Validation
- `target_url`: Optional string (for SSE)
- `container_name`: Optional string (for Docker stdio)

### Output Format
```
🔍 MCP Transport Debugger
------------------------
Target: http://localhost:8000/sse

✅ Connection Successful (200 OK)
⏱️ Latency: 15ms
```

### Usage Heuristics
- Use when agents report "MCP Connection Error".
- Use to verify Docker container reachability.

---

## Performance Specifications

| Tool | Typical Time | Max Time | Factors |
|------|--------------|----------|---------|
| search_codebase (keyword) | 1ms | 10ms | Index size |
| search_codebase (semantic, API) | 240ms | 500ms | API latency |
| search_codebase (semantic, local) | 50-100ms | 200ms | CPU speed |
| retrieve_context | 500ms-2s | 5s | Graph size |
| process_task | 1-30s | 60s | Task complexity |
| index_codebase (keyword) | 0.2s | 1s | File count |
| index_codebase (API) | 45s | 120s | Chunk count, API |
| index_codebase (local) | 60-120s | 300s | CPU speed |

---

## Rate Limits

### API Providers

**Gemini:**
- Free tier: 60 requests/minute
- Paid: Higher limits

**OpenAI:**
- Tier-based limits
- Check OpenAI dashboard

### Local

No rate limits (CPU-bound)

---

## Caching Behavior

### Search Index

- Cached in `.swarm-cache/index.json`
- Persists between runs
- Invalidated on re-index

### Embeddings

- Cached with index
- Reused across searches
- Regenerated on re-index

---

## Error Codes

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "No index found" | Index not created | Run `index_codebase()` |
| "Task Rejected" | Instruction too short | Be more specific (>= 3 words) |
| "No API key set" | Missing env var | Set `GEMINI_API_KEY` or `OPENAI_API_KEY` |
| "No results found" | Query too specific | Try semantic search or escalate |
| "Failed to build AST graph" | No Python files | Check path contains `.py` files |

---

## Best Practices for Agents

### Minimize API Calls

**Don't:**
```python
for symbol in symbols:
    search_codebase(symbol)  # Multiple calls
```

**Do:**
```python
search_codebase(" ".join(symbols), top_k=20)  # Single call
```

### Use Auto-Pilot

**Don't:**
```python
if looks_like_symbol(query):
    search_codebase(query, keyword_only=True)
else:
    search_codebase(query)
```

**Do:**
```python
search_codebase(query)  # Auto-Pilot handles it
```

### Respect Guardrails

**Don't:**
```python
process_task("fix")  # Will be rejected
```

**Do:**
```python
process_task("Fix login error in auth.py line 45")  # Accepted
```

### Check Status Appropriately

**Don't:**
```python
while True:
    get_status()  # Tight loop
    time.sleep(0.1)
```

**Do:**
```python
get_status()  # Check once
# Wait for user feedback or next action
```

---



