# ZAP

ZAP is a versatile framework designed for creating and managing agents with various capabilities, enriched by an advanced command-line user interface (CLIUX) powered by the `rich` library. This enables enhanced console outputs and interactivity, supporting seamless development workflows.

## Features

### Framework Components
- **Agents:** Modular agent classes such as `ChatAgent`, `CodeAgent`, `EchoAgent`, and `GitAnalyzer`.
- **Commands:** Manage file contexts, git operations, utility commands, and more.
- **UI System (CLIUX):** Advanced UI features leveraging `rich` for superior console outputs.
- **Configuration:** Supports JSON, YAML, and TOML formats for flexible configuration.

### CLIUX Highlights
- **Rich Console Output:** Syntax highlighting, panels, tables, and more.
- **Interactive Prompts:** Asynchronous user input handling.
- **Input Logging:** Logs inputs to a history file.
- **Exporting:** Export console output to HTML, SVG, or text formats.
- **Progress Indicators:** Visual feedback via spinners and progress bars.
- **Markdown Rendering:** Display markdown content.
- **File Tree Visualization:** Visualize file and directory structures.
- **Customizable Configuration:** Easy configuration through dictionaries or files (JSON, YAML, TOML).

### Agent Types
- **ChatAgent:** Assists in chat-based interactions.
- **CodeAgent:** Manages code-related tasks such as reading, writing, and analyzing code.
- **EchoAgent:** Simply echoes back the input message.
- **GitAnalyzer:** Analyzes Git repositories, extracting useful metrics and repository information.

### Git Analyzer Features
- **Project Structure and Dependency Analysis**
- **Commit History and Statistics**
- **Git Status and Configurable Limits for Changed Files**

## Getting Started

### Installation

Clone the repository and install the dependencies:

```sh
git clone https://github.com/your-repo/zap.git
cd zap
pip install -r requirements.txt
```

### Configuration

#### JSON Example
```json
{
    "theme": "monokai",
    "history_file": "command_history.log",
    "panel_border_style": "bold",
    "table_header_style": "bold magenta",
    "spinner_type": "dots",
    "live_refresh_per_second": 4,
    "syntax_theme": "monokai",
    "verbose": false
}
```

#### YAML Example
```yaml
theme: monokai
history_file: command_history.log
panel_border_style: bold
table_header_style: bold magenta
spinner_type: dots
live_refresh_per_second: 4
syntax_theme: monokai
verbose: false
```

#### TOML Example
```toml
theme = "monokai"
history_file = "command_history.log"
panel_border_style = "bold"
table_header_style = "bold magenta"
spinner_type = "dots"
live_refresh_per_second = 4
syntax_theme = "monokai"
verbose = false
```

### Usage Example

Here’s how to use ZAP's CLIUX with a sample configuration:

```python
import asyncio
from zap.cliux import UI

config = {
    "theme": "monokai",
    "history_file": "command_history.log",
    "panel_border_style": "bold magenta",
    "table_header_style": "bold blue",
    "spinner_type": "line",
    "live_refresh_per_second": 5,
    "verbose": True
}

ui = UI(config)

async def main():
    ui.panel("Welcome to ZAP CLIUX Demo", title="Hello")
    
    with ui.spinner("Processing data"):
        await asyncio.sleep(2)
    
    ui.info("Data processing complete")
    
    table_data = [
        {"Name": "Alice", "Age": "25", "Role": "Engineer"},
        {"Name": "Bob", "Age": "30", "Role": "Designer"},
        {"Name": "Charlie", "Age": "35", "Role": "Manager"}
    ]
    ui.display_table("Employee Data", table_data)
    
    code = "print('Hello, World!')"
    ui.syntax_highlight(code, "python")

    ui.tree([
        "/home/user/documents", 
        "/home/user/downloads", 
        "/home/user/pictures"
    ])

    with ui.live_output("Processing...") as live:
        for i in range(10):
            live.update(f"Updating live output: {i}")
            await asyncio.sleep(0.5)

    await ui.export_async("output.html", "html")

if __name__ == "__main__":
    asyncio.run(main())
```

## Core Methods

### UI Methods
- **input_async(prompt):** Asynchronous user input.
- **print(*args, **kwargs):** Print messages to the console.
- **debug(message):** Print a debug message.
- **info(message):** Print an info message.
- **warning(message):** Print a warning message.
- **error(message):** Print an error message.
- **exception(e, message):** Print an exception message.
- **panel(content, title):** Display content in a panel.
- **table(title, columns, rows):** Display a table.
- **display_table(title, data):** Display data in table format.
- **spinner(message):** Display a spinner with a message.
- **progress(total):** Show a progress bar.
- **data_view(data, methods, title):** Detailed data view.
- **syntax_highlight(code, language, line_numbers):** Display syntax-highlighted code.
- **tree(paths):** Show a tree view of file paths.
- **live_output(content):** Display live output.
- **markdown(md_string):** Render markdown content.
- **log_input(input_str):** Log user input.
- **export_html(filename):** Export console output to HTML.
- **export_svg(filename):** Export console output to SVG.
- **export_text(filename):** Export console output to a text file.
- **export_async(filename, fmt):** Export console output asynchronously.

### Agent Configuration

Configure ZAP agents using YAML files, each with unique capabilities and configurations.

#### Example Agent Configuration

##### Echo Agent
```yaml
name: echo
type: EchoAgent
system_prompt: prompts/chat/system.j2
```

##### Documentation Agent
```yaml
name: documentation
type: ChatAgent
system_prompt: prompts/documentation/system.j2
tools:
  - read_file
  - write_file
```

##### Code Agent
```yaml
name: code
type: CodeAgent
system_prompt: prompts/code/system.j2
user_prompt: prompts/code/user.j2
tools:
  - read_file
  - write_file
  - list_files
  - delete_file
  - build_project
  - lint_project
  - run_tests
```

### Command System

ZAP supports a versatile array of commands for managing development workflows, file contexts, and more.

#### Example Commands

- **add:** Add files to the context.
- **remove:** Remove files from the context.
- **drop:** Clear all files from the context.
- **list:** List all files in the context.
- **diff:** Show git diff.
- **lint:** Run linting.
- **build:** Run build process.
- **test:** Run tests.
- **copy:** Copy file content to clipboard.
- **shell:** Execute a shell command.
- **switch_context:** Switch to a different context.
- **list_contexts:** List all available contexts.
- **visualize_context:** Show current context and agent.
- **save_context:** Save the current context.
- **load_contexts:** Load all saved contexts.
- **list_saved:** List all saved contexts.
- **delete_context:** Delete a context.
- **rename_context:** Rename a context.
- **clear_context:** Clear messages in a context.
- **switch_agent:** Switch to a different agent in the current context.
- **list_agents:** List all available agents.
- **archive_context:** Archive all contexts.
- **list_archives:** List all archived contexts.
- **load_archived:** Load an archived context.
- **help:** Show help information.

## Git Analyzer Features

- **Analyze project structure and dependencies**
- **Examine commit history**
- **Identify most and least changed files**
- **Get current Git status**
- **Customizable analysis depth and focus**
- **Support for various configuration file formats (JSON, YAML, TOML)**

### Configuration

Customize the Git Analyzer through configuration settings provided as a dictionary or file (JSON, YAML, TOML).

#### Example Configuration

##### JSON
```json
{
    "commit_limit": 20,
    "most_changed_files_limit": 15,
    "least_changed_files_limit": 15,
    "log_level": "DEBUG"
}
```

##### YAML
```yaml
commit_limit: 20
most_changed_files_limit: 15
least_changed_files_limit: 15
log_level: DEBUG
```

##### TOML
```toml
commit_limit = 20
most_changed_files_limit = 15
least_changed_files_limit = 15
log_level = "DEBUG"
```

### Usage

Here’s a basic example of using the Git Analyzer:

```python
import asyncio
from zap.git_analyzer import GitAnalyzer, GitAnalyzerConfig

config = {
    "commit_limit": 20,
    "most_changed_files_limit": 15,
    "least_changed_files_limit": 15,
    "log_level": "DEBUG"
}

analyzer_config = GitAnalyzerConfig.from_dict(config)

async def main():
    analyzer = GitAnalyzer('/path/to/your/repo', config=analyzer_config)
    
    result = await analyzer.analyze()
    
    print(f"Number of dependencies: {len(result.project_info.dependencies)}")
    print(f"Number of recent commits: {len(result.recent_commits)}")
    print(f"Most changed file: {result.most_changed_files[0][0]}")
    
    print("Git status:")
    for status, files in result.git_status.items():
        print(f"  {status}: {', '.join(files)}")
    
    print("Most changed files:")
    for file, count in result.most_changed_files:
        print(f"  {file}: {count} changes")

if __name__ == "__main__":
    asyncio.run(main())
```

## Contributors

ZAP is developed and maintained by a collaborative team of developers. Contributions are welcome!

## License

ZAP is licensed under the MIT License.
