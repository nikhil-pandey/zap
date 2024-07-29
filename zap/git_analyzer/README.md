# Git Analyzer

Git Analyzer is a powerful Python library for analyzing Git repositories. It provides insights into project structure, dependencies, commit history, and file changes.

## Features

- Analyze project structure and dependencies
- Examine commit history
- Identify most and least changed files
- Get current Git status
- Customizable analysis depth and focus
- Support for various configuration file formats (JSON, YAML, TOML)

## Configuration

Git Analyzer allows you to customize various aspects of the analysis through configuration settings. You can provide the configuration as a dictionary, a file path (JSON, YAML, TOML), or a `GitAnalyzerConfig` dataclass instance.

### Example Configuration

Here's an example of how the configuration might look in different formats:

#### JSON
```json
{
    "commit_limit": 20,
    "most_changed_files_limit": 15,
    "least_changed_files_limit": 15,
    "log_level": "DEBUG"
}
```

#### YAML
```yaml
commit_limit: 20
most_changed_files_limit: 15
least_changed_files_limit: 15
log_level: DEBUG
```

#### TOML
```toml
commit_limit = 20
most_changed_files_limit = 15
least_changed_files_limit = 15
log_level = "DEBUG"
```

## Usage

Here's a basic example of how to use Git Analyzer with configuration:

```python
import asyncio
from zap.git_analyzer import GitAnalyzer, GitAnalyzerConfig

# Example configuration dictionary
config = {
    "commit_limit": 20,
    "most_changed_files_limit": 15,
    "least_changed_files_limit": 15,
    "log_level": "DEBUG"
}

# Create a GitAnalyzerConfig instance from the dictionary
analyzer_config = GitAnalyzerConfig.from_dict(config)

# Alternatively, load configuration from a file
# analyzer_config = GitAnalyzerConfig.from_file('config.yaml')

async def main():
    # Initialize the GitAnalyzer with the configuration
    analyzer = GitAnalyzer('/path/to/your/repo', config=analyzer_config)
    
    # Perform the analysis
    result = await analyzer.analyze()
    
    # Print some results
    print(f"Number of dependencies: {len(result.project_info.dependencies)}")
    print(f"Number of recent commits: {len(result.recent_commits)}")
    print(f"Most changed file: {result.most_changed_files[0][0]}")
    
    # Print Git status
    print("Git status:")
    for status, files in result.git_status.items():
        print(f"  {status}: {', '.join(files)}")
    
    # Print most changed files
    print("Most changed files:")
    for file, count in result.most_changed_files:
        print(f"  {file}: {count} changes")

if __name__ == "__main__":
    asyncio.run(main())
```

This example demonstrates how to create a custom configuration, initialize the GitAnalyzer with it, perform the analysis, and print some of the results.