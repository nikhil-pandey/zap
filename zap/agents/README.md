# Agent Submodule Documentation

## Quick Start

Here’s how you can get started with the agents submodule quickly.

### Example: Using the Echo Agent

```python
from zap.tools.tool_manager import ToolManager
from zap.agents.echo_agent import EchoAgent
from zap.agents.agent_config import AgentConfig

# Initialize the ToolManager
tool_manager = ToolManager()

# Define the agent configuration
config = AgentConfig(
    name="echo",
    type="EchoAgent",
    system_prompt="You are an echo bot"
)

# Initialize the EchoAgent
agent = EchoAgent(config, tool_manager, ui=None, engine=None)

# Process a message
response = await agent.process(message="Hello, Agent!", context=None, template_context={})
print(response.content)
```

Expected Output:
```
"I heard you say: Hello, Agent!"
```

## Core Concepts

### Agent Configuration
The `AgentConfig` class allows configuring various aspects of an agent:

```python
from zap.agents.agent_config import AgentConfig

config = AgentConfig(
    name="documentation",
    type="ChatAgent",
    system_prompt="You are a helpful assistant",
    tools=["read_file", "write_file"],
    model="gpt-4o",
    provider="azure"
)
```

### Tool Management
Tools extend an agent's capabilities. The `ToolManager` class helps register and retrieve tools:

```python
from zap.tools.tool_manager import ToolManager
from zap.tools.basic_tools import ReadFileTool
from zap.app_state import AppState

tool_manager = ToolManager()
app_state = AppState()

# Register tools
tool_manager.register_tool(ReadFileTool(app_state))

# Retrieve and use a tool
read_file_tool = tool_manager.get_tool("read_file")
content = await read_file_tool.execute(filename="README.md")
print(content)
```

## Examples and Use Cases

### Simple Echo Agent

```python
from zap.agents.echo_agent import EchoAgent
from zap.agents.agent_config import AgentConfig

config = AgentConfig(
    name="echo",
    type="EchoAgent",
    system_prompt="You are an echo bot"
)
agent = EchoAgent(config, tool_manager=None, ui=None, engine=None)
response = await agent.process(message="Hello!", context=None, template_context={})
print(response.content)
```

Expected Output:
```
"I heard you say: Hello!"
```

### Agent with Tools

```python
from zap.agents.agent_config import AgentConfig
from zap.tools.tool_manager import ToolManager
from zap.tools.basic_tools import ReadFileTool, WriteFileTool
from zap.app_state import AppState
from pathlib import Path

# Instantiate the ToolManager and AppState
app_state = AppState()
tool_manager = ToolManager()

# Register tools
tool_manager.register_tool(ReadFileTool(app_state))
tool_manager.register_tool(WriteFileTool(app_state))

# Define agent configuration
config = AgentConfig(
    name="documentation",
    type="ChatAgent",
    system_prompt="You are a documentation bot",
    tools=["read_file", "write_file"]
)

# Initialize and use the agent
# Assuming ChatAgent is implemented
agent = ChatAgent(config, tool_manager, ui=None, engine=None)
response = await agent.process(message="Create a README.", context=None, template_context={})
print(response.content)
```

## Extending Functionality

### Creating a Custom Agent

You can extend the functionality by creating custom agents.

```python
from zap.agents.base import Agent
from zap.agents.agent_config import AgentConfig
from zap.agents.agent_output import AgentOutput

class CustomAgent(Agent):
    async def process(self, message: str, context: Context, template_context: dict) -> AgentOutput:
        custom_response = f"Custom agent response: {message}"
        message_history = [
            {"role": "user", "content": message},
            {"role": "assistant", "content": custom_response}
        ]
        return AgentOutput(content=custom_response, message_history=message_history)

# Define agent configuration
config = AgentConfig(
    name="custom",
    type="CustomAgent",
    system_prompt="You are a custom bot"
)

# Initialize the CustomAgent
custom_agent = CustomAgent(config, tool_manager=None, ui=None, engine=None)
response = await custom_agent.process(message="Hello!", context=None, template_context={})
print(response.content)
```

### Adding New Tools

You can also extend the functionality by adding new tools:

```python
from zap.tools.tool import Tool
from zap.tools.tool_manager import ToolManager

class CustomTool(Tool):
    def __init__(self):
        super().__init__(name="custom_tool", description="A custom tool")

    async def execute(self, *args, **kwargs):
        return {"status": "success", "result": "Executed custom tool"}

# Register the custom tool
tool_manager = ToolManager()
tool_manager.register_tool(CustomTool())

# Use the custom tool
custom_tool = tool_manager.get_tool("custom_tool")
result = await custom_tool.execute()
print(result)
```

## Configuration

### YAML Configuration File Example

**Configuration File:**

```yaml
name: echo
type: EchoAgent
system_prompt: prompts/chat/system.j2
```

### Python Configuration

```python
from zap.agents.agent_config import AgentConfig

config = AgentConfig(
    name="example-agent",
    type="CustomAgent",
    system_prompt="custom prompt",
    tools=["custom_tool"]
)
```

## Troubleshooting

### Common Issues

**Problem:** Tool not found in tool manager.

**Solution:** Ensure the tool is registered with the ToolManager before accessing it.

```python
# Ensure to register your custom tool
tool_manager.register_tool(CustomTool())
tool = tool_manager.get_tool("custom_tool")
```

**Problem:** Agent fails to process a message.

**Solution:** Check if the agent configuration has been correctly set:

```python
# Verify Agent Configuration
config = AgentConfig(
    name="example-agent",
    type="CustomAgent",
    system_prompt="custom prompt",
    tools=["custom_tool"]
)
```
