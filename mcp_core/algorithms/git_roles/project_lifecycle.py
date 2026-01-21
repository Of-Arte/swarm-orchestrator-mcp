"""
ProjectLifecycleRole: Autonomous project initialization, updating, and archival.

This role manages the full lifecycle of a project from bootstrap to completion.
"""

from typing import Any, Dict, List
from .base import GitAgentRole, GitRole, ExitReport


class ProjectLifecycleRole(GitAgentRole):
    """
    Autonomous project lifecycle manager.
    
    Responsibilities:
    - Start: Initialize new projects with templates
    - Update: Sync PLAN.md with actual progress
    - Archive: Finalize completed projects
    """
    
    def __init__(self):
        super().__init__(GitRole.PROJECT_LIFECYCLE)
    
    def trigger_check(self, task: Any, context: Dict[str, Any]) -> bool:
        """
        Trigger on project_bootstrap or lifecycle management flags.
        
        Args:
            task: Task object
            context: Execution context
            
        Returns:
            True if lifecycle management should run
        """
        if hasattr(task, 'project_bootstrap') and task.project_bootstrap:
            return True
        
        task_type = getattr(task, 'type', None)
        if task_type in ['project_update', 'project_archive']:
            return True
        
        return False
    
    def execute(self, task: Any, context: Dict[str, Any]) -> ExitReport:
        """
        Execute project lifecycle operation.
        
        Determines operation type (start/update/archive) and delegates.
        
        Args:
            task: Task object
            context: Execution context
            
        Returns:
            ExitReport with operation results
        """
        task_type = getattr(task, 'type', 'project_bootstrap')
        
        if task_type == 'project_bootstrap' or (hasattr(task, 'project_bootstrap') and task.project_bootstrap):
            return self._execute_start(task, context)
        elif task_type == 'project_update':
            return self._execute_update(task, context)
        elif task_type == 'project_archive':
            return self._execute_archive(task, context)
        else:
            return ExitReport(
                task_id=task.task_id if hasattr(task, 'task_id') else "unknown",
                status="BLOCKED",
                warnings=[f"Unknown project lifecycle type: {task_type}"]
            )
    
    def _execute_start(self, task: Any, context: Dict[str, Any]) -> ExitReport:
        """
        Bootstrap a new project.
        
        Steps:
        1. Read global templates from PLAN/memory_bank
        2. Define project spec (name, repo, structure)
        3. Create repository via GitHub
        4. Scaffold initial structure
        5. Seed task_queue with MVP tasks
        6. Log project creation in memory
        """
        warnings = []
        
        # Step 1: Read templates
        templates = self._load_templates(context)
        
        # Step 2: Define project spec
        project_spec = self._generate_project_spec(task, templates, context)
        
        # Step 3: Create repository
        github_client = context.get('github_client')
        if github_client:
            repo_result = self._create_repository(project_spec, github_client)
        else:
            warnings.append("GitHub client not available - repository not created")
            repo_result = None
        
        # Step 4: Scaffold structure
        if repo_result:
            self._scaffold_project(project_spec, repo_result, context)
        
        # Step 5: Seed tasks
        initial_tasks = self._generate_initial_tasks(project_spec, context)
        
        # Step 6: Log creation
        self._log_project_birth(project_spec, context)
        
        return ExitReport(
            task_id=task.task_id if hasattr(task, 'task_id') else "unknown",
            status="COMPLETED",
            remaining_work=f"Created project '{project_spec.get('name')}' with {len(initial_tasks)} initial tasks",
            warnings=warnings
        )
    
    def _execute_update(self, task: Any, context: Dict[str, Any]) -> ExitReport:
        """
        Update existing project status.
        
        Steps:
        1. Fetch current project state
        2. Compare PLAN.md with actual task completion
        3. Generate progress report
        4. Update stakeholder documentation
        """
        project_id = context.get('project_id')
        
        # Fetch state
        current_state = self._get_project_state(project_id, context)
        
        # Sync PLAN.md
        sync_result = self._sync_plan_with_reality(current_state, context)
        
        # Generate report
        report = self._generate_progress_report(current_state, context)
        
        return ExitReport(
            task_id=task.task_id if hasattr(task, 'task_id') else "unknown",
            status="COMPLETED",
            remaining_work=f"Updated project status: {sync_result.get('summary', '')}"
        )
    
    def _execute_archive(self, task: Any, context: Dict[str, Any]) -> ExitReport:
        """
        Archive completed project.
        
        Steps:
        1. Mark remaining tasks as CANCELLED/DEFERRED
        2. Generate final summary
        3. Update PLAN.md with completion status
        4. Mark repo as archived (if applicable)
        """
        project_id = context.get('project_id')
        
        # Handle remaining tasks
        cancelled_tasks = self._cancel_remaining_tasks(project_id, context)
        
        # Final summary
        summary = self._generate_final_summary(project_id, context)
        
        # Update PLAN
        self._finalize_plan(project_id, summary, context)
        
        # Archive repo
        github_client = context.get('github_client')
        if github_client:
            self._archive_repository(project_id, github_client)
        
        return ExitReport(
            task_id=task.task_id if hasattr(task, 'task_id') else "unknown",
            status="COMPLETED",
            remaining_work=f"Archived project with {len(cancelled_tasks)} deferred tasks"
        )
    
    # Helper methods (placeholders)
    
    def _load_templates(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Load project templates from memory_bank."""
        return {}
    
    def _generate_project_spec(self, task: Any, templates: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project specification."""
        return {
            "name": "new-project",
            "description": task.description if hasattr(task, 'description') else "",
            "org": "default-org",
            "template": "python-mcp-server"
        }
    
    def _create_repository(self, spec: Dict[str, Any], github_client) -> Dict[str, Any]:
        """Create GitHub repository."""
        return self._run_async(github_client.create_repository(
            name=spec.get('name', 'new-project'),
            description=spec.get('description', ''),
            private=True
        ))

    def _archive_repository(self, project_id: str, github_client):
        """Mark repository as archived."""
        # Simple heuristic: project_id might be the repo name
        return self._run_async(github_client.archive_repository(
            owner="AgentAgony", # Default
            repo=project_id
        ))
