import os

import pytest

from zap.git_analyzer import GitAnalyzer
from zap.git_analyzer.config import GitAnalyzerConfig


@pytest.fixture
def complex_repo(temp_git_repo):
    # Create a more complex repository structure
    files = {
        "requirements.txt": "requests==2.25.1\nnumpy==1.20.1",
        "src/main.py": 'print("Hello, World!")',
        "tests/test_main.py": "def test_main(): pass",
        "package.json": '{"dependencies": {"express": "^4.17.1"}}',
        "Pipfile": '[packages]\nrequests = "*"',
        "project.csproj": '<Project><ItemGroup><PackageReference Include="Newtonsoft.Json" Version="12.0.3" '
        "/></ItemGroup></Project>",
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

    # Create a new branch and add a file
    os.system("git branch feature-branch")
    os.system("git checkout feature-branch")
    with open("feature.txt", "w") as f:
        f.write("New feature")
    os.system("git add feature.txt")
    os.system('git commit -m "Add feature"')

    # Switch back to main branch and create a merge commit
    os.system("git checkout master")  # Use 'master' instead of 'main'
    os.system('git merge feature-branch --no-ff -m "Merge feature branch"')

    return temp_git_repo


@pytest.mark.asyncio
async def test_integration_complex_repo(complex_repo):
    config = GitAnalyzerConfig()
    analyzer = GitAnalyzer(complex_repo.path, config)
    result = await analyzer.analyze()

    assert result.project_info is not None
    assert result.relevant_files is not None
    assert result.git_status is not None
    assert result.recent_commits is not None
    assert result.most_changed_files is not None
    assert result.least_changed_files is not None
    assert result.file_change_count is not None

    # Check if all dependency files are detected
    assert "requirements.txt" in result.relevant_files
    assert "package.json" in result.relevant_files
    assert "Pipfile" in result.relevant_files
    assert "project.csproj" in result.relevant_files

    # Check if dependencies are correctly parsed
    dependencies = result.project_info.dependencies
    assert any("requests" in dep.dependencies for dep in dependencies.values())
    assert any("express" in dep.dependencies for dep in dependencies.values())
    assert any("Newtonsoft.Json" in dep.dependencies for dep in dependencies.values())

    # Check if commits are detected
    assert len(result.recent_commits) >= 2  # Initial commit and merge commit

    # Check if branches are detected (implicitly through commits)
    assert any(
        "Merge feature branch" in commit.message for commit in result.recent_commits
    )


@pytest.mark.asyncio
async def test_integration_empty_repo(temp_git_repo):
    config = GitAnalyzerConfig()
    analyzer = GitAnalyzer(temp_git_repo.path, config)
    result = await analyzer.analyze()

    assert result.project_info is not None
    assert result.relevant_files is not None
    assert result.git_status is not None
    assert result.recent_commits is not None
    assert result.most_changed_files is not None
    assert result.least_changed_files is not None
    assert result.file_change_count is not None

    assert len(result.project_info.dependencies) == 0
    assert len(result.relevant_files) == 0
    assert len(result.recent_commits) == 0
    assert len(result.file_change_count) == 0
