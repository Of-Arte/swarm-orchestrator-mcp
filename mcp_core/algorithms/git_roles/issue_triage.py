"""
IssueTriageRole: Autonomous issue prioritization and assignment.

This role investigates open issues, assigns priorities based on impact and effort,
and updates task queues with proper dependencies.
"""

from typing import Any, Dict, List
from .base import GitAgentRole, GitRole, ExitReport


class IssueTriageRole(GitAgentRole):
    """
    Autonomous issue triage agent.
    
    Responsibilities:
    - Fetch open issues from GitHub
    - Query HippoRAG for related code context
    - Assign priorities (P0-P3) based on impact/effort
    - Update labels and milestones
    - Insert tasks into task_queue with dependencies
    """
    
    def __init__(self):
        super().__init__(GitRole.ISSUE_TRIAGE)
    
    def trigger_check(self, task: Any, context: Dict[str, Any]) -> bool:
        """
        Trigger on issue_triage_needed flag or new issue creation.
        
        Args:
            task: Task object
            context: Execution context
            
        Returns:
            True if triage should run
        """
        if hasattr(task, 'issue_triage_needed') and task.issue_triage_needed:
            return True
        
        if context.get('new_issues_count', 0) > 0:
            return True
        
        return False
    
    def execute(self, task: Any, context: Dict[str, Any]) -> ExitReport:
        """
        Execute issue triage workflow.
        
        Steps:
        1. Fetch open issues
        2. Analyze each issue for context
        3. Assign priority
        4. Update labels/milestones
        5. Create tasks with dependencies
        
        Args:
            task: Task object
            context: Execution context with github_client
            
        Returns:
            ExitReport with triage results
        """
        warnings = []
        triaged_issues = []
        
        # Step 1: Fetch open issues
        github_client = context.get('github_client')
        if not github_client:
            warnings.append("GitHub client not available")
            return ExitReport(
                task_id=task.task_id if hasattr(task, 'task_id') else "unknown",
                status="BLOCKED",
                warnings=warnings
            )
        
        open_issues = self._fetch_open_issues(github_client, context)
        
        # Step 2-4: Process each issue
        for issue in open_issues:
            triage_result = self._triage_issue(issue, context)
            triaged_issues.append(triage_result)
            
            # Update GitHub
            self._update_issue_metadata(issue, triage_result, github_client)
        
        # Step 5: Create tasks
        created_tasks = self._create_tasks_from_issues(triaged_issues, context)
        
        return ExitReport(
            task_id=task.task_id if hasattr(task, 'task_id') else "unknown",
            status="COMPLETED",
            remaining_work=f"Triaged {len(triaged_issues)} issues, created {len(created_tasks)} tasks",
            warnings=warnings
        )
    
    def _fetch_open_issues(self, github_client, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch open issues from GitHub."""
        repo_owner = context.get('repo_owner', 'AgentAgony')
        repo_name = context.get('repo_name', 'swarm')
        
        issues = self._run_async(github_client.list_issues(
            owner=repo_owner,
            repo=repo_name,
            state="open"
        ))
        return issues
    
    def _triage_issue(self, issue: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Triage a single issue.
        
        Steps:
        1. Read description and comments
        2. Query HippoRAG for related code
        3. Estimate impact and effort
        4. Assign priority
        
        Returns:
            Triage result with priority, milestone, labels
        """
        issue_id = issue.get('number')
        title = issue.get('title', '')
        body = issue.get('body', '')
        
        # Query HippoRAG for context
        hipporag = context.get('hipporag_client')
        related_code = []
        if hipporag:
            related_code = self._find_related_code(title, body, hipporag)
        
        # Estimate impact and effort
        impact = self._estimate_impact(issue, related_code)
        effort = self._estimate_effort(issue, related_code)
        
        # Assign priority
        priority = self._calculate_priority(impact, effort)
        
        return {
            "issue_id": issue_id,
            "priority": priority,
            "labels": self._suggest_labels(issue, related_code),
            "milestone": self._suggest_milestone(priority, context),
            "estimated_effort": effort
        }
    
    def _find_related_code(self, title: str, body: str, hipporag) -> List[str]:
        """Find code related to the issue using HippoRAG."""
        # Placeholder: would query graph for relevant modules
        return []
    
    def _estimate_impact(self, issue: Dict[str, Any], related_code: List[str]) -> str:
        """Estimate impact level (high/medium/low)."""
        # Placeholder: would analyze affected systems
        return "medium"
    
    def _estimate_effort(self, issue: Dict[str, Any], related_code: List[str]) -> str:
        """Estimate effort level (high/medium/low)."""
        # Placeholder: would analyze complexity
        return "medium"
    
    def _calculate_priority(self, impact: str, effort: str) -> str:
        """
        Calculate priority based on impact/effort matrix.
        
        Returns:
            Priority string (P0-P3)
        """
        # Simple heuristic: high impact + low effort = highest priority
        if impact == "high" and effort == "low":
            return "P0"
        elif impact == "high":
            return "P1"
        elif impact == "medium":
            return "P2"
        else:
            return "P3"
    
    def _suggest_labels(self, issue: Dict[str, Any], related_code: List[str]) -> List[str]:
        """Suggest appropriate labels for the issue."""
        # Placeholder: would analyze issue type and scope
        return []
    
    def _suggest_milestone(self, priority: str, context: Dict[str, Any]) -> str:
        """Suggest appropriate milestone based on priority."""
        # Placeholder: would map to active milestones
        return "Backlog"
    
    def _update_issue_metadata(self, issue: Dict[str, Any], triage: Dict[str, Any], github_client):
        """Update issue labels and milestone on GitHub."""
        # Placeholder for real update call - GitHub MCP would need add_labels_to_issue etc.
        # For now, we'll log the intention
        logging.info(f"Triage: Would update Issue #{issue.get('number')} with labels {triage['labels']} and milestone {triage['milestone']}")
        pass
    
    def _create_tasks_from_issues(self, triaged_issues: List[Dict[str, Any]], context: Dict[str, Any]) -> List[str]:
        """Create tasks in task_queue from triaged issues."""
        # Placeholder: would insert into project_profile.tasks
        return []
