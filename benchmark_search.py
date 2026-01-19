"""
Swarm Search Benchmark: Accurate Comparison

This benchmark compares:
1. Swarm Keyword Search (indexed, ~1ms)
2. Swarm Semantic Search - API (Gemini/OpenAI, ~200-300ms)
3. Swarm Semantic Search - Local (sentence-transformers, varies)
4. Ripgrep (Antigravity's default, ~10-50ms)

Metrics measured:
- Indexing Time
- Search Latency
- Result Quality (semantic understanding)
"""

import time
import subprocess
import shutil
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from mcp_core.search_engine import (
    CodebaseIndexer,
    HybridSearch,
    IndexConfig,
    get_embedding_provider,
)


# ============================================================================
# Test Queries
# ============================================================================

TEST_QUERIES = [
    "authentication logic",
    "database models",
    "error handling",
    "user management",
    "search implementation",
]


# ============================================================================
# Ripgrep Benchmark (Antigravity's actual default)
# ============================================================================

def benchmark_ripgrep(queries: List[str]) -> Dict[str, Any]:
    """Benchmark ripgrep - Antigravity's actual search tool."""
    print("\n" + "=" * 60)
    print("RIPGREP BENCHMARK (Antigravity's Default)")
    print("=" * 60)
    
    # Check if ripgrep is available
    rg_path = shutil.which("rg")
    if not rg_path:
        print("⚠ ripgrep not found, skipping...")
        return {"avg_query_time_ms": None, "available": False}
    
    print(f"✓ Using ripgrep: {rg_path}")
    
    query_times = []
    results_summary = []
    
    for query in queries:
        start_search = time.time()
        
        try:
            # Run ripgrep with case-insensitive search
            result = subprocess.run(
                ["rg", "-i", "-l", "--type", "py", query, "."],
                capture_output=True,
                text=True,
                timeout=10
            )
            match_files = [f for f in result.stdout.strip().split("\n") if f]
        except subprocess.TimeoutExpired:
            match_files = []
        except Exception as e:
            print(f"  ✗ Error: {e}")
            match_files = []
        
        search_time = time.time() - start_search
        query_times.append(search_time)
        
        print(f"\n  Query: '{query}'")
        print(f"  Time: {search_time*1000:.1f}ms | Files: {len(match_files)}")
        
        if match_files:
            print(f"  Top Result: {Path(match_files[0]).name}")
        
        results_summary.append({
            "query": query,
            "time_ms": search_time * 1000,
            "num_files": len(match_files),
        })
    
    avg_query_time = sum(query_times) / len(query_times) if query_times else 0
    
    print(f"\n  Avg Query Time: {avg_query_time*1000:.1f}ms")
    
    return {
        "avg_query_time_ms": avg_query_time * 1000,
        "results": results_summary,
        "available": True,
    }


# ============================================================================
# Swarm Search Benchmark
# ============================================================================

def benchmark_swarm_keyword(queries: List[str], indexer: CodebaseIndexer) -> Dict[str, Any]:
    """Benchmark Swarm keyword-only search (no embeddings)."""
    print("\n" + "=" * 60)
    print("SWARM KEYWORD SEARCH (Indexed)")
    print("=" * 60)
    
    searcher = HybridSearch(indexer, provider=None)
    query_times = []
    
    for query in queries:
        start_search = time.time()
        results = searcher.keyword_search(query, top_k=3)
        search_time = time.time() - start_search
        query_times.append(search_time)
        
        print(f"\n  Query: '{query}'")
        print(f"  Time: {search_time*1000:.1f}ms | Results: {len(results)}")
        
        if results:
            file_name = Path(results[0].file_path).name
            print(f"  Top Result: {file_name}:{results[0].start_line}")
    
    avg_query_time = sum(query_times) / len(query_times) if query_times else 0
    print(f"\n  Avg Query Time: {avg_query_time*1000:.1f}ms")
    
    return {"avg_query_time_ms": avg_query_time * 1000}


def benchmark_swarm_semantic(
    queries: List[str], 
    indexer: CodebaseIndexer, 
    provider_type: str
) -> Dict[str, Any]:
    """Benchmark Swarm semantic search with specified provider."""
    provider_name = provider_type.upper()
    print("\n" + "=" * 60)
    print(f"SWARM SEMANTIC SEARCH ({provider_name})")
    print("=" * 60)
    
    try:
        provider = get_embedding_provider(provider_type)
        print(f"✓ Using: {type(provider).__name__}")
    except Exception as e:
        print(f"⚠ {provider_name} unavailable: {e}")
        return {"avg_query_time_ms": None, "available": False}
    
    # Re-index with embeddings if needed
    has_embeddings = any(c.embedding is not None for c in indexer.chunks)
    if not has_embeddings:
        print("  Generating embeddings...")
        start_embed = time.time()
        indexer.index_all(provider=provider)
        embed_time = time.time() - start_embed
        print(f"  Embedding time: {embed_time:.1f}s")
    
    searcher = HybridSearch(indexer, provider=provider)
    query_times = []
    
    for query in queries:
        start_search = time.time()
        results = searcher.search(query, top_k=3)
        search_time = time.time() - start_search
        query_times.append(search_time)
        
        print(f"\n  Query: '{query}'")
        print(f"  Time: {search_time*1000:.1f}ms | Results: {len(results)}")
        
        if results:
            file_name = Path(results[0].file_path).name
            print(f"  Top Result: {file_name}:{results[0].start_line} (score: {results[0].score:.3f})")
    
    avg_query_time = sum(query_times) / len(query_times) if query_times else 0
    print(f"\n  Avg Query Time: {avg_query_time*1000:.1f}ms")
    
    return {"avg_query_time_ms": avg_query_time * 1000, "available": True}


# ============================================================================
# Main Benchmark Runner
# ============================================================================

def main():
    """Run comprehensive benchmark comparison."""
    print("\n" + "🔍 SWARM SEARCH BENCHMARK v2.0".center(60) + "\n")
    print("Accurate comparison against Antigravity's ripgrep")
    print("=" * 60)
    
    # Step 1: Index codebase (keyword-only first)
    print("\n[1/5] Indexing codebase (keyword-only)...")
    config = IndexConfig(root_path=".", chunk_size=50, chunk_overlap=10)
    indexer = CodebaseIndexer(config)
    
    start_index = time.time()
    indexer.index_all(provider=None)
    keyword_index_time = time.time() - start_index
    print(f"✓ Indexed {len(indexer.chunks)} chunks in {keyword_index_time:.2f}s")
    
    # Step 2: Benchmark ripgrep
    print("\n[2/5] Benchmarking ripgrep...")
    ripgrep_results = benchmark_ripgrep(TEST_QUERIES)
    
    # Step 3: Benchmark Swarm keyword search
    print("\n[3/5] Benchmarking Swarm keyword search...")
    keyword_results = benchmark_swarm_keyword(TEST_QUERIES, indexer)
    
    # Step 4: Benchmark Swarm semantic (API)
    print("\n[4/5] Benchmarking Swarm semantic (API)...")
    api_results = {"avg_query_time_ms": None, "available": False}
    if os.environ.get("GEMINI_API_KEY"):
        api_results = benchmark_swarm_semantic(TEST_QUERIES, indexer, "gemini")
    elif os.environ.get("OPENAI_API_KEY"):
        api_results = benchmark_swarm_semantic(TEST_QUERIES, indexer, "openai")
    else:
        print("⚠ No API key set, skipping API semantic search")
    
    # Step 5: Benchmark Swarm semantic (Local)
    print("\n[5/5] Benchmarking Swarm semantic (Local)...")
    local_results = {"avg_query_time_ms": None, "available": False}
    try:
        # Force fresh indexer for local embeddings test
        local_indexer = CodebaseIndexer(config)
        local_results = benchmark_swarm_semantic(TEST_QUERIES, local_indexer, "local")
    except Exception as e:
        print(f"⚠ Local embeddings unavailable: {e}")
    
    # Print comparison
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    
    print("\n┌────────────────────────┬────────────┬─────────────────┐")
    print("│ Search Method          │ Avg Time   │ Best For        │")
    print("├────────────────────────┼────────────┼─────────────────┤")
    
    # Swarm Keyword
    kw_time = keyword_results["avg_query_time_ms"]
    print(f"│ Swarm Keyword (indexed)│ {kw_time:>7.1f}ms │ Exact symbols   │")
    
    # Ripgrep
    if ripgrep_results.get("available"):
        rg_time = ripgrep_results["avg_query_time_ms"]
        print(f"│ Ripgrep (Antigravity)  │ {rg_time:>7.1f}ms │ No index needed │")
    else:
        print("│ Ripgrep (Antigravity)  │   N/A     │ (not installed) │")
    
    # API Semantic
    if api_results.get("available"):
        api_time = api_results["avg_query_time_ms"]
        print(f"│ Swarm Semantic (API)   │ {api_time:>7.1f}ms │ Concepts        │")
    else:
        print("│ Swarm Semantic (API)   │   N/A     │ (no API key)    │")
    
    # Local Semantic
    if local_results.get("available"):
        local_time = local_results["avg_query_time_ms"]
        print(f"│ Swarm Semantic (Local) │ {local_time:>7.1f}ms │ Offline use     │")
    else:
        print("│ Swarm Semantic (Local) │   N/A     │ (not installed) │")
    
    print("└────────────────────────┴────────────┴─────────────────┘")
    
    # Speed comparisons
    print("\nSpeed Comparisons:")
    if ripgrep_results.get("available") and kw_time > 0:
        speedup = ripgrep_results["avg_query_time_ms"] / kw_time
        print(f"  • Swarm Keyword vs Ripgrep: {speedup:.1f}x {'faster' if speedup > 1 else 'slower'}")
    
    print(f"\nChunks indexed: {len(indexer.chunks)}")
    print(f"Keyword index time: {keyword_index_time:.2f}s")
    
    return {
        "keyword": keyword_results,
        "ripgrep": ripgrep_results,
        "api_semantic": api_results,
        "local_semantic": local_results,
    }


if __name__ == "__main__":
    main()
