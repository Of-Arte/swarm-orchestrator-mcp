
import os
import json
import logging
from unittest.mock import MagicMock, patch
from mcp_core.orchestrator_loop import Orchestrator
from mcp_core.swarm_schemas import Task, ProjectProfile

logging.basicConfig(level=logging.DEBUG)

def run():
    f_path = "reproduce_profile.json"
    if os.path.exists(f_path): os.remove(f_path)
    if os.path.exists(f_path+".lock"): os.remove(f_path+".lock")
    
    try:
        orch = Orchestrator(state_file=f_path)
        t = Task(description="Test", status="PENDING")
        orch.state.add_task(t)
        orch.save_state()
        print("✅ Initial save done")
        
        with open(f_path, 'r') as f:
            print(f"File content post-init: {f.read()}")
            
        # Mocking Generate Response
        with patch("mcp_core.orchestrator_loop.generate_response") as mock_gen:
            resp = MagicMock()
            resp.status = "SUCCESS"
            mock_gen.return_value = resp
            
            print("Running process_task")
            orch.process_task(t.task_id)
            print("process_task returned")
            
        with open(f_path, 'r') as f:
            content = f.read()
            print(f"File content post-process: {content}")
            if not content:
                print("❌ File is empty!")
            else:
                data = json.loads(content)
                print(f"✅ Data loaded: {data.keys()}")
                p = ProjectProfile(**data)
                print(f"Provenance: {p.provenance_log}")

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run()
