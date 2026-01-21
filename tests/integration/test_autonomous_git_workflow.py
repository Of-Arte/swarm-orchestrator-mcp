
import pytest
from unittest.mock import MagicMock, patch
from mcp_core.swarm_schemas import Task
from mcp_core.algorithms.git_role_dispatcher import GitRoleDispatcher
from mcp_core.algorithms.git_roles import GitRole, ExitReport

class TestAutonomousGitWorkflow:
    
    @pytest.fixture
    def mock_orchestrator(self):
        orchestrator = MagicMock()
        orchestrator.state.active_context = {"project_name": "test_project"}
        orchestrator.rag = MagicMock()
        orchestrator.git = MagicMock()
        orchestrator.git.is_available.return_value = True
        return orchestrator

    def test_full_autonomous_chain(self, mock_orchestrator):
        """
        Test a chain of roles: FeatureScout -> IssueTriage -> CodeAuditor
        """
        dispatcher = GitRoleDispatcher(mock_orchestrator)
        
        # We'll trigger multiple roles via flags
        task = Task(
            description="Autonomous ecosystem maintenance",
            feature_discovery=True,
            code_audit=True,
            issue_triage_needed=True,
            status="PENDING"
        )
        
        # Mock role executions
        with patch.object(dispatcher.roles[GitRole.FEATURE_SCOUT], 'execute') as mock_scout, \
             patch.object(dispatcher.roles[GitRole.ISSUE_TRIAGE], 'execute') as mock_triage, \
             patch.object(dispatcher.roles[GitRole.CODE_AUDITOR], 'execute') as mock_audit:
            
            mock_scout.return_value = ExitReport(task_id=task.task_id, status="COMPLETED", remaining_work="Scouted 1 feature")
            mock_triage.return_value = ExitReport(task_id=task.task_id, status="COMPLETED", remaining_work="Triaged 2 issues")
            mock_audit.return_value = ExitReport(task_id=task.task_id, status="COMPLETED", remaining_work="Audited 3 files")
            
            reports = dispatcher.dispatch(task)
            
            assert len(reports) == 3
            assert mock_triage.called
            assert mock_scout.called
            assert mock_audit.called
            
            # Check execution order (ProjectLifecycle, IssueTriage, FeatureScout, CodeAuditor, BranchManager)
            # In our case: Triage -> Scout -> Audit
            assert reports[0].remaining_work == "Triaged 2 issues"
            assert reports[1].remaining_work == "Scouted 1 feature"
            assert reports[2].remaining_work == "Audited 3 files"

    def test_lifecycle_to_manager_flow(self, mock_orchestrator):
        """
        Test ProjectLifecycle and BranchManager triggers.
        """
        dispatcher = GitRoleDispatcher(mock_orchestrator)
        
        task = Task(
            description="Project maintenance",
            project_bootstrap=True,
            status="PENDING"
        )
        
        # Add context for BranchManager
        mock_orchestrator.state.active_context = {
            "pr_status": {"approved": True, "ci_passing": True},
            "pr_number": 42
        }
        # Update dispatcher prepare_context to use mock_orchestrator's active_context
        # (It already does in implementation)
        
        with patch.object(dispatcher.roles[GitRole.PROJECT_LIFECYCLE], 'execute') as mock_lifecycle, \
             patch.object(dispatcher.roles[GitRole.BRANCH_MANAGER], 'execute') as mock_manager:
            
            mock_lifecycle.return_value = ExitReport(task_id=task.task_id, status="COMPLETED", remaining_work="Bootstrap done")
            mock_manager.return_value = ExitReport(task_id=task.task_id, status="COMPLETED", remaining_work="Merged PR #42")
            
            reports = dispatcher.dispatch(task)
            
            assert len(reports) == 2
            assert reports[0].remaining_work == "Bootstrap done"
            assert reports[1].remaining_work == "Merged PR #42"
