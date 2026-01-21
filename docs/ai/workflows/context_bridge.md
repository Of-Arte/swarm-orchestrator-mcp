---
description: How to bridge context between conversations using artifacts.
---

# Context Bridge Workflow

This workflow describes how to preserve high-quality context across different AI sessions.

## 1. Closing a Session (Archiving)
When a major task is completed:

1.  **Synthesize, Don't Duplicate**: 
    - Do NOT copy full artifacts if they are already accessible. 
    - Instead, create a **Synthesis Note** in `docs/ai/memory/`.
    - Summarize key decisions, architectural changes, or "gotchas".
2.  **Naming**: `YYYY-MM-DD_Topic_Summary.md`
3.  **Update Loader**:
    - Edit `docs/ai/PLAN.md`.
    - Update the **Current Focus** and **Search Triggers** for the NEXT session.

## 2. Opening a Session (Restoring)
When starting a new conversation:

1.  **Read Dashboard**:
    Always start by reading `docs/ai/PLAN.md`.
2.  **Retrieve Context**:
    If specific details are needed, follow the links in "Recent Context" or use the `search_codebase` tool with queries related to the topic (e.g., "search engine refactor plan").
    *Note: `index_codebase` might need to be run if the memory files were just added.*

## 3. Maintenance
- Periodically archive older "Recent Context" items in `PLAN.md` to a separate `docs/ai/memory/ARCHIVE.md` list to keep the dashboard clean.
