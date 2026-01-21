# Memory Lifecycle Workflow

> **Usage**: Follow this protocol to prevent memory bloat while keeping knowledge accessible.

## Tiers
- **`active/`**: Current. Max ~10 files. High detail.
- **`archive/`**: Historical. Monthly summaries. Low detail.

## Protocol: "Consolidate & Prune"

### 1. Task Start
Create a file in `active/` for significant tasks:
```
docs/ai/memory/active/task_<short_name>.md
```

### 2. Task End
Update the file with a **Resolution** section.

### 3. Refresh (Weekly/Sprint Boundary)
When `active/` exceeds 10 files:
1.  Parse all completed tasks.
2.  Extract key learnings (errors, fixes, decisions).
3.  Append to `archive/<YYYY_MM>_summary.md`.
4.  **Delete** the original task files from `active/`.

## Permanent Files (Never Delete)
- `00_MASTER_PLAN.md`: Strategic roadmap.
- `PostgreSQL Error Knowledge`: Database-backed diagnostic knowledge base accessible via `diagnose_error`.
