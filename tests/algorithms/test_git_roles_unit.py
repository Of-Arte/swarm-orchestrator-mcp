
import pytest
from unittest.mock import MagicMock, patch
from mcp_core.algorithms.git_roles.feature_scout import FeatureScoutRole
from mcp_core.algorithms.git_roles.code_auditor import CodeAuditorRole
from mcp_core.algorithms.git_roles.issue_triage import IssueTriageRole
from mcp_core.algorithms.git_roles.branch_manager import BranchManagerRole
from mcp_core.algorithms.git_roles.project_lifecycle import ProjectLifecycleRole
from mcp_core.algorithms.git_roles import GitRole

class TestFeatureScoutRole:
    @pytest.fixture
    def role(self):
        return FeatureScoutRole()

    def test_trigger_check_no_flag(self, role):
        task = MagicMock()
        task.feature_discovery = False
        assert role.trigger_check(task, {}) is False

    def test_trigger_check_with_flag(self, role):
        task = MagicMock()
        task.feature_discovery = True
        assert role.trigger_check(task, {}) is True

    def test_execute_no_hipporag(self, role):
        task = MagicMock(task_id="test_task")
        # FeatureScoutRole.execute checks for hipporag_client
        context = {"hipporag_client": None, "memory_bank": {}}
        report = role.execute(task, context)
        assert report.status == "COMPLETED"
        assert any("HippoRAG client not available" in w for w in report.warnings)

class TestCodeAuditorRole:
    @pytest.fixture
    def role(self):
        return CodeAuditorRole()

    def test_trigger_check_with_flag(self, role):
        task = MagicMock()
        task.code_audit = True
        assert role.trigger_check(task, {}) is True

    def test_priority_tasks_creation(self, role):
        # CodeAuditorRole has _create_priority_tasks
        findings = [{"severity": "critical", "message": "error"}]
        tasks = role._create_priority_tasks(findings, {})
        assert isinstance(tasks, list)

class TestIssueTriageRole:
    @pytest.fixture
    def role(self):
        return IssueTriageRole()

    def test_trigger_check_with_flag(self, role):
        task = MagicMock()
        task.issue_triage_needed = True
        assert role.trigger_check(task, {}) is True

    def test_priority_calculation(self, role):
        # IssueTriageRole has _calculate_priority(impact, effort)
        assert role._calculate_priority("high", "low") == "P0"
        assert role._calculate_priority("low", "high") == "P3"

class TestBranchManagerRole:
    @pytest.fixture
    def role(self):
        return BranchManagerRole()

    def test_trigger_check_ready_pr(self, role):
        task = MagicMock()
        context = {"pr_status": {"approved": True, "ci_passing": True}}
        assert role.trigger_check(task, context) is True

    def test_is_ready_to_merge(self, role):
        pr = {"approved": True, "ci_passing": True, "mergeable": True}
        assert role._is_ready_to_merge(pr) is True
        
        pr["ci_passing"] = False
        assert role._is_ready_to_merge(pr) is False

class TestProjectLifecycleRole:
    @pytest.fixture
    def role(self):
        return ProjectLifecycleRole()

    def test_trigger_check_bootstrap(self, role):
        task = MagicMock()
        task.project_bootstrap = True
        assert role.trigger_check(task, {}) is True

    def test_trigger_check_update(self, role):
        task = MagicMock()
        task.type = "project_update"
        task.project_bootstrap = False
        assert role.trigger_check(task, {}) is True
