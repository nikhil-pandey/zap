# Zap

Zap is a powerful, flexible agent framework designed to enable various automated tasks. It supports agents that can chat, generate documentation, execute code, and much more. Each agent is configurable via YAML files and can utilize different tools based on the specified configuration.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Loading and Managing Agents](#loading-and-managing-agents)
  - [Processing Messages](#processing-messages)
- [Configuration](#configuration)
  - [Agent Configuration Files](#agent-configuration-files)
  - [Prompt Templates](#prompt-templates)
- [Extending Zap](#extending-zap)

## Installation

Ensure you have Python installed and then run:

```bash
pip install -r requirements.txt
```

## Usage

### Loading and Managing Agents

Agents in Zap are managed through the `AgentManager`. This class loads agent configurations from a specified directory.

```python
from pathlib import Path
from zap.agent_manager import AgentManager
from zap.tools.tool_manager import ToolManager
from zap.cliux import UIInterface
from zap.templating import ZapTemplateEngine

# Initialize required components
config_dir = Path('./path_to_your_config_directory')
ui = UIInterface()
engine = ZapTemplateEngine()
tool_manager = ToolManager()

# Load agent manager
agent_manager = AgentManager(config_dir, tool_manager, ui, engine)

# List available agents
print(agent_manager.list_agents())

# Get a specific agent
agent = agent_manager.get_agent('code')
```

### Processing Messages

Once an agent is obtained, you can process messages using the `process` method.

```python
from zap.contexts.context import Context

# Create a context (this would be your actual context)
context = Context(messages=[])

# Define a template context
template_context = {}

# Process a message
result = await agent.process("Generate documentation for my code.", context, template_context)

print(result.content)
```

## Configuration

### Agent Configuration Files

Agents are configured via YAML files placed in the configuration directory. Below are examples of different agent configurations:

#### `code_agent.yaml`

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

#### `chat_agent.yaml`

```yaml
name: chat
type: ChatAgent
system_prompt: prompts/chat/system.j2
```

### Prompt Templates

Prompt templates are defined using Jinja2 templates and are rendered based on the agent’s context and input. These templates define the behavior and response style of the agents.

#### Example: `system.j2` for CodeAgent

```j2
You are a documentation generator that creates clear, concise, and accurate documentation for code and APIs.
```

#### Example: `system.j2` for ChatAgent

```j2
You are a helpful chat assistant.
```

## Extending Zap

To add a new agent to Zap:

1. **Create a New Agent Class:**
   Inherit from `Agent` or an existing agent type and implement any required methods.

   ```python
   from zap.agents.base import Agent

   class CustomAgent(Agent):
       async def process(self, message: str, context: Context, template_context: dict) -> AgentOutput:
           # Implement custom processing logic
           pass
   ```

2. **Add a YAML Configuration:**
   Add a configuration file in the configuration directory for your new agent.

   ```yaml
   name: custom
type: CustomAgent
system_prompt: prompts/custom/system.j2
   ```

3. **Update AgentManager (if required):**
   Ensure that `AgentManager` can recognize and load your new agent type.

   ```python
   import yaml
   from pathlib import Path
   from zap.agents import *

   class AgentManager:
       # ...

       def load_agents(self, config_dir: Path):
           for config_file in config_dir.glob('*.yaml'):
               with open(config_file, 'r') as f:
                   config_dict = yaml.safe_load(f)
                   config = AgentConfig(**config_dict)
                   agent_class = globals()[config.type]
                   agent = agent_class(config, tool_manager=self.tool_manager, ui=self.ui, engine=self.engine)
                   self.agents[config.name] = agent
   ```

This brief guide provides an overview on how to get started with Zap, configure agents, and extend the framework by adding custom agents. For further details, explore the code and provided examples.