import logging
import os
from pathlib import Path
from typing import List
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def orient_context(session_id: str = None) -> str:
        """
        Orient the current session using the memory systems defined in skill-memory-orient.md.
        
        Usage Heuristics:
        - Use when: Session start, context reset, or before starting a complex task.
        - Returns: A summary of the current roadmap, active tasks, and context triggers.
        
        Args:
            session_id: Optional unique identifier for the session. If provided, creates an isolated memory environment.
        """
        return _orient_context(session_id)

    @mcp.tool()
    def refresh_memory(session_id: str = None) -> str:
        """
        Consolidate and prune active memory files per skill-memory-refresh.md.
        
        Usage Heuristics:
        - Use when: Too many active task files exist (>10) or at session end.
        - Effect: Moves completed task insights to archive and deletes raw files.
        
        Args:
            session_id: Optional unique identifier for the session.
        """
        return _refresh_memory(session_id)

    @mcp.tool()
    def claim_task(session_id: str, task_description: str) -> str:
        """
        Locks a task in the Global PLAN.md to prevent overlap.
        
        Usage Heuristics:
        - Use when: Starting a task in an isolated session.
        - Effect: Marks task as in-progress in global plan with session attribution.
        """
        return _claim_task(session_id, task_description)

    @mcp.tool()
    def merge_session(session_id: str) -> str:
        """
        Syncs completed tasks from Session back to Global Plan and archives session.
        
        Usage Heuristics:
        - Use when: Session goal is complete and verified.
        - Effect: Updates global plan with completed tasks, archives session memory.
        """
        return _merge_session(session_id)

def _orient_context(session_id: str = None) -> str:
    import shutil
    import hashlib
    # Logic extracted for testability
    swarm_root = Path(__file__).parent.parent.parent.parent
    
    # Determine paths based on session_id
    if session_id:
        session_root = swarm_root / "docs" / "sessions" / session_id
        plan_path = session_root / "PLAN.md"
        active_dir = session_root / "memory" / "active"
        
        # Initialize session if not exists
        if not session_root.exists():
            session_root.mkdir(parents=True, exist_ok=True)
            active_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy global PLAN.md if it exists, else create empty
            global_plan = swarm_root / "docs" / "ai" / "PLAN.md"
            if global_plan.exists():
                shutil.copy(global_plan, plan_path)
                # Store hash for drift detection
                plan_hash = hashlib.md5(global_plan.read_bytes()).hexdigest()
                (session_root / "plan_snapshot.hash").write_text(plan_hash, encoding="utf-8")
            else:
                plan_path.write_text("# Session Plan\n", encoding="utf-8")
                
            info_header = f"🧠 Swarm Orienting Protocol Results (Session: {session_id}):\n"
        else:
            # Check for Drift
            global_plan = swarm_root / "docs" / "ai" / "PLAN.md"
            snapshot_hash_file = session_root / "plan_snapshot.hash"
            drift_warning = ""
            
            if global_plan.exists() and snapshot_hash_file.exists():
                current_hash = hashlib.md5(global_plan.read_bytes()).hexdigest()
                snapshot_hash = snapshot_hash_file.read_text(encoding="utf-8").strip()
                if current_hash != snapshot_hash:
                    drift_warning = "\n⚠️ WARNING: Global PLAN.md has changed since this session started. You may be working on stale requirements.\n"
            
            info_header = f"🧠 Swarm Orienting Protocol Results (Session: {session_id}):{drift_warning}\n"
    else:
        # Global Mode
        plan_path = swarm_root / "docs" / "ai" / "PLAN.md"
        active_dir = swarm_root / "docs" / "ai" / "memory" / "active"
        info_header = "🧠 Swarm Orienting Protocol Results (Global):\n"
    
    info = [info_header]
    
    # 1. Load Roadmap
    if plan_path.exists():
        plan_content = plan_path.read_text(encoding="utf-8")
        # Extract high-level goals (first 5 lines for conciseness)
        info.append(f"📍 Roadmap Snapshot ({plan_path.relative_to(swarm_root)}):")
        info.append("\n".join(plan_content.splitlines()[:5]))
        if len(plan_content.splitlines()) > 5:
            info.append("...")
        info.append("")
    else:
        info.append("⚠️ PLAN.md not found.")
        
    # 2. Identify Active Tasks
    if active_dir.exists():
        active_files = list(active_dir.glob("*.md"))
        limit = 15
        info.append(f"🔥 Active Task Files ({len(active_files)} total):")
        
        display_files = active_files[:limit]
        for f in display_files:
            # Get the first line/title
            first_line = "No title"
            try:
                with open(f, "r", encoding="utf-8") as f_obj:
                    first_line = f_obj.readline().strip().replace("# ", "")
            except Exception:
                pass
            info.append(f"  • {f.name}: {first_line[:50]}...")
            
        if len(active_files) > limit:
            info.append(f"  ...and {len(active_files) - limit} more.")
    else:
        info.append("ℹ️ No active/ directory found.")
        
    return "\n".join(info)

def _claim_task(session_id: str, task_description: str) -> str:
    swarm_root = Path(__file__).parent.parent.parent.parent
    global_plan = swarm_root / "docs" / "ai" / "PLAN.md"
    
    if not global_plan.exists():
        return "❌ Global PLAN.md not found."
        
    content = global_plan.read_text(encoding="utf-8")
    lines = content.splitlines()
    updated_lines = []
    found = False
    
    for line in lines:
        if task_description in line:
            if "[x]" in line:
                return f"❌ Task already completed: {line}"
            if "[/]" in line and session_id not in line:
                return f"❌ Task already claimed by another session: {line}"
            
            # Claim it
            if "[ ]" in line:
                line = line.replace("[ ]", "[/]") + f" (claimed by {session_id})"
                found = True
            elif "[/]" in line and session_id in line:
                 return f"ℹ️ Task already claimed by you: {line}"
        updated_lines.append(line)
        
    if found:
        global_plan.write_text("\n".join(updated_lines), encoding="utf-8")
        # Also update session plan if exists to match
        _sync_session_plan(session_id, global_plan)
        return f"✅ Task claimed: {task_description}"
    
    return f"❌ Task not found in Global Plan: {task_description}"

def _merge_session(session_id: str) -> str:
    import shutil
    swarm_root = Path(__file__).parent.parent.parent.parent
    session_root = swarm_root / "docs" / "sessions" / session_id
    global_plan = swarm_root / "docs" / "ai" / "PLAN.md"
    
    if not session_root.exists():
         return "❌ Session not found."

    # 1. Update Global Plan with completed tasks
    # For now, we simple mark tasks claimed by this session as [x]
    if global_plan.exists():
        content = global_plan.read_text(encoding="utf-8")
        lines = content.splitlines()
        updated_lines = []
        updates_count = 0
        
        for line in lines:
            if f"(claimed by {session_id})" in line:
                # Mark done and remove claim tag
                line = line.replace("[/]", "[x]").replace(f" (claimed by {session_id})", "")
                updates_count += 1
            updated_lines.append(line)
            
        global_plan.write_text("\n".join(updated_lines), encoding="utf-8")
    
    # 2. Archive Session Memory
    active_dir = session_root / "memory" / "active"
    archive_file = swarm_root / "docs" / "ai" / "memory" / "archive" / f"session_{session_id}_summary.md"
    
    if active_dir.exists():
        summary = _refresh_memory(session_id) # Consolidates to session archive
        # Move session archive to global archive
        session_archive = session_root / "memory" / "archive" / "session_summary.md"
        if session_archive.exists():
            archive_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(session_archive, archive_file)
    
    # 3. Cleanup Session
    # shutil.rmtree(session_root) # Optional: Decide if we want to keep history? Let's keep for now but maybe rename?
    # For now, just leave it.
    
    return f"✅ Session merged. {updates_count} tasks marked completed in Global Plan. Memory archived to {archive_file.name}."

def _sync_session_plan(session_id: str, global_plan_path: Path):
    """Helper to re-copy global plan to session to keep them in sync after a claim."""
    import shutil
    import hashlib
    swarm_root = Path(__file__).parent.parent.parent.parent
    session_root = swarm_root / "docs" / "sessions" / session_id
    if session_root.exists():
        shutil.copy(global_plan_path, session_root / "PLAN.md")
        # Update hash to prevent drift warning for own actions
        plan_hash = hashlib.md5(global_plan_path.read_bytes()).hexdigest()
        (session_root / "plan_snapshot.hash").write_text(plan_hash, encoding="utf-8")

def _refresh_memory(session_id: str = None) -> str:
    swarm_root = Path(__file__).parent.parent.parent.parent
    
    if session_id:
        base_dir = swarm_root / "docs" / "sessions" / session_id
        active_dir = base_dir / "memory" / "active"
        archive_path = base_dir / "memory" / "archive" / "session_summary.md"
    else:
        active_dir = swarm_root / "docs" / "ai" / "memory" / "active"
        archive_path = swarm_root / "docs" / "ai" / "memory" / "archive" / "2026_01_Summary.md"
    
    if not active_dir.exists():
        return f"❌ active/ directory not found at {active_dir}."
        
    active_files = list(active_dir.glob("*.md"))
    to_prune = []
    summary_entries = []
    
    for f in active_files:
        # Safety guards
        if any(p in f.name for p in ["MASTER_PLAN", "ERROR_LOG", "[ACTIVE]"]):
            continue
            
        content = f.read_text(encoding="utf-8")
        # Check if completed
        if "[x]" in content or "status: completed" in content.lower():
            # Extract simple summary (first 500 chars)
            summary_entries.append(f"### {f.name}\n{content[:500]}...\n")
            to_prune.append(f)
            
    if not summary_entries:
        return "✅ No completed tasks found to refresh."
        
    # Append to archive
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with open(archive_path, "a", encoding="utf-8") as a:
        a.write("\n" + "\n".join(summary_entries))
        
    # Prune
    for f in to_prune:
        f.unlink()
        
    return f"📦 Memory Refreshed: Consolidated {len(summary_entries)} files into {archive_path.name} and pruned them."
