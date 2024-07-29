# Zap Agents Documentation

## Quick Start

### Getting Started with Agents

1. **Installation**:

   Ensure you have Python version `>=3.11,<3.13` installed. Navigate to the project's root directory and install the dependencies using Poetry:

   ```sh
   poetry install
   ```

2. **Running an Agent**:

   You can start the application and utilize agents by running the main script:

   ```sh
   poetry run python zap/main.py
   ```

### Example Usage

#### Switching Agents and Listing Available Agents

```sh
# Switch to a different agent
poetry run python zap/main.py /switch_agent ExampleAgent

# List all available agents
poetry run python zap/main.py /list_agents
```

## Core Concepts

### Agent

An agent is a core component that processes user inputs using a defined behavior.

#### Example

```py
from zap.agents.base import ChatAgent

class ExampleAgent(ChatAgent):
    async def process(self, input_text, context, template_context):
        # Perform processing
        response = "Processed: " + input_text
        return response
```

### Context Command Manager

Manages context-related commands including switching agents.

#### Example

```py
from zap.contexts.context_command_manager import ContextCommandManager

ccm = ContextCommandManager(context_manager, ui, agent_manager)

await ccm.switch_agent('ExampleAgent')
await ccm.list_agents()
```

## Examples and Use Cases

### Common Scenarios

#### Switching and Listing Agents

Switching agents allows you to change the behavior of the system dynamically.

```py
from zap.contexts.context_command_manager import ContextCommandManager

# Assuming context_manager, ui, and agent_manager are already defined
ccm = ContextCommandManager(context_manager, ui, agent_manager)

# Switch to specified agent
await ccm.switch_agent('ExampleAgent')

# List all available agents
await ccm.list_agents()
```

### Chatting with an Agent

Use the main application loop to interact with a chat agent.

```py
from zap.app import ZapApp

# Initialize and run the application
app = ZapApp()

# In a real scenario, arguments might be parsed via the command line
args = parse_arguments()  
await app.initialize(args)

while True:
    # Simulation of user input (this would be collected from the user in real use)
    user_input = "/switch_agent ExampleAgent"
    await app.handle_input(user_input)
```

## Component Guide

### ContextCommandManager

**Description**: Manages commands related to switching and handling agent contexts.

**Usage**:

```py
ccm = ContextCommandManager(context_manager, ui, agent_manager)

# Switch context and agent
await ccm.switch_context("NewContext")
await ccm.switch_agent("ExampleAgent")

# List contexts and agents
await ccm.list_contexts()
await ccm.list_agents()
```

### ChatAgent

**Description**: Base class for creating custom chat agents.

**Usage**:

```py
class YourCustomAgent(ChatAgent):
    async def process(self, input_text, context, template_context):
        return "Custom response"
        
# Register and switch to your custom agent
agent_manager.register_agent("YourCustomAgent", YourCustomAgent)
await ccm.switch_agent("YourCustomAgent")
```

## Configuration

### Environment Variables

Ensure necessary API keys and environment variables are set for agent functionality.

```sh
export OPENAI_API_KEY=your_api_key
export ANTHROPIC_API_KEY=your_api_key
```

### Example Configuration (`pyproject.toml`)

Configure the package and dependencies:

```toml
[tool.poetry]
name = "zap"
version = "0.1.0"
...

[tool.poetry.dependencies]
python = ">=3.11,<3.13"
...
```

## Troubleshooting

### Common Issues

**Problem**: Unknown Agent

**Solution**: Ensure the agent is properly registered and available.

**Example**:

```sh
poetry run python zap/main.py /list_agents
```

Verify the agent name in the list of available agents.

### Example Error: Command Failed

**Solution**: Verify the command syntax and agent implementation.

## Extending Agents

### Adding a New Agent

1. **Define the Agent**:

   ```py
   from zap.agents.base import ChatAgent

   class MyNewAgent(ChatAgent):
       async def process(self, input_text, context, template_context):
           return "Response from MyNewAgent"
   ```

2. **Register the Agent**:

   ```py
   agent_manager.register_agent("MyNewAgent", MyNewAgent)
   ```

3. **Use the New Agent**:

   ```sh
   # Switch to the new agent
   poetry run python zap/main.py /switch_agent MyNewAgent
   ```

### Customizing Agent Behavior

Customize the processing logic in your agent's `process` method.

```py
class CustomBehaviorAgent(ChatAgent):
    async def process(self, input_text, context, template_context):
        # Custom behavior
        return "Custom Behavior Response"
```