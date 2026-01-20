"""
Dynamic Tool Loader

Automatically loads and registers tools from the dynamic/ directory.
"""

import logging
import importlib.util
from pathlib import Path
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def load_dynamic_tools(mcp: FastMCP) -> int:
    """
    Load all dynamic tools from mcp_core/tools/dynamic/.
    
    Each tool file must have a `register(mcp: FastMCP)` function.
    
    Args:
        mcp: The FastMCP server instance
        
    Returns:
        Number of tools loaded
    """
    tools_dir = Path(__file__).parent
    loaded = 0
    
    for tool_file in tools_dir.glob("*.py"):
        # Skip loader and test files
        if tool_file.name in ("loader.py", "__init__.py"):
            continue
            
        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(
                tool_file.stem, 
                tool_file
            )
            if spec is None or spec.loader is None:
                continue
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Call register function if it exists
            if hasattr(module, "register"):
                module.register(mcp)
                logger.info(f"✅ Loaded dynamic tool (via register): {tool_file.name}")
                loaded += 1
            else:
                # Inspect module for top-level functions that look like tools
                # Heuristic: Functions that are not private and not imported
                import inspect
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if name.startswith("_") or func.__module__ != module.__name__:
                        continue
                    
                    try:
                        mcp.tool()(func)
                        logger.info(f"    - Registered function: {name}")
                        loaded += 1
                    except Exception as e:
                        logger.warning(f"Could not register {name}: {e}")
                
                logger.info(f"✅ Loaded dynamic tool module: {tool_file.name}")

        except Exception as e:
            logger.error(f"❌ Failed to load {tool_file.name}: {e}")
    
    logger.info(f"📦 Loaded {loaded} dynamic tools")
    return loaded
