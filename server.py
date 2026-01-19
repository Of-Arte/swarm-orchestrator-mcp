"""
Swarm v3.0 - FastMCP Server

Exposes the Swarm orchestrator functionality as an MCP server.
This allows AI agents (like Claude Desktop, VSCode, etc.) to interact
with the Swarm via the Model Context Protocol.
"""

import logging
from typing import Optional
from fastmcp import FastMCP

# Import Swarm components
from mcp_core.orchestrator_loop import Orchestrator
from mcp_core.swarm_schemas import Task
from mcp_core.search_engine import CodebaseIndexer, HybridSearch, IndexConfig, get_embedding_provider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Swarm Orchestrator v3.0")

# Initialize orchestrator (lazy)
_orchestrator: Optional[Orchestrator] = None
_indexer: Optional[CodebaseIndexer] = None


def get_orchestrator() -> Orchestrator:
    """Lazy-load orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        logger.info("🚀 Initializing Swarm Orchestrator...")
        _orchestrator = Orchestrator()
    return _orchestrator


def get_indexer() -> CodebaseIndexer:
    """Lazy-load indexer instance."""
    global _indexer
    if _indexer is None:
        logger.info("📚 Initializing Codebase Indexer...")
        config = IndexConfig()
        _indexer = CodebaseIndexer(config)
        _indexer.load_cache()  # Try to load existing index
    return _indexer


@mcp.tool()
def process_task(instruction: str) -> str:
    """
    Create and process a task in the Swarm orchestrator using algorithmic workers.
    
    **When to use:**
    - Requesting code analysis, refactoring, or modifications
    - Tasks requiring Swarm's algorithmic capabilities (HippoRAG, SBFL, CRDT, etc.)
    - Complex multi-step software engineering workflows
    - When you need Swarm's blackboard state management
    
    **When NOT to use:**
    - Simple code search (use search_codebase instead)
    - Running commands in containers (use Docker MCP tools)
    - File system operations (use filesystem MCP tools)
    - Git operations (use GitHub/Git MCP tools)
    
    **Works well with:**
    - Docker MCP: Execute generated code in isolated environments
    - GitHub MCP: Apply Swarm changes to repositories
    - Filesystem MCP: Read files before processing
    
    **Example:**
    ```
    process_task("Refactor the authentication module to use async/await")
    # → Swarm analyzes code, applies algorithmic transformations
    ```
    
    Args:
        instruction: Natural language task description
        
    Returns:
        Task ID, status, and initial feedback from Swarm workers
    """
    try:
        orch = get_orchestrator()
        
        # Create a new task
        task = Task(description=instruction)
        task_id = task.task_id
        
        # Add to orchestrator state
        orch.state.tasks[task_id] = task
        orch.save_state()
        
        # Process the task
        orch.process_task(task_id)
        
        # Reload to get updated status
        orch.load_state()
        updated_task = orch.state.tasks[task_id]
        
        return f"✅ Task {task_id[:8]} created and processed.\nStatus: {updated_task.status}\nFeedback: {updated_task.feedback_log[-1] if updated_task.feedback_log else 'None'}"
        
    except Exception as e:
        logger.error(f"Error processing task: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
def get_status() -> str:
    """
    Get the current status of all tasks in the Swarm blackboard.
    
    **When to use:**
    - Checking progress of previously submitted tasks
    - Monitoring Swarm's internal state
    - Debugging task execution flows
    - Before creating new tasks to avoid duplicates
    
    **When NOT to use:**
    - Checking Docker container status (use Docker MCP)
    - Viewing file contents (use filesystem tools)
    - Git repository status (use GitHub MCP)
    
    **Example:**
    ```
    get_status()
    # → Returns list of all tasks with IDs, status (PENDING/COMPLETED), descriptions
    ```
    
    Returns:
        Formatted list of all tasks with their current status
    """
    try:
        orch = get_orchestrator()
        orch.load_state()
        
        if not orch.state.tasks:
            return "📋 No tasks found in the blackboard."
        
        status_lines = ["📋 Swarm Blackboard Status:\n"]
        for task_id, task in orch.state.tasks.items():
            status_lines.append(f"  • {task_id[:8]}: [{task.status}] {task.description[:50]}...")
        
        return "\n".join(status_lines)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
def search_codebase(query: str, top_k: int = 5, keyword_only: bool = False) -> str:
    """
    Search the codebase using hybrid semantic + keyword search.
    
    **When to use:**
    - Finding functions/classes by semantic description (e.g., "authentication logic")
    - Locating implementation of specific features
    - Discovering code patterns or similar implementations
    - Quick lookups before deeper analysis with retrieve_context()
    
    **When NOT to use:**
    - Deep architectural analysis (use retrieve_context for AST-based graph reasoning)
    - File tree navigation (use filesystem MCP tools)
    - Cross-repository search (use GitHub MCP search tools)
    - Regex-based pattern matching (use grep/ripgrep tools)
    
    **Works well with:**
    - retrieve_context(): Start with search, then deep-dive with HippoRAG
    - Docker MCP: Search for code, then test in containers
    - process_task(): Find code to modify, then create Swarm task
    
    **Examples:**
    ```
    # Semantic search
    search_codebase("database connection pooling")
    
    # Literal function name search
    search_codebase("calculate_metrics", keyword_only=True)
    
    # Find all error handlers
    search_codebase("exception handling", top_k=10)
    ```
    
    Args:
        query: Natural language description or exact keywords
        top_k: Number of results to return (1-50, default 5)
        keyword_only: Skip semantic matching for faster literal searches
        
    Returns:
        Formatted search results with file paths, line numbers, scores, and code snippets
    """
    try:
        indexer = get_indexer()
        
        if not indexer.chunks:
            return "⚠️ No index found. Please run 'index' command first."
        
        # Get embedding provider for hybrid search (optional)
        embed_provider = None
        if not keyword_only:
            has_embeddings = any(c.embedding is not None for c in indexer.chunks)
            if has_embeddings:
                try:
                    embed_provider = get_embedding_provider("auto")
                except RuntimeError:
                    logger.warning("No API key set, falling back to keyword search")
        
        # Perform search
        searcher = HybridSearch(indexer, embed_provider)
        
        if keyword_only:
            results = searcher.keyword_search(query, top_k=top_k)
        else:
            results = searcher.search(query, top_k=top_k)
        
        if not results:
            return "🔍 No results found."
        
        # Format results
        result_lines = [f"🔍 Found {len(results)} results for: {query}\n"]
        for i, result in enumerate(results, 1):
            result_lines.append(f"{i}. {result.file_path}:{result.start_line}-{result.end_line}")
            result_lines.append(f"   Score: {result.score:.3f}")
            result_lines.append(f"   {result.content[:200]}...\n")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        logger.error(f"Error searching codebase: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
def index_codebase(path: str = ".", provider: str = "auto") -> str:
    """
    Index the codebase for semantic search capabilities.
    
    **When to use:**
    - First-time setup before using search_codebase()
    - After significant code changes to refresh embeddings
    - When switching to a different codebase/directory
    - To enable semantic (meaning-based) search vs keyword-only
    
    **When NOT to use:**
    - Before every search (index persists until manually refreshed)
    - On extremely large codebases (>100k files) without filtering
    - When only keyword search is needed (works without indexing)
    
    **Prerequisites:**
    - Set OPENAI_API_KEY or GOOGLE_API_KEY for semantic embeddings
    - Or use provider="local" for offline embedding models (slower)
    
    **Works well with:**
    - search_codebase(): Required for semantic search capabilities
    - Docker MCP: Index mounted volumes inside containers
    
    **Examples:**
    ```
    # Index current directory with auto-detected provider
    index_codebase()
    
    # Index specific path with OpenAI embeddings
    index_codebase("/path/to/project", provider="openai")
    
    # Offline indexing (keyword-only if no local model available)
    index_codebase(provider="local")
    ```
    
    Args:
        path: Absolute or relative path to codebase root (default: current directory)
        provider: Embedding provider - "auto" | "gemini" | "openai" | "local"
        
    Returns:
        Number of indexed code chunks and status message
    """
    try:
        config = IndexConfig(root_path=path)
        indexer = CodebaseIndexer(config)
        
        # Try to get embedding provider
        try:
            embed_provider = get_embedding_provider(provider)
            logger.info(f"Using embedding provider: {type(embed_provider).__name__}")
            indexer.index_all(embed_provider)
        except RuntimeError as e:
            logger.warning(f"⚠️ {e}")
            logger.warning("Indexing files without embeddings (keyword search only)")
            indexer.index_all(None)
        
        # Update global indexer
        global _indexer
        _indexer = indexer
        
        return f"✅ Indexed {len(indexer.chunks)} chunks from {path}"
        
    except Exception as e:
        logger.error(f"Error indexing codebase: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
def retrieve_context(query: str, top_k: int = 10) -> str:
    """
    Use HippoRAG to retrieve relevant code context via AST graph + PageRank.
    
    **When to use:**
    - Understanding code architecture and relationships
    - Finding all code related to a feature (multi-hop reasoning)
    - Analyzing dependencies and call graphs
    - Deep dives after initial search_codebase() results
    - Complex refactoring requiring full context understanding
    
    **When NOT to use:**
    - Simple function name lookups (use search_codebase with keyword_only=True)
    - First-time exploration (use search_codebase first, it's faster)
    - Non-Python codebases (HippoRAG currently Python-only via AST)
    
    **Comparison to search_codebase:**
    - search_codebase: Fast, surface-level, uses embeddings
    - retrieve_context: Slower, deep analysis, uses AST + graph algorithms
    - **Best practice:** Search first, retrieve context for deep dives
    
    **Works well with:**
    - search_codebase(): Find entry points, then retrieve full context
    - process_task(): Get context, then create informed refactoring tasks
    - Docker MCP: Retrieve context, test in isolated environment
    
    **Technical details:**
    - Builds Abstract Syntax Tree (AST) for all Python files
    - Creates knowledge graph of code relationships
    - Runs Personalized PageRank to find semantically related nodes
    - Returns ranked results by graph centrality + relevance
    
    **Examples:**
    ```
    # Find all authentication-related code
    retrieve_context("user authentication flow")
    
    # Understand database layer architecture
    retrieve_context("database models and migrations", top_k=15)
    
    # Deep dive after search
    search_codebase("payment processing")  # Fast overview
    retrieve_context("payment processing")  # Deep architectural understanding
    ```
    
    Args:
        query: Natural language description of concept/feature to analyze
        top_k: Number of context chunks to return (1-50, default 10)
        
    Returns:
        Ranked code chunks with node types, PPR scores, file locations, and content
    """
    try:
        from mcp_core.algorithms import HippoRAGRetriever
        
        retriever = HippoRAGRetriever()
        
        logger.info("📊 Building AST knowledge graph...")
        retriever.build_graph_from_ast(".", extensions=[".py"])
        
        logger.info(f"🔗 Graph: {retriever.graph.number_of_nodes()} nodes, {retriever.graph.number_of_edges()} edges")
        
        chunks = retriever.retrieve_context(query, top_k=top_k)
        
        if not chunks:
            return "🔍 No context found."
        
        result_lines = [f"🔍 Retrieved {len(chunks)} context chunks for: {query}\n"]
        for i, chunk in enumerate(chunks, 1):
            result_lines.append(f"{i}. [{chunk.node_type}] {chunk.node_name}")
            result_lines.append(f"   {chunk.file_path}:{chunk.start_line}-{chunk.end_line}")
            result_lines.append(f"   PPR Score: {chunk.ppr_score:.4f}")
            result_lines.append(f"   {chunk.content[:150]}...\n")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return f"❌ Error: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    logger.info("🚀 Starting Swarm MCP Server...")
    mcp.run()
