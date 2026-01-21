import os
import sys
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

app = FastAPI(title="Swarm Admin API")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock/Load actual data
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
        _orchestrator.load_state()
    return _orchestrator

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
