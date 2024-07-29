import os

import pytest

from zap.git_analyzer.config import GitAnalyzerConfig
from zap.git_analyzer.repo.git_repo import GitRepo
from zap.git_analyzer.repo.repo_explorer import RepoExplorer


@pytest.fixture
def complex_nested_repo(temp_git_repo):
    # Create a complex nested repository structure with different dependency management in each directory
    files = {
        'requirements.txt': 'requests==2.25.1\nnumpy==1.20.1',
        'src/main.py': 'print("Hello, World!")',
        'src/package.json': '{"dependencies": {"express": "^4.17.1"}}',
        'src/lib/Pipfile': '[packages]\ndjango = "*"',
        'tests/test_main.py': 'def test_main(): pass',
        'docs/conf.py': 'extensions = []',
        'apps/webapp/package.json': '{"dependencies": {"react": "^17.0.2"}}',
        'services/microservice/requirements.txt': 'flask==2.0.1',
        'libs/dotnet/project.csproj': '<Project><ItemGroup><PackageReference Include="Newtonsoft.Json" '
                                      'Version="13.0.1" /></ItemGroup></Project>'
    }

    for file_path, content in files.items():
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(os.path.join(temp_git_repo.path, dir_path), exist_ok=True)
        with open(os.path.join(temp_git_repo.path, file_path), 'w') as f:
            f.write(content)

    os.chdir(temp_git_repo.path)
    os.system('git add .')
    os.system('git commit -m "Initial commit with complex structure"')

    return temp_git_repo


@pytest.mark.asyncio
async def test_repo_explorer_complex_structure(complex_nested_repo):
    git_repo = GitRepo(complex_nested_repo.path)
    config = GitAnalyzerConfig()
    explorer = RepoExplorer(git_repo, config)
    result = await explorer.explore()

    # Check if all dependency files are detected
    expected_files = [
        'requirements.txt',
        'src/package.json',
        'src/lib/Pipfile',
        'apps/webapp/package.json',
        'services/microservice/requirements.txt',
        'libs/dotnet/project.csproj'
    ]
    for file in expected_files:
        assert file in result.relevant_files, f"{file} not found in relevant_files"

    # Check if dependencies are correctly parsed
    dependencies = result.project_info.dependencies
    expected_dependencies = [
        'requests', 'express', 'django', 'react', 'flask', 'Newtonsoft.Json'
    ]
    for dep in expected_dependencies:
        assert any(
            dep in dep_info.dependencies for dep_info in dependencies.values()), f"{dep} not found in dependencies"

    # Check if the structure is correctly analyzed
    assert len(result.file_change_count) >= len(expected_files), "Not all expected files were analyzed"
