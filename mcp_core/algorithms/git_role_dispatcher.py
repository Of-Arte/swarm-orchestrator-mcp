"""
GitRoleDispatcher: Central coordinator for role-based Git operations.
"""

import logging
from typing import List, Dict, Any, Optional
from mcp_core.swarm_schemas import Task
from mcp_core.algorithms.git_roles import GitRole, ExitReport, HandoffProtocol
from mcp_core.algorithms.git_roles.feature_scout import FeatureScoutRole
from mcp_core.algorithms.git_roles.code_auditor import CodeAuditorRole
from mcp_core.algorithms.git_roles.issue_triage import IssueTriageRole
from mcp_core.algorithms.git_roles.branch_manager import BranchManagerRole
from mcp_core.algorithms.git_roles.project_lifecycle import ProjectLifecycleRole


class GitRoleDispatcher:
    """
    Central dispatcher for autonomous Git agent roles.
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.roles = {
            GitRole.FEATURE_SCOUT: FeatureScoutRole(),
            GitRole.CODE_AUDITOR: CodeAuditorRole(),
            GitRole.ISSUE_TRIAGE: IssueTriageRole(),
            GitRole.BRANCH_MANAGER: BranchManagerRole(),
            GitRole.PROJECT_LIFECYCLE: ProjectLifecycleRole()
        }
    
    def dispatch(self, task: Task) -> List[ExitReport]:
        """
        Execute all triggered roles for the given task.
        """
        reports = []
        context = self._prepare_context(task)
        
        # Check and execute each role sequentially
        # Order matters: lifecycle/triage -> scout -> auditor -> manager
        execution_order = [
            GitRole.PROJECT_LIFECYCLE,
            GitRole.ISSUE_TRIAGE,
            GitRole.FEATURE_SCOUT,
            GitRole.CODE_AUDITOR,
            GitRole.BRANCH_MANAGER
        ]
        
        for role_key in execution_order:
            role = self.roles[role_key]
            if role.trigger_check(task, context):
                logging.info(f"🚀 Dispatching Git Role: {role_key.value}")
                try:
                    report = role.execute(task, context)
                    reports.append(report)
                    
                    # If role generated a handoff, handle it
                    # (In a real implementation, this might recursive or loop)
                    logging.info(f"✅ {role_key.value} completed with status: {report.status}")
                except Exception as e:
                    logging.error(f"❌ {role_key.value} failed: {e}")
                    reports.append(ExitReport(
                        task_id=task.task_id,
                        status="FAILED",
                        warnings=[str(e)]
                    ))
        
        return reports
    
    def _prepare_context(self, task: Task) -> Dict[str, Any]:
        """
        Prepare execution context for roles.
        Merges active_context (memory_bank) into top-level for easier access.
        """
        active_context = self.orchestrator.state.active_context or {}
        context = {
            "memory_bank": active_context,
            "hipporag_client": self.orchestrator.rag,
            "github_client": getattr(self.orchestrator, 'github_client', None),
            "git_worker": self.orchestrator.git,
            "orchestrator": self.orchestrator
        }
        # Merge active_context keys into top-level for convenience in trigger_check
        context.update(active_context)
        return context
