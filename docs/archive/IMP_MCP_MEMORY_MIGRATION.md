# IMP_MCP_MEMORY_MIGRATION.md

## Overview
Migration of the Knowledge Graph Memory Server (`mcp-memory`) from a misidentified/missing Docker container to a robust, Antigravity-integrated Docker configuration.

## Status
- **Analysis**: Completed. Identified that `wizardly_lumiere` is the GitHub server. No existing memory server found.
- **Strategy**: "Fresh Start" with Docker.
- **Configuration**: `mcpServers.json` configured to use `node:18-alpine` ephemeral container.
- **Persistence**: Local binding to `%APPDATA%\Antigravity\memory.json` (or equivalent).

## Configuration Details
**File**: `%APPDATA%\Antigravity\mcpServers.json`

```json
{
  "mcpServers": {
    "memory": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "C:\\Users\\YOUR_USERNAME\\AppData\\Roaming\\Antigravity\\memory.json:/app/memory.json",
        "node:18-alpine",
        "npx",
        "-y",
        "@modelcontextprotocol/server-memory",
        "/app/memory.json"
      ]
    }
  }
}
```

## Verification Steps
1.  **File Existence**: `memory.json` created active.
2.  **Docker Pull**: `node:18-alpine` will be pulled on first run.
3.  **Connection**: Antigravity should now show "memory" as a connected server.

## Next Steps
- Restart Antigravity or "Reload Window" to pick up the new server.
- Verify "Knowledge Graph" tools in the tool list.
