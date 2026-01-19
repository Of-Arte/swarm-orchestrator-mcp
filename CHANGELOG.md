# Changelog

All notable changes to Project Swarm will be documented in this file.

## [3.0.2] - 2026-01-19

### Changed
- **Documentation Restructure**: Reorganized documentation into professional open-source structure
  - New concise `README.md` (150 lines vs 599) as GitHub landing page
  - Created `docs/human/` for developer documentation (getting-started, user-guide, architecture, API reference, configuration, performance, contributing)
  - Created `docs/ai/` for AI agent documentation (agent-guide, tool-reference, examples)
  - Separated concerns: humans get tutorials, AI agents get optimized specs
  - All documentation updated to reflect v3.0.1 Active Governance features
- **MCP Resources**: Updated resource paths and added new comprehensive endpoints
  - Added `swarm://docs/ai/guide`, `swarm://docs/ai/tools`, `swarm://docs/ai/examples`
  - Added `swarm://docs/getting-started`, `swarm://docs/user-guide`, `swarm://docs/api-reference`, `swarm://docs/configuration`, `swarm://docs/performance`
  - Updated `swarm://docs/architecture` to point to `docs/human/architecture.md`
  - Kept `swarm://docs/ai` (legacy ai.txt) for backwards compatibility

---

## [3.0.1] - 2026-01-19

### Enhanced
- **Auto-Pilot Search**: `search_codebase` now *automatically* executes keyword search for symbol queries (e.g. `UserModel`), falling back to semantic search only if needed. Optimized for speed (~1ms).
- **Task Guardrails**: `process_task` now rejects vague/short instructions (`< 3 words`) to encourage better prompting and prevent wasted agent cycles.
- **Fallback Guidance**: Keyword-only searches with no results suggest trying semantic search.
- **Escalation Tips**: Sparse semantic results trigger `retrieve_context()` suggestions.

### Technical
- Implemented `Auto-Pilot` logic: Symbol detection triggers eager keyword search.
- Implemented `Input Guardrails`: Pre-flight validation for task instructions.
- Improved agent decision reliability to near 100% for symbol searches (enforced).

---

## [3.1.0] - 2026-01-19

### 🎯 Enhanced: Comprehensive Tool Heuristics

Added decision heuristics to all MCP tools to help AI agents make optimal performance and capability trade-offs.

### Added

- **MCP Resources** (agent-discoverable documentation)
  - `swarm://docs/ai` - Agent guidance file
  - `swarm://docs/architecture` - Project structure
  - `swarm://docs/changelog` - Version history

- **ai.txt Agent Guidance File**
  - Cross-tool navigation: when to use Swarm vs Antigravity built-in
  - Decision flowcharts for search and modification workflows
  - Performance reference table for all tools
  - Multi-tool workflow examples

- **Agent Integration Guide** in README
  - Tool selection flowchart (keyword vs semantic vs deep analysis)
  - Performance comparison table with exact timings
  - Best practices for each tool

- **search_codebase Heuristics**
  - Smart query detection: auto-identify symbols vs concepts
  - Performance guide: ~1ms keyword vs ~240ms semantic
  - Clear examples: when to use `keyword_only=True`

- **index_codebase Heuristics**
  - Provider comparison: auto/gemini/openai/local with timing
  - Re-indexing criteria: when to (>10 files) vs when not to
  - Cost information for each provider

- **retrieve_context Heuristics**
  - Escalation guide: when to upgrade from search_codebase
  - Comparison table: speed, depth, method, languages
  - Workflow examples: search → escalate pattern

- **process_task Heuristics**
  - Task routing guide showing algorithm triggers
  - Best practices: specific instructions with context
  - Examples for refactor/debug/verify/merge/analyze patterns

### Changed

- **Benchmark Accuracy**
  - Replaced misleading "152x faster" claim
  - Added honest comparison vs ripgrep (Antigravity's actual tool)
  - Included local embeddings speed data (~50-100ms)
  - Updated benchmark script to test all modes

## [3.0.0] - 2026-01-18

### 🚀 Major: Algorithmic Blackboard Upgrade

Tranformed Swarm from a standard LLM orchestrator to an **Algorithmic Blackboard** with 7 specialized deterministic workers.

### Added

- **7 New Algorithm Workers** (`mcp_core/algorithms/`)
  - **HippoRAG:** AST-based graph retrieval with PageRank.
  - **OCC Validator:** Optimistic Concurrency Control for atomic file writes.
  - **CRDT Merger:** Conflict-Free Replicated Data Types for concurrent edits.
  - **Weighted Voting:** Consensus engine with Elo ratings.
  - **Debate Engine:** Sparse-topology debate system.
  - **Z3 Verifier:** Formal verification using SMT solver.
  - **Ochiai Localizer:** Automated fault localization (SBFL).

- **New CLI Commands** (`orchestrator.py`)
  - `retrieve <query>`: Deep context retrieval via HippoRAG.
  - `debug --test-cmd`: Auto-locate bugs in failing tests.
  - `verify <func>`: Generate Z3 verification guides.
  - `benchmark`: Validate 3x velocity improvements.

- **Comprehensive Test Suite** (`tests/algorithms/`)
  - ~80 new tests covering all algorithm workers.
  - 95% coverage target.

### Changed

- **Task Dispatch:** `Orchestrator` now routes tasks to algorithms based on flags (`context_needed`, `conflicts_detected`, etc.) before falling back to LLM agents.
- **Project Structure:** Moved core logic to `mcp_core/` with dedicated `algorithms/` submodule.

## [2.1.0] - 2026-01-01

- **Python-Native Search Engine**
  - Replaced Node.js search with pure Python implementation.
  - Added Hybrid Search (Semantic + Keyword).

## [2.0.0] - Previous

- Node.js MCP server architecture.
- Initial Python orchestrator prototype.
