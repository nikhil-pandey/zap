# `zap.commands` Documentation

## Quick Start

### 1. Setup

To use the `zap.commands` submodule, ensure you have Python 3.11+, Poetry, and all necessary dependencies installed. Begin with:

```bash
git clone <repository_url>
cd zapfinal
poetry install
```

### 2. Utilizing Commands

Here�s a quick example of how to add files to the context using the `Commands` class:

```python
from zap.commands import Commands
from zap.config import AppConfig
from zap.app_state import AppState
from zap.cliux import UIInterface
from zap.contexts.context_manager import ContextManager
from zap.agent_manager import AgentManager

# Initialize necessary components
config = AppConfig()
state = AppState()
ui = UIInterface()
context_manager = ContextManager()
agent_manager = AgentManager()

# Initialize Context Command Manager (ccm)
ccm = ContextCommandManager(context_manager, ui, agent_manager)

# Initialize Commands
commands = Commands(config, state, ui, ccm, agent_manager)

# Run `add` command
await commands.run_command('/add path/to/file')
```

## Core Concepts

### Command Registration

Commands are registered within the `Commands` class using the `CommandRegistry`. Example:

```python
def _register_commands(self):
    self.registry.command(
        "add", aliases=["a"], description="Add files to the context"
    )(self.file_manager.add)
```

### File Context Management

**Adding Files**

Adds specified files to the current context.
```python
await commands.run_command('/add path/to/file1 path/to/file2')
```

**Clearing All Files**

Clears all files from the current context.
```python
await commands.run_command('/drop')
```

## Examples and Use Cases

### Example 1: Copy All Context Files to Clipboard

```python
await commands.run_command('/copy')
```

Copies the contents of all files in the context to the clipboard.

### Example 2: Running Shell Commands

```python
await commands.run_command('/shell "ls -la"')
```
Executes a shell command.

### Example 3: Git Integration - Diff

```python
await commands.run_command('/diff')
```
Shows the git diff of the repository.

## Component Guide

### `AdvancedInput`
Prompts for input with advanced completions using the `PromptSession` from `prompt_toolkit`.

Example:
```python
advanced_input = AdvancedInput(registry, state, ui)
output = await advanced_input.input_async(prompt="> ")
```

### `UtilityCommands`

- **copy_to_clipboard**: Copies the content of all files in the context to the clipboard.
- **shell**: Executes a given shell command.

Example:
```python
utility = UtilityCommands(state, ui)
await utility.shell("echo 'Hello World'")
```

### `DevelopmentWorkflow`

Manages tasks for the development workflow such as linting, building, and testing.

Example:

```python
dev_workflow = DevelopmentWorkflow(config, ui)
await dev_workflow.lint()
await dev_workflow.build(,
await dev_workflow.test()
```

### `FileContextManager`

Manages files within the project context.

Example:
```python
file_manager = FileContextManager(state, ui)
await file_manager.add("file1.py", "folder/")
await file_manager.remove("file1.py")
await file_manager.clear()
await file_manager.list()
```

## Configuration

### Sample Configuration (`pyproject.toml`)

Example configuration for setting up your project:

```toml
[tool.poetry]
name = "zap"
version = "0.1.0"
description = ""
authors = ["Nikhil Pandey <nikhil@nikhil.com.np>"]
readme = "README.md"

[tool.poetry.dependencies]
python = ">=3.11,<3.13"
flake8 = "^7.1.0"
pyyaml = "^6.0.1"
# ... other dependencies
```

## Troubleshooting

### Problem: Not Enough Arguments for Command

**Error Message:**

```
Not enough arguments for command 'add'. Expected 1, got 0.
Usage: add <file>
```

**Solution:**

Provide the required arguments:
```bash
/add path/to/file1
```

### Problem: Shell Command Failure

**Error Message:**
```
Shell command failed: <error details>
```

**Solution:**

Ensure the command is correct and retry:
```bash
/shell "echo 'Hello World'"
```

## Extending or Customizing the `commands` Submodule

### Adding a New Command

To add a new command, register it within the `Commands` class:

```python
self.registry.command("new_command", description="My new command")(self.my_new_command)
```

Implement the command logic:

```python
async def my_new_command(self, *args):
    # Command logic here
    pass
```
