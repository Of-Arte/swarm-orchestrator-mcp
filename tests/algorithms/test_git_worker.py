import os
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from mcp_core.algorithms.git_worker import GitWorker, GitConfig, GitProvider

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def mock_path_exists():
    with patch("pathlib.Path.exists") as mock_exists:
        yield mock_exists

@pytest.fixture
def mock_path_read_text():
    with patch("pathlib.Path.read_text") as mock_read:
        yield mock_read

@pytest.fixture
def mock_subprocess():
    with patch("subprocess.run") as mock_run:
        yield mock_run

# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_detect_no_git_dir(mock_path_exists):
    """Test detection when .git directory does not exist."""
    # Setup: .git does not exist
    mock_path_exists.return_value = False
    
    worker = GitWorker("/tmp/fake_repo")
    
    assert worker.config.provider == GitProvider.NONE
    assert worker.is_available() is False
    assert worker.repo_path == Path("/tmp/fake_repo").resolve()

def test_detect_local_git_no_remote(mock_path_exists, mock_path_read_text):
    """Test detection of local git repo without remote."""
    # Setup: .git exists, .git/config exists
    mock_path_exists.return_value = True
    mock_path_read_text.return_value = "[core]\n\trepositoryformatversion = 0"
    
    worker = GitWorker("/tmp/fake_repo")
    
    assert worker.config.provider == GitProvider.LOCAL
    assert worker.is_available() is True
    assert worker.has_remote() is False

def test_detect_github_remote(mock_path_exists, mock_path_read_text):
    """Test detection of GitHub remote from config."""
    # Setup: .git exists
    mock_path_exists.return_value = True
    # Config content with GitHub URL
    mock_path_read_text.return_value = """
[core]
    repositoryformatversion = 0
[remote "origin"]
    url = https://github.com/test-user/test-repo.git
    fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
    remote = origin
    merge = refs/heads/main
"""
    
    worker = GitWorker("/tmp/fake_repo")
    
    assert worker.config.provider == GitProvider.GITHUB
    assert worker.config.remote_url == "https://github.com/test-user/test-repo.git"
    assert worker.config.default_branch == "main"
    assert worker.is_github() is True
    assert worker.has_remote() is True

def test_detect_gitlab_remote(mock_path_exists, mock_path_read_text):
    """Test detection of GitLab remote."""
    mock_path_exists.return_value = True
    mock_path_read_text.return_value = """
[remote "origin"]
    url = git@gitlab.com:course-group/project.git
"""
    
    worker = GitWorker("/tmp/fake_repo")
    
    assert worker.config.provider == GitProvider.GITLAB
    assert worker.is_gitlab() is True

def test_has_changes_true(mock_path_exists, mock_path_read_text, mock_subprocess):
    """Test has_changes when git status reports modifications."""
    mock_path_exists.return_value = True
    mock_path_read_text.return_value = "" # Minimal config
    
    # Mock subprocess returning output means changes exist
    mock_subprocess.return_value.stdout = " M file.py\n?? new_file.py"
    
    worker = GitWorker("/tmp/fake_repo")
    
    assert worker.has_changes() is True
    mock_subprocess.assert_called_with(
        ["git", "status", "--porcelain"],
        cwd=str(Path("/tmp/fake_repo").resolve()),
        capture_output=True,
        text=True,
        timeout=5
    )

def test_has_changes_false(mock_path_exists, mock_subprocess):
    """Test has_changes when repo is clean."""
    mock_path_exists.return_value = True
    mock_subprocess.return_value.stdout = "" # Empty output
    
    worker = GitWorker("/tmp/fake_repo")
    assert worker.has_changes() is False

@patch.dict(os.environ, {"GITHUB_TOKEN": "fake_token"})
def test_is_github_ready(mock_path_exists, mock_path_read_text):
    """Test is_github_ready with provider and token."""
    mock_path_exists.return_value = True
    mock_path_read_text.return_value = '[remote "origin"]\nurl = https://github.com/user/repo'
    
    worker = GitWorker("/tmp/fake_repo")
    
    assert worker.is_github() is True
    assert worker.has_github_token() is True
    assert worker.is_github_ready() is True

@patch.dict(os.environ, {}, clear=True)
def test_is_github_ready_no_token(mock_path_exists, mock_path_read_text):
    """Test is_github_ready without token."""
    mock_path_exists.return_value = True
    mock_path_read_text.return_value = '[remote "origin"]\nurl = https://github.com/user/repo'
    
    worker = GitWorker("/tmp/fake_repo")
    
    assert worker.is_github() is True
    assert worker.has_github_token() is False
    assert worker.is_github_ready() is False

def test_get_workflow_instructions_none(mock_path_exists):
    """Test instructions when no git repo detected."""
    mock_path_exists.return_value = False
    worker = GitWorker("/tmp/fake_repo")
    assert worker.get_workflow_instructions() == ""

@patch.dict(os.environ, {"GITHUB_TOKEN": "fake_token"})
def test_get_workflow_instructions_github(mock_path_exists, mock_path_read_text):
    """Test instructions for GitHub with token."""
    mock_path_exists.return_value = True
    mock_path_read_text.return_value = '[remote "origin"]\nurl = https://github.com/user/repo'
    
    worker = GitWorker("/tmp/fake_repo")
    instructions = worker.get_workflow_instructions()
    
    assert "git_status" in instructions
    assert "create_pull_request: Create PR for review (GitHub) ✅" in instructions
    assert "git_create_pr=True" in instructions

@patch.dict(os.environ, {}, clear=True)
def test_get_workflow_instructions_github_no_token(mock_path_exists, mock_path_read_text):
    """Test instructions for GitHub without token."""
    mock_path_exists.return_value = True
    mock_path_read_text.return_value = '[remote "origin"]\nurl = https://github.com/user/repo'
    
    worker = GitWorker("/tmp/fake_repo")
    instructions = worker.get_workflow_instructions()
    
    assert "Requires GITHUB_TOKEN env var" in instructions
