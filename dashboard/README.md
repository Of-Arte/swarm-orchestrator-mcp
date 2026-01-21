# Swarm Admin Dashboard

The Swarm Admin Dashboard provides a real-time visual interface for the Orchestrator, allowing you to monitor tasks, view the knowledge graph, and check system status.

## Architecture

-   **Frontend**: React (Vite) + Wouter + Lucide + Recharts
-   **Backend**: FastAPI (`../dashboard_server.py`) acting as a bridge to the Orchestrator logic.
-   **Design**: custom "Premium" glassmorphism theme using Vanilla CSS.

## Prerequisites

-   Node.js (v18+)
-   Python 3.10+
-   Swarm dependencies (installed in the parent project)

## Installation & Running

### 1. Build the Frontend
Inside this `dashboard/` directory:
```bash
npm install
npm run build
```

### 2. Start the Dashboard Server
From the root `swarm` directory (parent):
```bash
python dashboard_server.py
```

### 3. Access the Dashboard
Open [http://localhost:8000](http://localhost:8000) in your browser.

## Features

-   **Overview**: System stats (active tasks, memory nodes).
-   **Task Board**: List of active tasks and their status.
-   **Knowledge Graph**: Interactive force-directed graph of the codebase (HippoRAG).
-   **Memory**: View active context and memory state.

## Development

-   **Frontend Dev Server**: `npm run dev` (Runs on port 5173).
-   **Backend Dev Server**: `python ../dashboard_server.py` (Runs on port 8000).

Note: The dashboard client expects the backend API at `/api`. In production (FastAPI serving static files), this works automatically. For development with `npm run dev`, you may need to configure Vite proxy.
