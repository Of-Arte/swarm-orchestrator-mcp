---
description: How to autonomously manage, solve, and submit GitHub issues as an agent.
---

# 🤖 Observable Issue Management Workflow

This workflow defines the loop for an AI agent to maintain the repository using the Swarm's **Memory-Centric** approach. It is designed to be **fully transparent**, allowing a human user to observe progress in real-time via the IDE's task view and artifact system.

## 1. Detection & "Task" Initialization
- **Action:** Scan for issues (CodeQL, TODOs, search).
- **Communication:** Create/Update `docs/ai/memory/active/task.md`. This is the user's "Dashboard" in the IDE.
- **Rule:** Every autonomous session must have a task list. A human should be able to see exactly what is queued.

## 2. Planning "Artifact" Creation
- **Action:** Create `docs/ai/memory/active/implementation_plan.md`.
- **Requirements:** Must group files by component, define a verification plan, and list specific gates to run.
- **Agent Rule:** Always assign yourself to the GitHub issue (`assign_copilot_to_issue`) only AFTER your plan is drafted.

## 3. Execution & Memory Logging
- **Action:** Follow the plan to modify the codebase.
- **Action:** Record non-obvious insights into `docs/ai/memory/active/task.md` or dedicated insight logs as they occur.
- **Gate:** Use `validate_all.py` before any commit.

## 4. Verification & "Walkthrough" Generation
- **Action:** Create `docs/ai/memory/active/walkthrough.md`.
- **Requirements:** Must document proof of validation (test results, diffs).
- **Action:** Use `GitWorker` to commit (Conventional Commits).

## 5. Submission & Metadata Sync
- **Action:** Create Pull Request with `AGENT_METADATA` synced from the local `task.md`.
- **Action:** Refresh the `Repo Nanny Dashboard`.
- **Final Step:** Run `memory-refresh` skill to move artifacts to archive.
