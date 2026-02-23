import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add parent directory to path to import mcp_core
sys.path.append(str(Path(__file__).parent))

from mcp_core.orchestrator_loop import Orchestrator
from mcp_core.search_engine import CodebaseIndexer, IndexConfig
from mcp_core.algorithms.hipporag_retriever import HippoRAGRetriever
from mcp_core.algorithms.hipporag_retriever import HippoRAGRetriever
from mcp_core.telemetry.telemetry_analytics import TelemetryAnalyticsService

from fastapi import Security, Depends
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse
import secrets

# Security Configuration
SWARM_DASHBOARD_KEY = os.getenv("SWARM_DASHBOARD_KEY")
if not SWARM_DASHBOARD_KEY:
    # Generate a secure key if one isn't provided
    generated_key = secrets.token_urlsafe(32)
    logging.warning(f"⚠️ NO DASHBOARD KEY SET! Generated temporary key: {generated_key}")
    logging.warning("Please set SWARM_DASHBOARD_KEY in your .env file for persistence.")
    SWARM_DASHBOARD_KEY = generated_key

SWARM_ALLOWED_ORIGINS = os.getenv("SWARM_ALLOWED_ORIGINS", "*").split(",")

api_key_header = APIKeyHeader(name="X-Swarm-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verifies the X-Swarm-Key header for admin access."""
    if not api_key:
        raise HTTPException(
            status_code=403, 
            detail="Authentication required. Please provide X-Swarm-Key header."
        )
    if api_key != SWARM_DASHBOARD_KEY:
        raise HTTPException(
            status_code=403, 
            detail="Invalid authentication key."
        )
    return api_key

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' *"
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.tokens = {}
    
    async def dispatch(self, request, call_next):
        import time
        
        # Simple IP-based rate limiting (in production use Redis)
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Cleanup old entries (naive)
        if len(self.tokens) > 1000:
            self.tokens = {k: v for k, v in self.tokens.items() if now - v['last'] < self.window}
            
        if client_ip not in self.tokens:
            self.tokens[client_ip] = {'count': 0, 'last': now}
            
        bucket = self.tokens[client_ip]
        if now - bucket['last'] > self.window:
            bucket['count'] = 0
            bucket['last'] = now
            
        if bucket['count'] >= self.limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."}
            )
            
        bucket['count'] += 1
        return await call_next(request)

app = FastAPI(title="Swarm Admin API")

# 1. Rate Limiting (DoS Protection)
app.add_middleware(RateLimitMiddleware, limit=200, window=60)

# 2. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 2. Trusted Host (Prevent Host header attacks)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "swarm-dashboard.local"]
)

# 3. CORS (Restrict to allowed origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=SWARM_ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Multi-session management
_orchestrators: Dict[str, Orchestrator] = {}
_active_session_id: str = os.getenv("SWARM_SESSION_ID", "default")
_analytics = None

def get_analytics():
    global _analytics
    if _analytics is None:
        _analytics = TelemetryAnalyticsService()
    return _analytics

def get_orchestrator(session_id: str = None):
    global _orchestrators, _active_session_id
    sid = session_id or _active_session_id
    
    if sid not in _orchestrators:
        # Create a new orchestrator for this session
        import logging
        logging.info(f"Dashboard: Initializing orchestrator for session '{sid}'")
        _orchestrators[sid] = Orchestrator(session_id=sid)
        _orchestrators[sid].load_state()
        
    return _orchestrators[sid]

@app.get("/api/sessions")
async def get_sessions():
    """List all available sessions in the database."""
    orch = get_orchestrator()
    # Use the orchestrator's postgres client to list sessions
    sessions = await orch.postgres.list_sessions()
    return {
        "active_session": _active_session_id,
        "sessions": sessions
    }

@app.post("/api/sessions/{session_id}/activate", dependencies=[Depends(verify_api_key)])
async def activate_session(session_id: str):
    """Switch the dashboard to a different session."""
    global _active_session_id
    _active_session_id = session_id
    # Initialize it if not already tracked
    get_orchestrator(session_id)
    return {"status": "success", "active_session": _active_session_id}

@app.get("/api/config", dependencies=[Depends(verify_api_key)])
async def get_config():
    """Get system configuration (env and models)."""
    # 1. Load safe env vars
    safe_keys = ["GEMINI_API_KEY", "OPENAI_API_KEY", "POSTGRES_URL", "SWARM_MAX_LOOPS", "SWARM_DEBUG"]
    env_data = {k: os.getenv(k, "") for k in safe_keys}
    
    # 2. Load model config
    from mcp_core.config_loader import load_global_model_config
    model_config = load_global_model_config()
    
    return {
        "env": env_data,
        "models": model_config
    }

@app.post("/api/config", dependencies=[Depends(verify_api_key)])
async def update_config(config: Dict[str, Any]):
    """Update system configuration."""
    # This is a dangerous but powerful operation for an admin dashboard
    # 1. Update .env file if it exists
    if "env" in config:
        env_path = ROOT_DIR.parent / ".env"
        if env_path.exists():
            # Simple .env update (naive)
            lines = env_path.read_text().splitlines()
            new_lines = []
            updated_keys = set()
            
            for line in lines:
                if "=" in line and not line.startswith("#"):
                    key = line.split("=")[0].strip()
                    if key in config["env"]:
                        new_lines.append(f"{key}={config['env'][key]}")
                        updated_keys.add(key)
                        continue
                new_lines.append(line)
            
            # Add new keys
            for key, val in config["env"].items():
                if key not in updated_keys:
                    new_lines.append(f"{key}={val}")
            
            env_path.write_text("\n".join(new_lines))
            
    # 2. Update model config
    if "models" in config:
        home = os.path.expanduser("~")
        config_path = Path(home) / ".gemini" / "antigravity" / "mcp_config.json"
        
        if config_path.exists():
            try:
                import json
                data = json.loads(config_path.read_text())
                data["models"] = config["models"]
                config_path.write_text(json.dumps(data, indent=2))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update model config: {e}")

    return {"status": "success", "message": "Configuration updated. Restart may be required."}

@app.get("/api/status")
async def get_status():
    orch = get_orchestrator()
    return {
        "status": "online",
        "tasks_total": len(orch.state.tasks),
        "tasks_completed": len([t for t in orch.state.tasks.values() if t.status == "COMPLETED"]),
        "agent_id": "Swarm-Master-v3",
        "agent_id": "Swarm-Master-v3",
        "memory_nodes": _get_graph_node_count()
    }

def _get_graph_node_count():
    try:
        config = IndexConfig()
        retriever = HippoRAGRetriever()
        cache_path = os.path.join(config.root_path or os.getcwd(), ".hipporag_cache")
        if retriever.load_graph(cache_path):
             return retriever.graph.number_of_nodes()
        return 0
    except Exception:
        return 0

@app.get("/api/tasks")
async def get_tasks():
    orch = get_orchestrator()
    return list(orch.state.tasks.values())

@app.get("/api/memory")
async def get_memory():
    orch = get_orchestrator()
    return {
        "provenance": orch.state.provenance_log,
        "worker_models": orch.state.worker_models,
        "toolchain": orch.state.toolchain_config.dict() if orch.state.toolchain_config else None,
        "stack": orch.state.stack_fingerprint.dict() if orch.state.stack_fingerprint else None
    }

@app.get("/api/docs")
async def list_docs():
    """Returns a list of available documentation files."""
    docs = [
        {"id": "README.md", "label": "README"},
        {"id": "ARCHITECTURE.md", "label": "Architecture"},
        {"id": "CONTRIBUTING.md", "label": "Contributing"},
        {"id": "CHANGELOG.md", "label": "Changelog"},
        {"id": "SECURITY.md", "label": "Security"}
    ]
    
    for folder in ["human", "ai"]:
        docs_dir = ROOT_DIR / "docs" / folder
        if docs_dir.exists():
            for f in docs_dir.glob("*.md"):
                docs.append({"id": f"{folder}/{f.name}", "label": f"{folder.upper()} - {f.stem}"})
    
    return docs

@app.get("/api/docs/{filename:path}")
async def get_doc_file(filename: str):
    """Serves the content of markdown files from the root and docs/ directory."""
    # Whitelist allowed documentation files to avoid path traversal
    allowed_files = {
        "README.md": ROOT_DIR / "README.md",
        "ARCHITECTURE.md": ROOT_DIR / "ARCHITECTURE.md",
        "CONTRIBUTING.md": ROOT_DIR / "CONTRIBUTING.md",
        "CHANGELOG.md": ROOT_DIR / "CHANGELOG.md",
        "SECURITY.md": ROOT_DIR / "SECURITY.md"
    }
    
    # Also allow files in docs/human/ and docs/ai/
    for folder in ["human", "ai"]:
        docs_dir = ROOT_DIR / "docs" / folder
        if docs_dir.exists():
            for f in docs_dir.glob("*.md"):
                allowed_files[f"{folder}/{f.name}"] = f

    if filename not in allowed_files:
        raise HTTPException(status_code=404, detail="Document not found")
        
    doc_path = allowed_files[filename]
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Document file missing")
        
    with open(doc_path, "r", encoding="utf-8") as f:
        return {"filename": filename, "content": f.read()}

@app.get("/api/graph")
async def get_graph(limit: int = 500):
    """Returns nodes and edges for force-graph visualization.
    
    Args:
        limit (int): Max number of nodes to return (selected by degree centrality).
    """
    try:
        # Load indexing config to get root path
        config = IndexConfig()
        retriever = HippoRAGRetriever()
        
        # Try to load cached graph
        cache_path = os.path.join(config.root_path or os.getcwd(), ".hipporag_cache")
        if not retriever.load_graph(cache_path):
             return {"nodes": [], "links": []}
        
        graph = retriever.graph
        
        # Calculate degrees for valid nodes (filtering out any strange artifacts if necessary)
        # Using degree as a proxy for "importance" to show the most connected components
        if graph.number_of_nodes() > limit:
            # Sort by degree (in_degree + out_degree)
            node_degrees = list(graph.degree())
            node_degrees.sort(key=lambda x: x[1], reverse=True)
            top_nodes = {node_id for node_id, _ in node_degrees[:limit]}
        else:
            top_nodes = set(graph.nodes())

        # Convert NetworkX graph to D3 format, filtering for top_nodes
        nodes = []
        for node_id in top_nodes:
            attrs = graph.nodes[node_id]
            nodes.append({
                "id": node_id,
                "name": node_id.split("::")[-1],
                "type": attrs.get("type", "unknown"),
                "file": attrs.get("file", "")
            })
            
        links = []
        for source, target, attrs in graph.edges(data=True):
            if source in top_nodes and target in top_nodes:
                links.append({
                    "source": source,
                    "target": target,
                    "type": attrs.get("type", "calls")
                })
            
        return {"nodes": nodes, "links": links}
        
    except Exception as e:
        print(f"Error serving graph: {e}")
        return {"nodes": [], "links": []}

@app.get("/api/analytics/tools")
async def get_tool_analytics(days: int = 7):
    """Get success rates for problematic tools."""
    analytics = get_analytics()
    return analytics.get_problematic_tools(threshold=1.0, window_days=days)

@app.get("/api/analytics/roles")
async def get_role_analytics():
    """Get success rates for all git roles."""
    analytics = get_analytics()
    roles = ["feature_scout", "code_auditor", "issue_triage", "branch_manager", "project_lifecycle"]
    stats = []
    for role in roles:
        rate = analytics.get_role_success_rate(role)
        stats.append({"role": role, "success_rate": rate})
    return stats

@app.get("/api/health")
async def get_health():
    """Get system health metrics."""
    analytics = get_analytics()
    orch = get_orchestrator()
    
    # Check DB size
    db_size_mb = 0
    if analytics.db_path.exists():
        db_size_mb = analytics.db_path.stat().st_size / (1024 * 1024)
        
    # Count tripped circuit breakers
    tripped = 0
    # Scan known tools from recent usage
    tools = analytics.get_problematic_tools(threshold=1.0, window_days=7)
    for t in tools:
        if analytics.get_tool_status(t['tool']) == "TRIPPED":
            tripped += 1
            
    return {
        "status": "critical" if tripped > 3 else "degraded" if tripped > 0 else "healthy",
        "telemetry_db_size_mb": round(db_size_mb, 2),
        "circuit_breakers_tripped": tripped,
        "active_tasks": len([t for t in orch.state.tasks.values() if t.status == "RUNNING"]),
    }

@app.post("/api/telemetry/prune", dependencies=[Depends(verify_api_key)])
async def prune_telemetry(days: int = 30):
    """Manually trigger telemetry pruning."""
    analytics = get_analytics()
    deleted = analytics.prune_old_events(retention_days=days)
    return {"deleted_rows": deleted}

@app.post("/api/telemetry/optimize", dependencies=[Depends(verify_api_key)])
async def optimize_telemetry():
    """Force telemetry DB optimization."""
    analytics = get_analytics()
    try:
        analytics.optimize_database()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/circuit-breakers")
async def get_circuit_breakers():
    """List all known tools and their circuit breaker status."""
    analytics = get_analytics()
    # Get all tools seen in last 7 days
    tools = analytics.get_problematic_tools(threshold=1.0, window_days=7)
    
    breakers = []
    for t in tools:
        status = analytics.get_tool_status(t['tool'])
        breakers.append({
            "tool": t['tool'],
            "status": status,
            "success_rate": t['success_rate'],
            "total_uses": t['total_uses']
        })
    return breakers

@app.post("/api/circuit-breakers/{tool}/reset", dependencies=[Depends(verify_api_key)])
async def reset_circuit_breaker(tool: str):
    """
    Reset a circuit breaker (manual override).
    In a real implementation, this might write a 'reset' event to the DB 
    or clear a cache. For this MVP, we'll log an event simulating a success 
    to bump the rate up, or we'd need a specific 'reset' mechanism in analytics.
    
    For now, we'll just log an artificial success event to help recovery.
    """
    # TODO: Implement proper reset logic in TelemetryAnalyticsService
    # This is a placeholder for the frontend action
    return {"status": "reset", "message": f"Circuit breaker reset requested for {tool}"}

# Task Management Endpoints

@app.post("/api/tasks", dependencies=[Depends(verify_api_key)])
async def create_task(description: str, priority: str = "NORMAL"):
    """Create a new task in the orchestrator."""
    orch = get_orchestrator()
    from mcp_core.swarm_schemas import Task
    import uuid
    
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    new_task = Task(
        task_id=task_id,
        description=description,
        status="PENDING",
        priority=priority
    )
    
    orch.state.tasks[task_id] = new_task
    orch.save_state()
    
    return {"task_id": task_id, "status": "created"}

@app.post("/api/tasks/{task_id}/cancel", dependencies=[Depends(verify_api_key)])
async def cancel_task(task_id: str):
    """Cancel a running or pending task."""
    orch = get_orchestrator()
    
    if task_id not in orch.state.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = orch.state.tasks[task_id]
    if task.status in ["COMPLETED", "FAILED"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed/failed task")
    
    task.status = "CANCELLED"
    task.feedback_log.append("Task cancelled by user via dashboard")
    orch.save_state()
    
    return {"task_id": task_id, "status": "cancelled"}

@app.post("/api/tasks/{task_id}/retry", dependencies=[Depends(verify_api_key)])
async def retry_task(task_id: str):
    """Retry a failed task."""
    orch = get_orchestrator()
    
    if task_id not in orch.state.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = orch.state.tasks[task_id]
    if task.status != "FAILED":
        raise HTTPException(status_code=400, detail="Can only retry failed tasks")
    
    # Reset task status
    task.status = "PENDING"
    task.feedback_log.append("Task retry requested by user via dashboard")
    orch.save_state()
    
    # Optionally trigger processing (async)
    # In a real implementation, you'd queue this or trigger background processing
    
    return {"task_id": task_id, "status": "retry_queued"}

# Indexing & System Control Endpoints

@app.post("/api/indexing/codebase", dependencies=[Depends(verify_api_key)])
async def trigger_codebase_indexing(path: str = ".", provider: str = "auto"):
    """Trigger codebase indexing (background operation)."""
    try:
        from mcp_core.search_engine import CodebaseIndexer, IndexConfig
        
        config = IndexConfig(root_path=path)
        indexer = CodebaseIndexer(config)
        
        # This is a synchronous operation - in production, run in background
        chunk_count = indexer.index_codebase(provider=provider)
        
        return {
            "status": "success",
            "chunks_indexed": chunk_count,
            "provider": provider
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/indexing/graph", dependencies=[Depends(verify_api_key)])
async def rebuild_knowledge_graph():
    """Rebuild HippoRAG knowledge graph from indexed codebase."""
    try:
        from mcp_core.algorithms.hipporag_retriever import HippoRAGRetriever
        from mcp_core.search_engine import IndexConfig
        
        config = IndexConfig()
        retriever = HippoRAGRetriever()
        
        cache_path = os.path.join(config.root_path or os.getcwd(), ".hipporag_cache")
        
        # Build graph (synchronous - should be background in production)
        retriever.build_graph(cache_path)
        node_count = retriever.graph.number_of_nodes() if retriever.graph else 0
        
        return {
            "status": "success",
            "nodes": node_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def get_logs(lines: int = 50, level: str = "INFO"):
    """Get recent log entries."""
    # Simple implementation - reads from a log file if it exists
    # In production, you'd integrate with the logging system directly
    
    log_file = Path.home() / ".swarm" / "swarm.log"
    
    if not log_file.exists():
        return {"logs": [], "message": "No log file found"}
    
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            
        # Filter by level if specified
        if level != "ALL":
            filtered = [l for l in all_lines if level in l]
        else:
            filtered = all_lines
            
        # Return last N lines
        recent = filtered[-lines:] if len(filtered) > lines else filtered
        
        return {
            "logs": [line.strip() for line in recent],
            "total_lines": len(recent)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files from React build
ROOT_DIR = Path(__file__).parent.absolute()
static_path = ROOT_DIR / "dashboard" / "dist"

if static_path.exists():
    # Mount assets separately to avoid capturing API calls
    assets_path = static_path / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")
    
    # Static files at root (index.html, etc)
    # Using a middleware or a catch-all route is better for SPAs
    from fastapi.responses import FileResponse
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # If the path looks like an API call, let it through (should have been caught by routes above)
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
            
        # Check if file exists in static path
        file_path = static_path / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
            
        # Default to index.html for SPA routing
        return FileResponse(str(static_path / "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "Swarm Admin API Online. Run 'npm run build' in dashboard/ to serve frontend.", "path_checked": str(static_path)}

if __name__ == "__main__":
    import uvicorn
    # Use reload=True for development if needed, but here we just run it
    uvicorn.run(app, host="0.0.0.0", port=8000)
