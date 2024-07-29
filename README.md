# zap Agents Documentation

## Quick Start
This guide provides an easy way to get started with `zap` agents.

### Step 1: Clone the Repository
```sh
git clone https://github.com/yourusername/zap.git
cd zap
```

### Step 2: Install Dependencies
Ensure Python (>=3.11, <3.13) is installed. Use Poetry to install dependencies:

```sh
poetry install
```

### Step 3: Run Your First Agent
Initialize configurations and templates, then run an agent:

```sh
poetry run python zap/main.py --init-config --init-templates --force
poetry run python zap/main.py --agent chat --tasks "hello world"
```

## Core Concepts

### Agents
Agents are the core components responsible for processing tasks and managing interactions within `zap`.

### Context Management
Contexts maintain the state across sessions, allowing for continuous interaction.

### Template Engine
The `ZapTemplateEngine` handles dynamic content rendering using Jinja2 templates.

## Examples and Use Cases

### Default Chat Agent
Running tasks using the default chat agent:

```sh
poetry run python zap/main.py --agent chat --tasks "analyze repository"
```

### Custom Agent
Creating and running a custom agent:

1. Define your agent by extending the `Agent` class.
2. Register your custom agent.
3. Run tasks with the custom agent.

**Example:**

```py
# custom_agent.py
from zap.agents.base import Agent

class CustomAgent(Agent):
    async def process(self, input_text, context, config):
        # Custom processing logic
        return f"Processed with CustomAgent: {input_text}"

# Register the custom agent in the main script
agent_manager.register_agent("custom", CustomAgent)
```

Run the custom agent:

```sh
poetry run python zap/main.py --agent custom --tasks "custom task"
```

### Context Management
Save and load contexts to maintain state across sessions.

**Example:**

```py
context_manager = ContextManager(agent_manager, "custom-agent")
context = context_manager.get_current_context()
context.add_message("Initiating custom task")
context_manager.save_context("custom-context")
```

Loading a previously saved context:

```sh
poetry run python zap/main.py --init-config --force
poetry run python zap/main.py --tasks "custom task"
```

## Component Guide

### ChatAgent
A built-in agent for chat-based interactions.

**Example Usage:**

```sh
poetry run python zap/main.py --agent chat --tasks "say hello"
```

### CustomAgent
Extend the `Agent` class to create custom agents for specific tasks.

**Example:**

```py
class CustomAgent(Agent):
    async def process(self, input_text, context, config):
        # Custom processing logic
        return f"Processed with CustomAgent: {input_text}"
```

## Configuration

Agents can be configured via CLI parameters or configuration files.

**Example Configuration:**

```yaml
agent: chat
templates_dir: ~/.zap/templates
auto_archive_contexts: true
auto_load_contexts: true
auto_persist_contexts: true
```

Set configuration via CLI:

```sh
poetry run python zap/main.py --agent custom --templates-dir "custom/templates"
```

## Troubleshooting

### Common Issues

**Problem:** Agent not recognized
**Solution:** Ensure the agent is registered and specified correctly:

```sh
poetry run python zap/main.py --agent custom --tasks "custom task"
```

**Problem:** Missing configuration file
**Solution:** Initialize the configuration:

```sh
poetry run python zap/main.py --init-config --force
```

### API Key Issues

**Problem:** API keys not recognized
**Solution:** Verify API keys through CLI or environment variables:

```sh
poetry run python zap/main.py --openai-api-key YOUR_API_KEY
```

## Performance Tips and Optimization

- Periodically archive contexts to prevent large state files.
- Modularize tasks for efficient parallel execution once supported.

## Extending or Customizing Agents

### Adding Custom Templates
Add custom templates under the `templates` directory and reference them in your agent configuration.

### Creating Advanced Agents
Extend existing agent classes to implement more complex logic and interaction capabilities.

**Example:**

```py
class AdvancedAgent(ChatAgent):
    async def process(self, input_text, context, config):
        # Advanced processing logic
        return f"Advanced Processing Done: {input_text}"
```

Use the newly created agent:

```sh
poetry run python zap/main.py --agent advanced --tasks "advanced task"
```
