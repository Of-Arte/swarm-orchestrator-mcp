# Performance

Benchmarks, comparisons, and optimization guide for Project Swarm.

## Search Performance Benchmarks

**Test Environment:** 36 Python files, 169 chunks, 5 semantic queries

| Search Mode | Avg Time | Indexing Time | Best For |
|-------------|----------|---------------|----------|
| **Swarm Keyword** | ~1ms ⚡ | 0.2s | Exact symbols, debugging |
| **Swarm Semantic (API)** | ~240ms | 45s | Conceptual queries, exploration |
| **Swarm Semantic (Local)** | ~50-100ms | 60-120s | Offline, no API costs |
| **Ripgrep** (Antigravity default) | ~10-50ms | None | No setup, regex support |

---

## Detailed Benchmarks

### Keyword Search

```
Query: "UserModel"
Time: 0.8ms
Results: 3 exact matches
Method: Hash-based index lookup
```

### Semantic Search (Gemini API)

```
Query: "authentication logic"
Time: 243ms
Results: 8 conceptually related chunks
Method: Vector similarity (cosine)
Breakdown:
  - API call: 215ms
  - Vector search: 28ms
```

### Semantic Search (Local)

```
Query: "authentication logic"
Time: 87ms
Results: 8 conceptually related chunks
Method: Local sentence-transformers
Breakdown:
  - Embedding generation: 62ms
  - Vector search: 25ms
```

### HippoRAG Retrieval

```
Query: "database layer"
Time: 1.2s
Results: 10 ranked chunks
Method: AST graph + Personalized PageRank
Breakdown:
  - AST parsing: 450ms
  - Graph construction: 380ms
  - PageRank: 320ms
  - Ranking: 50ms
```

---

## Swarm vs Ripgrep Comparison

| Aspect | Swarm Keyword | Swarm Semantic | Ripgrep |
|--------|---------------|----------------|---------|
| **Speed** | ⚡ ~1ms | ~240ms | ~10-50ms |
| **Setup** | Index once | Index + API | None |
| **Semantic Understanding** | ❌ | ✅ | ❌ |
| **Regex Support** | ❌ | ❌ | ✅ |
| **Offline** | ✅ | ❌ (API) / ✅ (Local) | ✅ |
| **Auto-Optimization** | ✅ | ✅ | ❌ |

**Key Insight:** Swarm's keyword search is faster than ripgrep after indexing. Semantic search is slower but finds conceptually related code that keyword search misses.

---

## Auto-Pilot Performance Impact

**Without Auto-Pilot (Manual):**
```
Agent calls: search_codebase("UserModel")
Execution: Semantic search (240ms)
Result: Correct, but slow
```

**With Auto-Pilot (Automatic):**
```
Agent calls: search_codebase("UserModel")
Execution: Auto-detects symbol → Keyword search (1ms)
Result: Correct, 240x faster
```

**Impact:** 99.6% time savings for symbol queries

---

## Indexing Performance

### Keyword-Only (No Embeddings)

```
Files: 36 Python files
Chunks: 169
Time: 0.21s
Storage: 45KB (JSON)
```

### Gemini API Embeddings

```
Files: 36 Python files
Chunks: 169
Time: 47s
Breakdown:
  - File parsing: 2s
  - API calls (batched): 43s
  - Index creation: 2s
Storage: 2.1MB (JSON + vectors)
```

### OpenAI API Embeddings

```
Files: 36 Python files
Chunks: 169
Time: 49s
Breakdown:
  - File parsing: 2s
  - API calls (batched): 45s
  - Index creation: 2s
Storage: 3.4MB (JSON + vectors)
```

### Local Embeddings

```
Files: 36 Python files
Chunks: 169
Time: 94s
Breakdown:
  - File parsing: 2s
  - Model loading: 12s (first run only)
  - Embedding generation: 78s
  - Index creation: 2s
Storage: 1.8MB (JSON + vectors)
First run: +400MB model download
```

---

## Scaling Characteristics

### Small Codebase (<100 files)

- **Keyword search:** <5ms
- **Semantic search:** ~240ms
- **Indexing:** <10s (API), <60s (local)

### Medium Codebase (100-1000 files)

- **Keyword search:** ~10ms
- **Semantic search:** ~300ms
- **Indexing:** ~2min (API), ~5min (local)

### Large Codebase (1000-10000 files)

- **Keyword search:** ~50ms
- **Semantic search:** ~400ms
- **Indexing:** ~15min (API), ~30min (local)

**Recommendation:** For >10k files, index subdirectories separately or use keyword-only mode.

---

## Optimization Strategies

### 1. Use Auto-Pilot

**Impact:** 240x speedup for symbol queries

**How:** Just call `search_codebase(query)` without flags. Auto-Pilot handles optimization automatically.

### 2. Choose Right Provider

| Priority | Provider | Reason |
|----------|----------|--------|
| Speed | Gemini/OpenAI | Fastest semantic search (~240ms) |
| Offline | Local | No API calls, ~50-100ms |
| Cost | Keyword-only | Free, ~1ms |

### 3. Optimize top_k

```python
# Fast: Fewer results
search_codebase(query, top_k=3)  # ~200ms

# Slower: More results
search_codebase(query, top_k=20)  # ~280ms
```

**Recommendation:** Use `top_k=5` (default) for most queries.

### 4. Cache Index

- Index persists in `.swarm-cache/`
- No need to re-index unless files change
- Saves 0.2s-120s per session

### 5. Use Escalation Pattern

```python
# Start fast
results = search_codebase(query)  # ~1ms or ~240ms

# Escalate only if needed
if len(results) <= 2:
    results = retrieve_context(query)  # ~1s
```

---

## Memory Usage

### Keyword-Only

```
Index: ~1MB per 1000 chunks
Runtime: ~50MB base Python
Total: ~100MB
```

### With Embeddings (API)

```
Index: ~10MB per 1000 chunks
Runtime: ~50MB base Python
Total: ~150MB
```

### With Embeddings (Local)

```
Index: ~10MB per 1000 chunks
Model: ~400MB (sentence-transformers)
Runtime: ~1GB (model in memory)
Total: ~1.5GB
```

---

## Network Usage

### Gemini API

```
Per chunk: ~500 bytes request, ~3KB response
Per 1000 chunks: ~3.5MB total
```

### OpenAI API

```
Per chunk: ~600 bytes request, ~6KB response
Per 1000 chunks: ~6.6MB total
```

### Local

```
No network usage (fully offline)
```

---

## Cost Analysis

### Gemini

```
Free tier: 60 requests/minute
Cost (paid): ~$0.0001 per chunk
1000 chunks: ~$0.10
```

### OpenAI

```
Cost: $0.02 per 1M tokens
1000 chunks (~500 tokens each): ~$0.01
```

### Local

```
Cost: $0 (one-time 400MB download)
```

---

## Real-World Performance

### Example: "authentication" Query

**Keyword search:**
```
Time: 0.9ms
Finds: "authentication" (exact match)
Misses: OAuth2Handler, JWTValidator (conceptually related)
```

**Semantic search:**
```
Time: 238ms
Finds:
  - "authentication" (exact match)
  - OAuth2Handler (conceptually related)
  - JWTValidator (conceptually related)
  - session_manager (conceptually related)
```

**Trade-off:** 264x slower, but 4x more comprehensive results.

---

## Bottleneck Analysis

### Keyword Search

**Bottleneck:** Index size  
**Solution:** Shard index for >100k chunks

### Semantic Search (API)

**Bottleneck:** API latency  
**Solution:** Batch requests, use local for offline

### Semantic Search (Local)

**Bottleneck:** CPU for embedding generation  
**Solution:** Use GPU if available, or switch to API

### HippoRAG

**Bottleneck:** AST parsing for large files  
**Solution:** Cache AST graphs, limit file size

---

## Benchmark Script

Run your own benchmarks:

```bash
python benchmark_search.py
```

**Output:**
```
=== Swarm Search Benchmark ===

Keyword Search:
  Avg: 1.2ms
  Min: 0.8ms
  Max: 2.1ms

Semantic Search (API):
  Avg: 243ms
  Min: 215ms
  Max: 287ms

Semantic Search (Local):
  Avg: 87ms
  Min: 76ms
  Max: 102ms

HippoRAG Retrieval:
  Avg: 1.18s
  Min: 0.95s
  Max: 1.42s
```

---

## Optimization Checklist

- [ ] Use Auto-Pilot for symbol queries
- [ ] Choose appropriate provider (API for speed, local for offline)
- [ ] Set reasonable `top_k` (5-10 for most queries)
- [ ] Cache index (don't re-index unnecessarily)
- [ ] Use escalation pattern (search → retrieve_context)
- [ ] Batch operations when possible
- [ ] Monitor memory usage for large codebases

---

## Next Steps

- **[Configuration](configuration.md)** - Provider setup and tuning
- **[User Guide](user-guide.md)** - Feature walkthrough
- **[API Reference](api-reference.md)** - Tool specifications
