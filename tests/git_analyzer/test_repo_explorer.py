import os
from unittest.mock import Mock

import pytest

from zap.git_analyzer.config import GitAnalyzerConfig
from zap.git_analyzer.repo.git_repo import GitRepo
from zap.git_analyzer.repo.repo_explorer import RepoExplorer


@pytest.fixture
def sample_repo(temp_git_repo):
    # Create a sample repository structure
    files = {
        "requirements.txt": "requests==2.25.1\nnumpy==1.20.1",
        "src/main.py": 'print("Hello, World!")',
        "tests/test_main.py": "def test_main(): pass",
        "package.json": '{"dependencies": {"express": "^4.17.1"}}',
    }

    for file_path, content in files.items():
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(os.path.join(temp_git_repo.path, dir_path), exist_ok=True)
        with open(os.path.join(temp_git_repo.path, file_path), "w") as f:
            f.write(content)

    os.chdir(temp_git_repo.path)
    os.system("git add .")
    os.system('git commit -m "Initial commit"')

    return temp_git_repo


@pytest.fixture
def mock_git_repo():
    return Mock(spec=GitRepo)


@pytest.fixture
def config():
    return GitAnalyzerConfig()


@pytest.mark.asyncio
async def test_repo_explorer_explore(sample_repo, config):
    git_repo = GitRepo(sample_repo.path)
    explorer = RepoExplorer(git_repo, config)
    result = await explorer.explore()
    assert result.project_info is not None
    assert result.relevant_files is not None
    assert result.git_status is not None
    assert result.recent_commits is not None
    assert result.most_changed_files is not None
    assert result.least_changed_files is not None
    assert result.file_change_count is not None


@pytest.mark.asyncio
async def test_repo_explorer_with_mocked_git_repo(mock_git_repo, config):
    mock_git_repo.path = "/mock/path"
    mock_git_repo.get_tracked_files.return_value = ["file1.py", "file2.py"]
    mock_git_repo.get_file_content.return_value = "Content"
    mock_git_repo.get_status.return_value = {"new": [], "modified": [], "deleted": []}
    mock_git_repo.get_recent_commits.return_value = []
    mock_git_repo.get_file_change_count.return_value = {"file1.py": 1, "file2.py": 2}

    explorer = RepoExplorer(mock_git_repo, config)
    result = await explorer.explore()

    assert result.project_info is not None
    assert result.relevant_files is not None
    assert result.git_status is not None
    assert result.recent_commits is not None
    assert result.most_changed_files is not None
    assert result.least_changed_files is not None
    assert result.file_change_count is not None
    mock_git_repo.get_tracked_files.assert_called_once()
    mock_git_repo.get_status.assert_called_once()
    mock_git_repo.get_recent_commits.assert_called_once()
    mock_git_repo.get_file_change_count.assert_called_once()
