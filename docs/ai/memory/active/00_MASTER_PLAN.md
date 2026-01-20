# Swarm Project Master Plan (LTM)

> **Role**: Long-Term Memory & Roadmap
> **Usage**: Retrieve this file when you need to understand the big picture or update the core strategy.

## 🌟 Strategic Goal
Create a self-organizing, autonomous "Swarm" of AI agents capable of maintaining and evolving a codebase with minimal human intervention.

## 🗺️ Roadmap & Status

### Phase 1: Foundation (Completed)
- [x] **Orchestrator V1**: Basic loop and dispatch.
- [x] **MCP Server**: Exposed orchestrator via FastMCP (`server.py`).
- [x] **Search Engine**: Hybrid semantic/keyword search (`search_engine.py`).

### Phase 2: Context Awareness (Completed)
- [x] **Context Bridge**:
    - `PLAN.md` converted to Context Loader (RAM).
    - `docs/ai/memory/active` established as high-fidelity LTM store.
    - `docs/ai/memory/archive` established for rolling compression.
- [x] **Markdown Indexing**: Enable `.md` and `.txt` indexing for documentation retrieval.
- [x] **Transport Stability**: Migration to **Docker-based Stdio** for robust local development.

### Phase 3: Autonomy & Integration (Current)
- [x] **Rolling Memory System**: Tiered active/archive memory.
- [x] **Structured Deliberation**: `deliberate()` tool for multi-step reasoning.
- [ ] **Autonomous Git Team**: GitWorker for multi-file PRs.
- [ ] **Context Injection**: Verify `retrieve_context` (HippoRAG) works on these new memory tiers.

## 🧠 Memory Bank Index
*Keywords to use with `search_codebase` to retrieve specific memory details.*

- **Architecture**: `retrieve_context("Swarm V3 Architecture")`
- **Context Bridge**: `search_codebase("Context Bridge Workflow")`
- **Git Strategy**: `search_codebase("Git Conventional Commits")`

## 📝 Active Constraints
1.  **Duplicate Storage**: Do NOT duplicate artifacts. Synthesis only.
2.  **Server Config**: Must use `127.0.0.1` for MCP connectivity on Windows.
