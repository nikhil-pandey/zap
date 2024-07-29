# Agent Documentation

## Quick Start

Let's get started quickly with using agents in the "zap" automation tool.

1. Clone the repository and navigate to the project directory:
    ```sh
    git clone <repository_url>
    cd zap
    ```

2. Install dependencies using Poetry:
    ```sh
    poetry install
    ```

3. Run the Zap CLI with an agent:
    ```sh
    poetry run python -m zap.main --agent echo
    ```

## Core Concepts

### Agents
Agents in zap are specialized entities designed to perform specific tasks like chatting, coding, or handling documentation. Each agent has a specific configuration that includes prompts and tools it can utilize.

#### Example: Running an Echo Agent
This agent simply echoes back what is inputted.

```yaml
# zap/templates/agents/echo_agent.yaml
name: echo
type: EchoAgent
system_prompt: prompts/chat/system.j2
user_prompt: null
```

```sh
poetry run python -m zap.main --agent echo
```

Input:
```plaintext
Hello!
```

Output:
```plaintext
I heard you say: Hello!
```

### Tools
Tools are functional units that agents use to perform actions like reading or writing files, building projects, etc.

#### Example Tool: ReadFileTool
```py
class ReadFileTool(Tool):
    async def execute(self, filename: str):
        # Implementation here
```

### Templates
Templates structure the agent's prompts. They guide how agents should generate their output and interact with tools.

#### Example Template: prompts/code/system.j2
```j2
You are an expert coding agent tasked with implementing changes in a software project.
```

## Examples and Use Cases

### Example 1: Running a Chat Agent
A chat agent helps in simulating a conversational interface.

#### Configuration File:
```yaml
# zap/templates/agents/chat_agent.yaml
name: chat
type: ChatAgent
system_prompt: prompts/chat/system.j2
user_prompt: null
```

#### Running the Chat Agent:
```sh
poetry run python -m zap.main --agent chat
```

#### Interaction:
Input:
```plaintext
How are you?
```

Expected Output:
```plaintext
I am just a program, but I'm functioning as expected!
```

### Example 2: Handling File Operations with a Code Agent
A code agent designed to handle file operations like reading, writing, and more.

#### Configuration File:
```yaml
# zap/templates/agents/code_agent.yaml
name: code
type: CodeAgent
system_prompt: prompts/code/system.j2
user_prompt: prompts/code/user.j2
tools:
  - read_file
  - write_file
  - list_files
```

#### Running the Code Agent:
```sh
poetry run python -m zap.main --agent code
```

#### Operations:
Command to list files:
```plaintext
list_files directory=.
```

Expected Output:
```json
{
  "status": "success",
  "result": ["file1.py", "file2.py", ...]
}
```

## Component Guide

### AgentConfig
Data structure holding configuration details for an agent.

#### Example:
```py
from zap.agents.agent_config import AgentConfig

config = AgentConfig(
    name="custom_agent",
    type="CustomAgent",
    system_prompt="prompts/custom/system.j2"
)
```

### ToolManager
Manages the registration and execution of tools.

#### Example:
```py
from zap.tools.tool_manager import ToolManager
from zap.tools.basic_tools import ReadFileTool

tool_manager = ToolManager()
tool_manager.register_tool(ReadFileTool(app_state))
```

## Extending Functionality

### Adding a New Agent

1. **Create configuration YAML for the agent.**
    ```yaml
    # zap/templates/agents/new_agent.yaml
    name: new_agent
type: NewAgent
    system_prompt: prompts/new_agent/system.j2
    user_prompt: prompts/new_agent/user.j2
tools:
      - read_file
      - write_file
    ```

2. **Define the agent class.**
    ```py
    # zap/agents/new_agent.py
    from zap.agents.base import Agent
    from zap.agents.agent_output import AgentOutput
    from zap.contexts.context import Context

    class NewAgent(Agent):
        async def process(self, message: str, context: Context, template_context: dict) -> AgentOutput {
            custom_message = f"Processing: {message}"
            message_history = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": custom_message}
            ]
            return AgentOutput(content=custom_message, message_history=message_history)
    ```

3. **Register the agent.**
    ```py
    # Update the __init__.py in the agents module
    from .new_agent import NewAgent
    ```

### Adding a New Tool

1. **Define the tool class.**
    ```py
    # zap/tools/new_tool.py
    from zap.tools.tool import Tool

    class NewTool(Tool):
        async def execute(self, *args, **kwargs):
            return "Tool executed"
    ```

2. **Register the tool.**
    ```py
    # Add to zap/tools/basic_tools.py
    def register_tools(tool_manager: ToolManager, app_state: AppState, ui: UIInterface):
        tool_manager.register_tool(NewTool())
    ```

## Performance Tips

- Minimize tool calls by batching operations.
- Utilize asynchronous execution for tasks that involve I/O operations.
- Regularly review and optimize agent configurations for efficiency.

---

**END**