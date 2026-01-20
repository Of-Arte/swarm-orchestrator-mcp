
import os
import sys
import time
import logging
from pathlib import Path
from dataclasses import dataclass

sys.path.append(os.getcwd())

# Import only necessary components
from mcp_core.swarm_schemas import Task
from mcp_core.algorithms.git_worker import GitWorker
from mcp_core.worker_prompts import prompt_git_commit

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Mock State/Orchestrator context
class MockState:
    worker_models = {"git-writer": "llama-3.2-3b"} # Use our free model

class MockOrchestrator:
    def __init__(self):
        self.state = MockState()
        self.git = GitWorker(".") # Use current dir

    # Copy of the relevant logic from _handle_git_workflow
    def handle_git_workflow(self, task: Task):
        print(f"🔄 Processing Task: {task.task_id}")
        
        if not self.git.is_available():
            print("❌ Git not available")
            return

        # Commit Worker Logic
        if task.git_commit_ready:
            print("🔍 Checking for changes...")
            if not self.git.has_changes():
                 print("⚠️ Commit Worker Skipped: No uncommitted changes detected.")
                 task.feedback_log.append("⚠️ Commit Worker Skipped: No uncommitted changes detected.")
            else:
                 print("✅ Changes detected! Generating commit...")
                 repo_owner = "owner" # Mock
                 repo_name = "repo"   # Mock
                 
                 git_context = {
                    "output_files": task.output_files,
                    "repo_owner": repo_owner,
                    "repo_name": repo_name,
                 }
                 commit_prompt = prompt_git_commit(task, git_context)
                 
                 # Call LLM
                 try:
                    from mcp_core.llm import generate_response
                    git_model = self.state.worker_models["git-writer"]
                    print(f"💾 Calling LLM ({git_model})...")
                    
                    response = generate_response(commit_prompt, model_alias=git_model)
                    
                    print(f"📥 LLM Response Status: {response.status}")
                    print(f"📥 Reasoning: {response.reasoning_trace}")
                    
                    if response.tool_calls:
                        calls_str = "\n".join([f"{t.function}({t.arguments})" for t in response.tool_calls])
                        print(f"🛠️  Tool Calls Generated:\n{calls_str}")
                        task.feedback_log.append(f"Commit Worker: {calls_str}")
                    else:
                        print("⚠️ No tool calls generated (Text only response)")
                        task.feedback_log.append(f"Commit Worker: {response.reasoning_trace}")

                 except Exception as e:
                     print(f"❌ LLM Error: {e}")

def test_git_worker_isolated():
    print("🚀 Initializing Isolated Git Worker Test...")
    
    # 1. Setup: Create dummy file
    test_file = Path("git_worker_test_artifact.txt")
    test_file.write_text(f"Test content {time.time()}")
    print(f"📝 Modified file: {test_file}")
    
    try:
        orch = MockOrchestrator()
        
        task = Task(
            task_id="test_git_002",
            description="Implement test artifact",
            status="COMPLETED",
            git_commit_ready=True,
            output_files=[str(test_file.absolute())]
        )
        
        orch.handle_git_workflow(task)
        
    finally:
        if test_file.exists():
            test_file.unlink()
            print("🧹 Cleanup done")

if __name__ == "__main__":
    test_git_worker_isolated()
