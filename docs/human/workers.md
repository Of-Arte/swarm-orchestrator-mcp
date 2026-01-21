# Swarm Workers & Algorithms

Comprehensive guide to Project Swarm's specialized algorithm workers and their capabilities.

---

## Table of Contents

1. [Overview](#overview)
2. [Ochiai SBFL](#ochiai-sbfl) - Fault Localization
3. [Z3 Verifier](#z3-verifier) - Formal Verification
5. [HippoRAG](#hipporag) - Context Retrieval
6. [Autonomous Git Worker Team](#autonomous-git-worker-team) - Autonomous Version Control
7. [Worker Routing](#worker-routing)

---

## Overview

Swarm uses **specialized algorithm workers** to handle complex software engineering tasks. Each worker implements a specific algorithm optimized for a particular problem domain.

### Worker Selection

Workers are automatically selected based on instruction patterns:

| Instruction Pattern | Worker | Algorithm |
|---------------------|--------|-----------|

| "debug...", "why is failing..." | Ochiai SBFL | Spectrum-Based Fault Localization |
| "verify...", "prove..." | Z3 Verifier | Symbolic Execution |
| "merge...", "combine..." | CRDT Merger | Conflict-Free Replicated Data Types |
| "analyze...", "understand..." | HippoRAG | Knowledge Graph + PageRank |

---



## Ochiai SBFL

**Spectrum-Based Fault Localization** - Automated bug location using test coverage.

### What It Does

Ranks lines of code by **suspiciousness score** based on which lines are executed by failing vs passing tests.

### Algorithm Theory

**Ochiai Formula**:
```
S(line) = failed(line) / sqrt(total_failed * (failed(line) + passed(line)))
```

Where:
- `failed(line)`: Number of failing tests that execute this line
- `passed(line)`: Number of passing tests that execute this line
- `total_failed`: Total number of failing tests

**Score Range**: 0.0 (least suspicious) to 1.0 (most suspicious)

### When to Use

✅ **Use Ochiai SBFL when:**
- Tests are failing but root cause is unclear
- Large codebase with complex call graphs
- Need to narrow down debugging scope

❌ **Don't use for:**
- No test suite exists
- All tests passing (no failures to analyze)
- Syntax errors (use linter instead)

### Example Usage

```python
from mcp_core.algorithms import OchiaiLocalizer

localizer = OchiaiLocalizer()

# Run full SBFL analysis
debug_prompt = localizer.run_full_sbfl_analysis(
    test_command="pytest tests/",
    source_path="src/",
    top_k=5
)

print(debug_prompt)
```

**Output**:
```
🔍 Top 5 Suspicious Lines:

1. auth/handlers.py:67 (score: 0.95)
   if user.password == password:  # ⚠️ Plain text comparison

2. auth/models.py:23 (score: 0.87)
   self.token = generate_token()

3. database/query.py:145 (score: 0.72)
   cursor.execute(f"SELECT * FROM {table}")  # SQL injection
```

### Requirements

- **Python**: `coverage>=7.0` package
- **Test Suite**: Must have both passing and failing tests
- **Source Code**: Must be instrumented by coverage.py

### Performance

- **Coverage Collection**: ~5-30s (depends on test suite size)
- **Suspiciousness Calculation**: ~100-500ms
- **Total**: ~5-30s for typical project

---

## Z3 Verifier

**Symbolic Execution** - Proves that code satisfies contracts for ALL possible inputs.

### What It Does

Uses the **Z3 SMT Solver** to verify that postconditions hold for every input satisfying preconditions, not just sampled test cases.

### Algorithm Theory

**Symbolic Execution**:
```python
# Instead of testing concrete values:
assert calculate_tax(100) == 10  # Only tests one case

# Z3 verifies for ALL values:
x = z3.Int('amount')
result = calculate_tax_symbolic(x)
z3.prove(z3.Implies(x >= 0, result >= 0))  # Proves for infinite inputs
```

**SMT Solving**:
- Converts code to logical constraints
- Searches for counterexamples (inputs that violate postconditions)
- If no counterexample exists → **verified**

### When to Use

✅ **Use Z3 Verifier when:**
- Critical invariants must hold (e.g., "balance never negative")
- Testing all edge cases is infeasible
- Formal proof required (security, finance, safety)

❌ **Don't use for:**
- Complex algorithms (Z3 may timeout)
- Floating-point arithmetic (imprecise)
- I/O-heavy code (not symbolic)

### Example Usage

```python
from mcp_core.algorithms import Z3Verifier, create_symbolic_int
import z3

verifier = Z3Verifier(timeout_ms=5000)

# Define symbolic variables
amount = create_symbolic_int("amount")
rate = create_symbolic_int("rate")

# Preconditions
preconditions = [
    amount >= 0,
    rate >= 0,
    rate <= 100
]

# Implementation (symbolic)
def calculate_tax_symbolic(vars):
    return vars["amount"] * vars["rate"] / 100

# Postcondition
result = calculate_tax_symbolic({"amount": amount, "rate": rate})
postconditions = [result >= 0]  # Tax never negative

# Verify
verification = verifier.verify_function(
    func=calculate_tax_symbolic,
    preconditions=preconditions,
    postconditions=postconditions
)

if verification.verified:
    print("✅ Verified: Tax is always non-negative")
else:
    print(f"❌ Counterexample: {verification.counterexample}")
```

**Counterexample Output**:
```python
{
    "amount": -10,  # Violates precondition, but shows edge case
    "rate": 50
}
```

### Limitations

- **Timeout**: Complex constraints may not solve in 5s
- **Scalability**: Works best for functions with <10 branches
- **Precision**: Integer arithmetic only (no floats)

### Performance

- **Simple Functions**: ~10-100ms
- **Medium Complexity**: ~500ms-2s
- **Complex**: May timeout (5s default)

---



## HippoRAG

**Knowledge Graph Retrieval** - Finds related code using AST graphs and Personalized PageRank.

### What It Does

Builds a **knowledge graph** from code structure (function calls, imports, inheritance) and uses **Personalized PageRank** to find architecturally related code.

**Multi-Language Support**: HippoRAG now supports multiple programming languages via parser plugins:
- ✅ **Python** (built-in, always available)
- ✅ **JavaScript/TypeScript** (optional, requires Tree-sitter packages)
- 🔮 **Future**: Go, Rust, Java (plugin system ready)

### Algorithm Theory

**Graph Construction**:
```
Nodes: Functions, Classes, Modules, Interfaces (TS), Types (TS)
Edges: Calls, Imports, Inheritance, Implements
```

**Personalized PageRank (PPR)**:
```
PPR(node) = (1 - α) * seed_weight + α * Σ(PPR(neighbor) / out_degree(neighbor))
```

Where:
- `α = 0.85` (damping factor)
- `seed_weight`: 1.0 for query matches, 0.0 otherwise

**Ranking**: Nodes with high PPR scores are structurally central to the query.

### When to Use

✅ **Use HippoRAG when:**
- Understanding code architecture
- Finding ALL code related to a feature (multi-hop reasoning)
- Refactoring requires full dependency context
- Analyzing polyglot codebases (Python + JS/TS)

❌ **Don't use for:**
- Simple function lookups (use `search_codebase` instead)
- Unsupported languages (unless you add a parser plugin)
- Quick questions (slower than semantic search)

### Enabling Multi-Language Support

**Python Only** (default, no extra dependencies):
```python
from mcp_core.algorithms import HippoRAGRetriever

retriever = HippoRAGRetriever()
# Automatically uses built-in Python AST parser
retriever.build_graph_from_ast(".")
```

**JavaScript/TypeScript** (requires optional packages):
```bash
# Install Tree-sitter packages
pip install tree-sitter tree-sitter-javascript tree-sitter-typescript
```

```python
retriever = HippoRAGRetriever()
# Automatically detects and loads JS/TS parsers if installed
# INFO: Multi-language support enabled: JavaScript, TypeScript

# Build graph from all supported languages
retriever.build_graph_from_ast(".")  # Auto-detects .py, .js, .ts, .tsx

# Or specify extensions manually
retriever.build_graph_from_ast(".", extensions=[".py", ".ts"])
```

### Example Usage

```python
from mcp_core.algorithms import HippoRAGRetriever

retriever = HippoRAGRetriever()

# Build graph from AST
retriever.build_graph_from_ast(".", extensions=[".py"])

print(f"Graph: {retriever.graph.number_of_nodes()} nodes, {retriever.graph.number_of_edges()} edges")

# Retrieve context
chunks = retriever.retrieve_context("authentication flow", top_k=10)

for chunk in chunks:
    print(f"{chunk.node_type} {chunk.node_name} (PPR: {chunk.ppr_score:.4f})")
    print(f"  {chunk.file_path}:{chunk.start_line}-{chunk.end_line}")
```

**Output**:
```
function handle_oauth_callback (PPR: 0.8734)
  auth/handlers.py:45-67

class OAuthProvider (PPR: 0.8123)
  auth/models.py:12-28

function validate_token (PPR: 0.7456)
  auth/utils.py:89-102
```

### Comparison: HippoRAG vs Semantic Search

| Aspect | Semantic Search | HippoRAG |
|--------|-----------------|----------|
| Speed | ~240ms | ~500-2000ms |
| Depth | Surface-level | Architectural |
| Method | Embeddings | AST + Graph |
| Languages | All | Python only |
| Use for | Quick lookups | Deep analysis |

### Performance

- **Graph Build**: ~500ms-2s (depends on codebase size)
- **PPR Computation**: ~100-500ms
- **Total**: ~1-3s for typical project

---

## Autonomous Git Worker Team

**Autonomous Version Control** - Semantically meaningful commits and PR management.

### What It Does

The Git Worker is a background autonomous agent that:
1.  **Monitors** the file system for changes ("dirty state").
2.  **Diffs** the changes to understand *what* happened.
3.  **Generates** a Conventional Commit message using `gemini-3-flash-preview` (high speed).
4.  **Commits** the changes (if `git_auto_commit` is enabled).

### Workflow

```mermaid
graph LR
    Diff[File Change] --> Detect{GitManager}
    Detect -- "Has Changes" --> LLM[Gemini-3-Flash]
    LLM -- "Draft Message" --> Commit[Git Commit]
    Commit -- "Push?" --> Remote[GitHub]
```

### Configuration

Controlled via `project_profile.json` or `process_task` commands:

```python
# Enable/Disable
process_task("Enable autonomous git commits")

# Manual Trigger
process_task("Commit these changes with message 'Refactor auth'")
```

### Models

- **Git Writer**: Defaults to `gemini-3-flash-preview` for sub-2s latency on commit message generation.

---

## Worker Routing

### Automatic Selection

Swarm analyzes instruction patterns to route tasks:

```python
# server.py - Routing logic

        return "Ochiai SBFL"
    elif re.search(r'\b(verify|prove|ensure)\b', instruction, re.I):
        return "Z3 Verifier"
    elif re.search(r'\b(analyze|understand|explore)\b', instruction, re.I):
        return "HippoRAG"
    else:
        return "General Worker"
```

### Manual Override

You can explicitly request a worker:

```python
process_task("Use SBFL: Debug login failure in test_auth.py")
process_task("Use Z3: Verify calculate_tax never returns negative")
```

### Multi-Worker Tasks

Complex tasks may use multiple workers:

```
1. HippoRAG → Find all authentication code
2. General Worker → Refactor
3. Ochiai SBFL → Debug any test failures
4. Z3 Verifier → Verify security invariants
```

---

## Best Practices

### 1. Choose the Right Worker

| Goal | Worker | Why |
|------|--------|-----|

| Find bugs | Ochiai SBFL | Coverage analysis |
| Prove correctness | Z3 Verifier | Formal methods |

| Understand architecture | HippoRAG | Graph traversal |

### 2. Combine Workers

```python
# Example: Refactor with verification
process_task("Refactor auth.py to use async/await")  # General Worker
process_task("Verify auth.py never leaks credentials")  # Z3
process_task("Debug any failing auth tests")  # SBFL
```

### 3. Understand Limitations


- **SBFL**: Requires test suite
- **Z3**: Limited to simple functions

- **HippoRAG**: Python AST only

---

## Next Steps

- **[User Guide](user-guide.md)** - How to use Swarm tools
- **[API Reference](api-reference.md)** - Detailed tool specifications
- **[Performance](performance.md)** - Benchmarks and optimization
