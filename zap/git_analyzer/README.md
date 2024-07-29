# zap Git Analyzer Documentation

## Quick Start

Get started with the zap Git Analyzer to perform a comprehensive exploration of a Git repository.

1. **Set Up the Environment**: Install dependencies using Poetry.
    ```bash
    poetry install
    ```

2. **Run the Analyzer**: Use the provided script to analyze your repository.
    ```bash
    python -m zap.git_analyzer.analyze_repo /path/to/your/git/repository
    ```

   This command will analyze the specified Git repository and print the exploration results.

## Core Concepts

### GitRepo

The `GitRepo` class interacts with the Git repository to fetch tracked files, file contents, Git status, and recent commits.

### Dependency Parsers

Parsers extract dependency information from various file types:
- `PythonParser` for `requirements.txt` and `pyproject.toml`
- `JavaScriptParser` for `package.json`
- `DotNetParser` for `.csproj`
- `PipfileParser` for `Pipfile`

### RepoExplorer

The `RepoExplorer` class orchestrates the exploration of the Git repository, gathering information about the project structure, Git status, recent commits, and file change statistics.

## Examples and Use Cases

### Analyzing a Git Repository

Run the following code to analyze a Python or DotNet project repository:

```python
import asyncio
from zap.git_analyzer.analyzer import analyze_repo

async def analyze_repo_example():
    result = await analyze_repo("/path/to/your/repo")
    print(result)

asyncio.run(analyze_repo_example())
```

### Custom Configuration

Create a custom configuration for the analyzer:

1. **Configuration File (YAML)**:
    ```yaml
    commit_limit: 20
    most_changed_files_limit: 15
    least_changed_files_limit: 5
    log_level: DEBUG
    ```

2. **Load and Use Configuration**:
    ```python
    import asyncio
    from zap.git_analyzer.config import GitAnalyzerConfig
    from zap.git_analyzer.analyzer import analyze_repo

    async def analyze_with_custom_config():
        config = GitAnalyzerConfig.from_file("/path/to/config.yaml")
        result = await analyze_repo("/path/to/repo", config)
        print(result)

    asyncio.run(analyze_with_custom_config())
    ```

## Component Guide

### GitRepo

**Description**: Fetch information from the Git repository.

**Usage**:
```python
from zap.git_analyzer.repo.git_repo import GitRepo

repo = GitRepo("/path/to/repo")

async def repo_operations():
    tracked_files = await repo.get_tracked_files()
    content = await repo.get_file_content("README.md")
    print(tracked_files)
    print(content)

asyncio.run(repo_operations())
```

### PythonParser

**Description**: Parses dependencies from `requirements.txt` and `pyproject.toml`.

**Usage**:
```python
from zap.git_analyzer.parsers.python import PythonParser

parser = PythonParser()

async def parse_python_dependencies():
    requirements_content = '''
    flask==2.0.1
    requests>=2.25.1
    '''
    pyproject_content = '''
    [tool.poetry.dependencies]
    flask = "^2.0.1"
    requests = "^2.25.1"
    '''
    req_result = await parser._parse_requirements(requirements_content, "requirements.txt")
    proj_result = await parser._parse_pyproject_toml(pyproject_content, "pyproject.toml")
    print(req_result)
    print(proj_result)

asyncio.run(parse_python_dependencies())
```

### JavaScriptParser

**Description**: Parses dependencies from `package.json`.

**Usage**:
```python
from zap.git_analyzer.parsers.javascript import JavaScriptParser

parser = JavaScriptParser()

async def parse_javascript_dependencies():
    content = '''
    {
      "dependencies": {
        "react": "^17.0.2"
      },
      "devDependencies": {
        "webpack": "^5.24.4"
      }
    }
    '''
    result = await parser.parse(content, "package.json")
    print(result)

asyncio.run(parse_javascript_dependencies())
```

### RepoExplorer

**Description**: Orchestrates the exploration of a Git repository.

**Usage**:
```python
from zap.git_analyzer.repo.git_repo import GitRepo
from zap.git_analyzer.repo.repo_explorer import RepoExplorer
from zap.git_analyzer.config import GitAnalyzerConfig

async def explore_repository():
    git_repo = GitRepo("/path/to/repo")
    config = GitAnalyzerConfig()
    explorer = RepoExplorer(git_repo, config)
    result = await explorer.explore()
    print(result)

asyncio.run(explore_repository())
```

## Configuration

### Example Configuration File (YAML)
```yaml
commit_limit: 20
most_changed_files_limit: 15
least_changed_files_limit: 5
log_level: DEBUG
```

### Loading Configuration
```python
from zap.git_analyzer.config import GitAnalyzerConfig

config = GitAnalyzerConfig.from_file("/path/to/config.yaml")
print(config)
```

## Troubleshooting

### Common Issues and Solutions

#### Unsupported File Type

**Error Message**:
```
ParserError: Unsupported file type: somefile.unknown
```

**Solution**: Only attempt to parse supported file types (`requirements.txt`, `pyproject.toml`, `package.json`, `.csproj`, `Pipfile`).

#### Invalid JSON/TOML/XML

**Error Message**:
```
ValueError: Invalid JSON in file: package.json
```
or
```
ValueError: Invalid TOML in file: pyproject.toml
```

**Solution**: Check the file for syntax errors or structural issues.
