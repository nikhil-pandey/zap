# Zap Project Documentation

## Quick Start

Let's get you up and running with a quick example.

1. **Install dependencies:**

```bash
poetry install
```

2. **Run the Echo Agent:**

```python
from zap.agents.echo_agent import EchoAgent
from zap.contexts.context import Context

async def run_echo_agent():
    agent = EchoAgent()
    context = Context(messages=[])
    output = await agent.process("Hello, World!", context, template_context={})
    print(output.content)

# In a proper async environment, you would use: asyncio.run(run_echo_agent())
```

## Core Concepts

### Agents

Agents are the main entities that process user input and generate responses. Each agent has a unique purpose and behavior.

#### Example: EchoAgent

The `EchoAgent` simply repeats back what the user says.

```python
from zap.agents.echo_agent import EchoAgent
from zap.contexts.context import Context

async def run_echo_agent():
    agent = EchoAgent()
    context = Context(messages=[])
    output = await agent.process("Hello, World!", context, template_context={})
    print(output.content)
```

Output:
```
I heard you say: Hello, World!
```

## Examples and Use Cases

### Running the EchoAgent

To run the `EchoAgent`, ensure you have the necessary context and configuration.

```python
from zap.agents.echo_agent import EchoAgent
from zap.contexts.context import Context

async def run_echo_agent():
    agent = EchoAgent()
    context = Context(messages=[])
    output = await agent.process("Hello, Zap!", context, template_context={})
    print(output.content)

# Use an async runtime to execute the function
event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(run_echo_agent())
```

### Using the ToolManager

The `ToolManager` helps manage and execute various tools.

```python
from zap.tools.tool_manager import ToolManager
from zap.tools.basic_tools import RegisterFileTool, WriteFileTool

# Initialize ToolManager
tool_manager = ToolManager()
register_tools(tool_manager)

# Get a tool and execute it
read_tool = tool_manager.get_tool('read_file')
content = await read_tool.execute(filename='README.md')
print(content)
```

## Component Guide

### Agents

Agents are the primary components responsible for handling user input and generating responses. Here are some key agents:

- **EchoAgent:** Repeats back the user's input.
- **ChatAgent:** Handles chat messages with advanced processing.
- **CodeAgent:** Specializes in handling code-related tasks.

#### EchoAgent

```python
class EchoAgent(ChatAgent):
    async def process(self, message: str, context: Context, template_context: dict) -> AgentOutput:
        echo_message = f"I heard you say: {message}"
        message_history = [
            {"role": "user", "content": message},
            {"role": "assistant", "content": echo_message}
        ]
        return AgentOutput(content=echo_message, message_history=message_history)
```

### Tools

Tools are utility classes that perform specific tasks. Examples include reading files, writing files, and running tests.

#### Example: ReadFileTool

```python
class ReadFileTool(Tool):
    async def execute(self, filename: str):
        with open(filename, 'r') as file:
            return file.read()
```

## Configuration

Configuration is managed through the `pyproject.toml` file. Here you can specify dependencies, tools, and other project settings.

### Example Configuration

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
pygit2 = "^1.15.1"
rich = "^13.7.1"
black = "^24.4.2"
litellm = "^1.42.4"
questionary = "^2.0.1"
toml = "^0.10.2"
aiofiles = "^24.1.0"
pyperclip = "^1.9.0"
pygtrie = "^2.5.0"
tiktoken= "^0.7.0"
keyboard = "^0.13.5"
fuzzywuzzy = "^0.18.0"
python-levenshtein = "^0.25.1"
pytest = "^8.3.2"
pytest-asyncio = "^0.23.8"
pytest-mock = "^3.14.0"
aiohttp = "^3.9.5"
coverage = "^7.6.0"
psutil = "^6.0.0"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Agent does not respond

**Solution:** Check if the context and template_context are correctly initialized.

#### Issue: File read/write tools not working

**Solution:** Ensure the file paths are correct and within the repository boundary as specified in the tool descriptions.

### Example Error

```
Path is outside the repository boundary.
```

**Resolution:** Verify that the file path starts within the repository root.

## Extending the Project

You can extend the project by adding new agents and tools. Ensure they inherit from the appropriate base classes (`Agent`, `Tool`) and register them correctly.

### Example: Adding a New Tool

```python
class NewTool(Tool):
    async def execute(self, arg1: str, arg2: str):
        # Implementation here
        return f"Processed {arg1} and {arg2}"

# Register the new tool
new_tool = NewTool()
tool_manager.register_tool(new_tool)
```