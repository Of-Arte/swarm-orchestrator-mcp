
import pytest
from unittest.mock import MagicMock, patch
from mcp_core.swarm_schemas import Task
from mcp_core.algorithms.git_role_dispatcher import GitRoleDispatcher
from mcp_core.algorithms.git_roles import GitRole, ExitReport

class TestGitRolesIntegration:
    
    @pytest.fixture
    def mock_orchestrator(self):
        orchestrator = MagicMock()
        orchestrator.state.active_context = {"project_name": "test_project"}
        orchestrator.rag = MagicMock()
        orchestrator.git = MagicMock()
        orchestrator.git.is_available.return_value = True
        return orchestrator

    def test_dispatcher_initialization(self, mock_orchestrator):
        dispatcher = GitRoleDispatcher(mock_orchestrator)
        assert len(dispatcher.roles) == 5
        assert GitRole.FEATURE_SCOUT in dispatcher.roles
        assert GitRole.CODE_AUDITOR in dispatcher.roles

    def test_dispatcher_dispatch_feature_discovery(self, mock_orchestrator):
        dispatcher = GitRoleDispatcher(mock_orchestrator)
        task = Task(description="Find new features", feature_discovery=True, status="PENDING")
        
        # Mock FeatureScoutRole.execute
        with patch.object(dispatcher.roles[GitRole.FEATURE_SCOUT], 'execute') as mock_execute:
            mock_execute.return_value = MagicMock(status="COMPLETED", remaining_work="Created 2 proposals")
            
            reports = dispatcher.dispatch(task)
            
            assert len(reports) == 1
            assert mock_execute.called
            assert reports[0].status == "COMPLETED"

    def test_dispatcher_no_trigger(self, mock_orchestrator):
        dispatcher = GitRoleDispatcher(mock_orchestrator)
        task = Task(description="Simple task", status="PENDING")
        
        reports = dispatcher.dispatch(task)
        assert len(reports) == 0

    def test_orchestrator_integration_workflow(self, mock_orchestrator):
        # This test checks if the orchestrator actually calls the dispatcher 
        # based on the flags we added.
        from mcp_core.orchestrator_loop import Orchestrator
        
        with patch('mcp_core.orchestrator_loop.ProjectProfile'), \
             patch('mcp_core.orchestrator_loop.GitWorker'), \
             patch('mcp_core.algorithms.git_role_dispatcher.GitRoleDispatcher') as MockDispatcher:
            
            # Setup mock dispatcher
            mock_dispatcher_instance = MockDispatcher.return_value
            mock_dispatcher_instance.dispatch.return_value = [
                ExitReport(task_id="test", status="COMPLETED", remaining_work="Audit done")
            ]
            
            orch = Orchestrator(root_path=".")
            orch._git = MagicMock()
            orch._git.is_available.return_value = True
            
            task = Task(description="Audit code", code_audit=True, status="PENDING")
            
            result = orch._handle_git_workflow(task)
            
            assert result is True
            assert mock_dispatcher_instance.dispatch.called
            assert any("🤖 GitRole" in log for log in task.feedback_log)
