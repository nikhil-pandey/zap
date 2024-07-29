# Zap Agents Documentation

## Quick Start

### Prerequisites

Ensure you have Python version 3.11 or greater installed and Poetry as a package manager.

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/zap.git
    cd zap
    ```

2. Install dependencies using Poetry:

    ```sh
    poetry install
    ```

### Running an Agent

Run the following command to start an agent using Zap CLI:

```sh
poetry run python zap/main.py --agent chat
```

### Quick Example

Initialize the configuration and templates:

```sh
poetry run python zap/main.py --init-config --force
poetry run python zap/main.py --init-templates --force
```

## Core Concepts

### Agent Management

Zap allows for managing multiple agents to perform various tasks. Agents can be chat agents, file-based agents, or custom agents tailored to specific needs.

### Contexts

Agents operate within contexts which store the state and history of interactions.

### Command Interface

Agents respond to commands and user inputs, making it easy to extend functionality through custom commands and interactions.

## Examples and Use Cases

### Running a Chat Agent

Start a chat agent to interactively respond to user inputs:

```sh
poetry run python zap/main.py --agent chat
```

### Performing Tasks

Configure an agent to perform a series of tasks:

```sh
poetry run python zap/main.py --tasks "task1" "task2" --agent chat
```

### Custom Agent Configuration

Specify a custom template directory and agent configuration:

```sh
poetry run python zap/main.py --templates-dir "/path/to/templates" --agent custom_agent
```

## Component Guide

### ZapApp

Handles the lifecycle and management of agents within the application.

#### Practical Example

```python
from zap.app import ZapApp

app = ZapApp()
await app.initialize(args)
await app.run()
```

### ChatAgent

A specific type of agent designed to handle interactive chat-based interactions.

#### Practical Example

```python
from zap.agents.base import ChatAgent

chat_agent = ChatAgent(config, state, ui)
response = await chat_agent.process("Hello, Zap!", context, template_context)
print(response.content)
```

### Agent Manager

Manages multiple agents, allowing for easy switching and management.

#### Practical Example

```python
from zap.agent_manager import AgentManager

agent_manager = AgentManager("/path/to/agent/templates", tool_manager, ui, template_engine)
agent = agent_manager.get_agent("chat")
response = await agent.process("Hello, Zap!", context, template_context)
print(response.content)
```

## Configuration

### Agent Configuration File

Configuration for agents is stored in YAML files within the templates directory.

#### Example Configuration for a Chat Agent

```yaml
name: chat
model: openai
parameters:
  temperature: 0.7
  max_tokens: 150
```

### Environment Variables

Configure API keys and other sensitive data through environment variables.

#### Example

```sh
export OPENAI_API_KEY="your_openai_api_key"
```

## Troubleshooting

### Common Issues

#### Agent Initialization Error

**Problem**: Error initializing an agent due to missing configuration.

**Solution**: Ensure you have initialized the configuration and templates:

```sh
poetry run python zap/main.py --init-config --force
poetry run python zap/main.py --init-templates --force
```

#### Missing Dependencies

**Problem**: ImportError for missing dependencies.

**Solution**: Ensure all dependencies are installed by running:

```sh
poetry install
```

## Extending and Customizing

### Extending Chat Agent

Create a custom agent by inheriting from `ChatAgent`.

#### Example

```python
from zap.agents.base import ChatAgent

class CustomChatAgent(ChatAgent):
    async def custom_process(self, user_input, context, template_context):
        # Your custom processing logic
        pass

custom_agent = CustomChatAgent(config, state, ui)
await custom_agent.custom_process("Hello!", context, template_context)
```

### Adding New Agent Types

Extend `Agent` to define new types of agents with custom behavior.

#### Example

```python
from zap.agents.base import Agent

class FileAgent(Agent):
    async def process_file(self, file_path, context, template_context):
        # Your file processing logic
        pass

file_agent = FileAgent(config, state, ui)
await file_agent.process_file("/path/to/file.txt", context, template_context)
```