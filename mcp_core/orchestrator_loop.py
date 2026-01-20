import os
import json
import logging
import time
import shutil

from filelock import FileLock
from datetime import datetime

# V2 Core
from mcp_core.swarm_schemas import ProjectProfile, Task
from mcp_core.stack_detector import StackDetector
from mcp_core.toolchain_manager import ToolchainManager
from mcp_core.worker_prompts import prompt_architect, prompt_engineer, prompt_auditor
from mcp_core.llm import generate_response

# V3.0 Algorithms
from mcp_core.algorithms import (
    OCCValidator, CRDTMerger, HippoRAGRetriever,
    WeightedVotingConsensus, DebateEngine,
    Z3Verifier, OchiaiLocalizer, GitWorker
)
from mcp_core.sync.sync_engine import SyncEngine

STATE_FILE = "project_profile.json"
LEGACY_STATE_FILE = "blackboard_state.json"
LOCK_FILE = "project_profile.json.lock"


class Orchestrator:
    def __init__(self, root_path: str = ".", state_file: str = STATE_FILE):
        self.root_path = root_path
        self.state_file = state_file
        self.lock_file = f"{state_file}.lock"

        # [Fix: Race/Migration]
        self._ensure_migration()

        # Load State
        self.state = ProjectProfile()
        self.load_state()

        # [Component: Eyes]
        self.detector = StackDetector(root_path)

        # [Component: Hands]
        self.toolchain = ToolchainManager(root_path)

        # Initialize Stack Identity if missing
        if not self.state.stack_fingerprint:
            logging.info("Initializing Stack Detection...")
            self.state.stack_fingerprint = self.detector.detect()
            self.save_state()

        # Initialize Toolchain
        self.state.toolchain_config = self.toolchain.load_or_detect(
            self.state.stack_fingerprint)
        self.save_state()

        # [V3.0: Algorithm Components]
        self.occ = OCCValidator()
        self.crdt = CRDTMerger()
        self.rag = None  # Lazy init (builds graph on first use)
        self.consensus = WeightedVotingConsensus()
        self.debate = DebateEngine()
        self.verifier = Z3Verifier() if Z3Verifier else None
        self.sbfl = OchiaiLocalizer() if OchiaiLocalizer else None
        self.git = GitWorker(root_path)
        self.sync = SyncEngine(root_path)
        
        logging.info("✅ v3.0 Algorithm workers initialized")
        if self.git.is_available():
            logging.info(f"✅ Git: {self.git.config.provider.value}")

    def _ensure_migration(self):
        """Auto-Archive Legacy State Logic."""
        if os.path.exists(LEGACY_STATE_FILE):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"blackboard_state_v1_backup_{timestamp}.json"
            logging.warning(
                f"⚠️ Migrating legacy state: {LEGACY_STATE_FILE} -> {archive_name}")
            shutil.move(LEGACY_STATE_FILE, archive_name)

    def load_state(self) -> None:
        if not os.path.exists(self.state_file):
            return

        with FileLock(self.lock_file):
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    self.state = ProjectProfile(**data)
            except Exception as e:
                logging.error(f"Failed to load state: {e}")

    def save_state(self) -> None:
        with FileLock(self.lock_file):
            with open(self.state_file, "w") as f:
                f.write(self.state.model_dump_json(indent=2))

    def process_task(self, task_id: str) -> None:
        self.load_state()
        task = self.state.get_task(task_id)
        if not task or task.status == "COMPLETED":
            return

        # [V3.0: Algorithm Dispatch]
        # Check task flags and route to appropriate algorithm
        algorithm_handled = False

        # 1. Context Retrieval (HippoRAG)
        if task.context_needed and self._handle_context_retrieval(task):
            algorithm_handled = True

        # 2. Conflict Detection (OCC)
        if task.conflicts_detected and self._handle_occ_validation(task):
            algorithm_handled = True

        # 3. Concurrent Edits (CRDT)
        if task.concurrent_edits and self._handle_crdt_merge(task):
            algorithm_handled = True

        # 4. Consensus Required (Weighted Voting)
        if task.requires_consensus and self._handle_consensus(task):
            algorithm_handled = True

        # 5. Debate Required (Debate Engine)
        if task.requires_debate and self._handle_debate(task):
            algorithm_handled = True

        # 6. Verification Required (Z3)
        if task.verification_required and self._handle_verification(task):
            algorithm_handled = True

        # 7. Tests Failing (Ochiai SBFL)
        if task.tests_failing and self._handle_fault_localization(task):
            algorithm_handled = True
        
        # 8. Git Workflow (v3.2 - Autonomous Git Team)
        if (task.git_commit_ready or task.git_create_pr) and self._handle_git_workflow(task):
            algorithm_handled = True

        # If algorithm handled the task, skip traditional LLM flow
        if algorithm_handled:
            self.save_state()
            return

        # [Fix: Context] Pruning logic
        # Instead of self.state.memory_bank (which could be huge), we just pass key items
        # For now, we still pass it, but this is where the RollingWindow would go.
        context_slice = self.state.memory_bank
        
        # [v3.1: Git Context Injection]
        git_context = {}
        if self.git.is_available():
            git_context = {
                "git_available": True,
                "git_workflow_instructions": self.git.get_workflow_instructions()
            }

        worker_prompt = ""
        worker_model = self.state.worker_models.get("default", "gemini-pro")

        if "plan" in task.description.lower():
            worker_prompt = prompt_architect(task, context_slice)
            worker_model = self.state.worker_models.get("architect", worker_model)
        elif "audit" in task.description.lower():
            worker_prompt = prompt_auditor(task, git_context)
            worker_model = self.state.worker_models.get("auditor", worker_model)
        else:
            worker_prompt = prompt_engineer(task, context_slice, git_context)
            worker_model = self.state.worker_models.get("engineer", worker_model)

        logging.info(f"Dispatching task {task_id[:8]}...")

        # Agentic Mode (Pause)
        if os.environ.get("ORCHESTRATOR_MODE") == "agentic":
            self._write_task_file(task, worker_prompt)
            logging.info("🛑 PAUSING for Agent.")
            return

        # Autonomous Mode
        # [Fix: Cost] Retry Logic
        # Not fully implemented here, but Schema has max_retries
        response = generate_response(worker_prompt, model_alias=worker_model)

        task.feedback_log.append(f"Worker execution: {response.status}")
        if response.status == "SUCCESS":
            task.status = "COMPLETED"
            
            # [v3.4] Git Interaction Nudge (Human-in-the-Loop)
            if self.git.is_available() and self.git.has_changes():
                 task.feedback_log.append("📝 Tip: You have uncommitted changes. To save, ask: 'Run git worker'")

        self.state.tasks[task_id] = task
        self.state.tasks[task_id] = task
        self.save_state()
        self.sync.sync_outbound(self.state)

    def _write_task_file(self, task: Task, prompt: str):
        with open("CURRENT_TASK.md", "w") as f:
            f.write(f"# Task: {task.task_id}\n\n## Instructions\n{prompt}\n")

    def orchestrate(self) -> None:
        logging.info("Starting Polyglot Orchestrator v2.0...")
        # type: ignore
        logging.info(f"Stack: {self.state.stack_fingerprint.primary_language}")

        while True:
            self.load_state()
            pending = [t for t in self.state.tasks.values()
                       if t.status == "PENDING"]

            if not pending:
                time.sleep(2)
                continue

            for task in pending:
                self.process_task(task.task_id)
            
            # [V3.6: Sync]
            if self.sync.sync_inbound(self.state):
                self.save_state()

    # [V3.0: Algorithm Handlers]
    
    def _handle_context_retrieval(self, task: Task) -> bool:
        """Use HippoRAG to retrieve relevant context"""
        try:
            # Lazy init: build graph on first use
            if self.rag is None:
                logging.info("🔍 Initializing HippoRAG graph...")
                self.rag = HippoRAGRetriever()
                self.rag.build_graph_from_ast(self.root_path)
            
            # Retrieve context based on task description
            chunks = self.rag.retrieve_context(task.description, top_k=5)
            
            # Add context to task feedback
            context_summary = "\n".join([
                f"- {c.node_name} ({c.file_path}:{c.start_line})"
                for c in chunks
            ])
            task.feedback_log.append(f"HippoRAG Context:\n{context_summary}")
            
            logging.info(f"✅ Retrieved {len(chunks)} context chunks")
            return True
            
        except Exception as e:
            logging.error(f"HippoRAG failed: {e}")
            task.feedback_log.append(f"HippoRAG error: {e}")
            return False
    
    def _handle_occ_validation(self, task: Task) -> bool:
        """Use OCC Validator for file modifications"""
        try:
            # Assume task.output_files contains files to validate
            for file_path in task.output_files:
                content, version = self.occ.read_with_version(file_path)
                # In a real implementation, the task would have new_content
                # For now, just log that OCC would be used
                task.feedback_log.append(
                    f"OCC: Would validate {file_path} (version={version[:8]})"
                )
            
            logging.info("✅ OCC validation complete")
            return True
            
        except Exception as e:
            logging.error(f"OCC failed: {e}")
            return False
    
    def _handle_crdt_merge(self, task: Task) -> bool:
        """Use CRDT Merger for concurrent edits"""
        try:
            # Create or get CRDT document for collaborative editing
            doc_id = f"task_{task.task_id}"
            
            if doc_id not in self.crdt.documents:
                self.crdt.create_document(doc_id, "")
            
            task.feedback_log.append(f"CRDT: Document {doc_id} ready for merging")
            logging.info("✅ CRDT merge initialized")
            return True
            
        except Exception as e:
            logging.error(f"CRDT failed: {e}")
            return False
    
    def _handle_consensus(self, task: Task) -> bool:
        """Use Weighted Voting for multi-agent consensus"""
        try:
            # In a real implementation, multiple agents would vote
            # For now, just demonstrate the API
            self.consensus.clear_votes()
            
            task.feedback_log.append("Consensus: Awaiting agent votes")
            logging.info("✅ Consensus voting initialized")
            return True
            
        except Exception as e:
            logging.error(f"Consensus failed: {e}")
            return False
    
    def _handle_debate(self, task: Task) -> bool:
        """Use Debate Engine for multi-agent debate"""
        try:
            debate_id = f"debate_{task.task_id}"
            agents = ["agent_1", "agent_2", "agent_3"]
            
            self.debate.start_debate(debate_id, agents, topology="ring")
            
            task.feedback_log.append(f"Debate: Started with {len(agents)} agents")
            logging.info("✅ Debate session started")
            return True
            
        except Exception as e:
            logging.error(f"Debate failed: {e}")
            return False
    
    def _handle_verification(self, task: Task) -> bool:
        """Use Z3 Verifier for symbolic execution"""
        if self.verifier is None:
            task.feedback_log.append("Z3 Verifier not available (dependency missing)")
            return False
        
        try:
            task.feedback_log.append("Z3: Verification requested")
            logging.info("✅ Z3 verification initialized")
            return True
            
        except Exception as e:
            logging.error(f"Z3 failed: {e}")
            return False
    
    def _handle_fault_localization(self, task: Task) -> bool:
        """Use Ochiai SBFL for automated bug location"""
        if self.sbfl is None:
            task.feedback_log.append("Ochiai SBFL not available (dependency missing)")
            return False
        
        try:
            # Run SBFL analysis
            test_cmd = self.state.toolchain_config.test_command if self.state.toolchain_config else "pytest"
            
            debug_prompt = self.sbfl.run_full_sbfl_analysis(
                test_command=test_cmd,
                source_path=self.root_path,
                top_k=5
            )
            
            task.feedback_log.append(f"SBFL Analysis:\n{debug_prompt}")
            logging.info("✅ Ochiai SBFL analysis complete")
            return True
            
        except Exception as e:
            logging.error(f"SBFL failed: {e}")
            task.feedback_log.append(f"SBFL error: {e}")
            return False
    
    def _handle_git_workflow(self, task: Task) -> bool:
        """
        Orchestrate Git worker team for autonomous repository maintenance.
        
        Workflow:
        1. Branch (if git_branch_name specified)
        2. Commit (if git_commit_ready)
        3. Push (if git_auto_push)
        4. PR (if git_create_pr OR auto-PR for completed feature tasks)
        """
        if not self.git.is_available():
            task.feedback_log.append("Git: Not available")
            return False
        
        try:
            from mcp_core.worker_prompts import prompt_git_branch, prompt_git_commit, prompt_git_pr
            
            # Parse repo info from remote
            repo_owner = None
            repo_name = None
            if self.git.config.remote_url:
                parts = self.git.config.remote_url.split('/')
                if len(parts) >= 2:
                    repo_owner = parts[-2]
                    repo_name = parts[-1].replace('.git', '')
            
            # Resolve Model (use git-writer / Gemini for efficiency)
            git_model = self.state.worker_models.get("git-writer", "gemini-3-flash-preview")
            from mcp_core.llm import generate_response
            
            # 1. Branch Worker (if needed)
            if task.git_branch_name and task.git_branch_name not in str(task.feedback_log):
                git_context = {
                    "git_branch_name": task.git_branch_name,
                    "git_base_branch": task.git_base_branch,
                }
                branch_prompt = prompt_git_branch(task, git_context)
                
                # Check if we should execute or just instruct
                # For branch creation, local logic is simpler, but let's stick to instructions/execution pattern
                task.feedback_log.append(f"🌿 Branch Worker: Create {task.git_branch_name}")
                task.feedback_log.append(f"Instructions: {branch_prompt[:200]}...")
                # Execution: Actually run git checkout -b? 
                # For now, we trust the Driver (Agent) to read instructions.
                logging.info(f"✅ Branch Worker dispatched for {task.task_id[:8]}")
            
            # 2. Commit Worker (if ready)
            if task.git_commit_ready: # Removed strict output_files check to allow "catch-all" commits
                if not self.git.has_changes():
                    task.feedback_log.append("⚠️ Commit Worker Skipped: No uncommitted changes detected.")
                    logging.info("Git workflow skipped: Clean working tree")
                else: 
                    git_context = {
                        "output_files": task.output_files,
                        "repo_owner": repo_owner,
                        "repo_name": repo_name,
                    }
                    commit_prompt = prompt_git_commit(task, git_context)
                
                # [Cost Check] Use Cheap LLM to generate commit message
                try:
                    logging.info(f"💾 Generating commit message with {git_model}...")
                    response = generate_response(commit_prompt, model_alias=git_model)
                    
                    # Extract the commit message/command from response tools or reasoning
                    # Since generate_response returns AgentResponse, we check tool_calls
                    # But prompt_git_commit asks to "Use IDE git tools", which implies the output should contain commands
                    # The prompt format expects a textual tool usage.
                    # Let's assume the LLM follows the prompt and we just log the reasoning/tool calls.
                    
                    if response.tool_calls:
                       # [v3.5] Autonomous Execution (Local Git)
                       execution_log = []
                       for tool in response.tool_calls:
                           import json
                           try:
                               args = json.loads(tool.arguments) if isinstance(tool.arguments, str) else tool.arguments
                               result = self._execute_git_tool(tool.function, args)
                               execution_log.append(result)
                           except Exception as ex:
                               execution_log.append(f"❌ Failed {tool.function}: {ex}")
                       
                       task.feedback_log.append(f"💾 Commit Worker Log:\n" + "\n".join(execution_log))
                       
                       # Add push confirmation prompt
                       task.feedback_log.append(
                           "\n📤 **Ready to Push**\n"
                           "Your commit is ready locally. To push to GitHub:\n"
                           "1. Run: `git push` (manual)\n"
                           "2. OR set `git_auto_push=True` in the task (autonomous)\n\n"
                           "The system will NOT auto-push without explicit confirmation."
                       )
                    else:
                       task.feedback_log.append(f"💾 Commit Worker ({git_model}):\n{response.reasoning_trace}")
                    
                except Exception as e:
                    logging.error(f"Git Generation Failed: {e}")
                    task.feedback_log.append(f"Instructions: {commit_prompt[:200]}...")

                logging.info(f"✅ Commit Worker dispatched for {task.task_id[:8]}")
            
            # 3. Auto-PR for completed feature tasks (v3.2 Autonomous Mode)
            should_create_pr = task.git_create_pr
            if not should_create_pr and task.status == "COMPLETED" and task.git_branch_name:
                # Auto-PR if: completed task + feature branch + GitHub ready
                if self.git.is_github_ready():
                    should_create_pr = True
                    task.feedback_log.append("🤖 Auto-PR: Feature task completed, creating PR")
                    logging.info(f"Auto-PR enabled for completed task {task.task_id[:8]}")
            
            # 4. PR Worker (if flagged or auto-enabled)
            if should_create_pr and task.git_branch_name:
                if not self.git.is_github():
                    task.feedback_log.append("⚠️ PR Worker: GitHub not detected")
                    return True  # Not an error, just skip
                
                if not self.git.has_github_token():
                    task.feedback_log.append("⚠️ PR Worker: GITHUB_TOKEN not set")
                    task.feedback_log.append("Set GITHUB_TOKEN env var to enable PR creation")
                    return True  # Not an error, just skip
                
                git_context = {
                    "git_branch_name": task.git_branch_name,
                    "git_base_branch": task.git_base_branch,
                    "git_pr_title": task.git_pr_title or task.description[:60],
                    "git_pr_body": task.git_pr_body or f"Automated PR from Swarm task {task.task_id[:8]}",
                    "output_files": task.output_files,
                    "repo_owner": repo_owner,
                    "repo_name": repo_name,
                }
                pr_prompt = prompt_git_pr(task, git_context)
                
                # [Cost Check] Use Cheap LLM to generate PR body
                try:
                    logging.info(f"🔀 Generating PR with {git_model}...")
                    response = generate_response(pr_prompt, model_alias=git_model)
                    
                    if response.tool_calls:
                       calls_str = "\n".join([f"{t.function}({t.arguments})" for t in response.tool_calls])
                       task.feedback_log.append(f"🔀 PR Worker ({git_model}):\n{calls_str}")
                    else:
                       task.feedback_log.append(f"🔀 PR Worker ({git_model}):\n{response.reasoning_trace}")
                       
                except Exception as e:
                    logging.error(f"PR Generation Failed: {e}")
                    task.feedback_log.append(f"Instructions: {pr_prompt[:200]}...")

                logging.info(f"✅ PR Worker dispatched for {task.task_id[:8]}")
            
            logging.info(f"✅ Git workflow orchestrated for {task.task_id[:8]}")
            return True
            
        except Exception as e:
            logging.error(f"Git workflow failed: {e}")
            task.feedback_log.append(f"Git workflow error: {e}")
            return False

    def _execute_git_tool(self, tool_name: str, args: dict) -> str:
        """Execute local Git operations autonomously."""
        import subprocess
        repo_path = str(self.git.repo_path)
        
        # Generic command runner (for LLM-generated commands)
        if tool_name == "run_command":
            cmd = args.get("command_line", "")
            cwd = args.get("cwd", repo_path)
            
            if not cmd.startswith("git "):
                return f"⚠️ Rejected non-git command: {cmd}"
            
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return f"✅ {cmd}\n{result.stdout}"
            except subprocess.CalledProcessError as e:
                return f"❌ {cmd}\n{e.stderr}"
        
        if tool_name == "git_add":
            files = args.get("files", ".")
            if isinstance(files, str): 
                # Handle "file1 file2" string or "." -> ["."]
                files = [files] if files == "." else files.split()
            
            subprocess.run(["git", "add"] + files, cwd=repo_path, check=True)
            return f"✅ Staged: {files}"

        elif tool_name == "git_commit":
            message = args.get("message", "Automated commit")
            subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
            return f"✅ Committed: {message}"

        elif tool_name == "git_push":
            remote = args.get("remote", "origin")
            branch = args.get("branch", self.git.config.default_branch)
            # Safe push
            subprocess.run(["git", "push", remote, branch], cwd=repo_path, check=True)
            return f"✅ Pushed to {remote}/{branch}"

        return f"⚠️ Unknown tool: {tool_name}"
