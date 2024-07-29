# ZAP

ZAP is an extensive framework designed for creating and managing agents with various capabilities. It provides a rich command-line user interface (CLIUX) powered by the `rich` library to enhance console outputs and interactivity, facilitating seamless development workflows.

## Features

### Framework Components
- **Agents:** Modular agent classes like `ChatAgent`, `CodeAgent`, and `EchoAgent`.
- **Commands:** System for managing commands such as file context management, git operations, and utility commands.
- **UI System (CLIUX):** Advanced UI features utilizing `rich` for enhanced console outputs.
- **Configuration:** Flexible system supporting JSON, YAML, and TOML formats.

### CLIUX Features
- **Rich Console Output:** Syntax highlighting, panels, tables, and more.
- **Interactive Prompts:** Asynchronous user input handling.
- **Input Logging:** Log inputs to a history file.
- **Exporting:** Export console output to HTML, SVG, or text.
- **Progress Indicators:** Spinners and progress bars.
- **Markdown Rendering:** Display markdown content.
- **File Tree Visualization:** Display file and directory structures.
- **Customizable Configuration:** Easily configured via dictionaries or files (JSON, YAML, TOML).

## Getting Started

### Configuration

#### JSON Example
```json
{
    "theme": "monokai",
    "history_file": "my_history.log",
    "panel_border_style": "bold magenta",
    "table_header_style": "bold blue",
    "spinner_type": "line",
    "live_refresh_per_second": 5,
    "verbose": true
}
```

#### YAML Example
```yaml
theme: monokai
history_file: my_history.log
panel_border_style: bold magenta
table_header_style: bold blue
spinner_type: line
live_refresh_per_second: 5
verbose: true
```

#### TOML Example
```toml
theme = "monokai"
history_file = "my_history.log"
panel_border_style = "bold magenta"
table_header_style = "bold blue"
spinner_type = "line"
live_refresh_per_second = 5
verbose = true
```

### Usage Example

Here’s a quick example of how to use ZAP's CLIUX with a sample configuration:

```python
import asyncio
from zap.cliux import UI

config = {
    "theme": "monokai",
    "history_file": "my_history.log",
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

- **input_async(prompt):** Asynchronous user input.
- **print(
args, 

kwargs):** Print messages to the console.
- **debug(message):** Print a debug message.
- **info(message):** Print an info message.
- **warning(message):** Print a warning message.
- **error(message):** Print an error message.
- **exception(e, message):** Print an exception message.
- **panel(content, title):** Display content in a panel.
- **table(title, columns, rows):** Display a table.
- **display_table(title, data):** Display data in a table format.
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

## Agents

Configure ZAP agents using YAML files, each with unique capabilities and configurations.

### Example Agent Configuration

#### Echo Agent
```yaml
name: echo
type: EchoAgent
system_prompt: prompts/chat/system.j2
```

## Command System

ZAP supports a diverse array of commands for handling development workflows, file context management, and more.

### Example Commands

- **add:** Add files to the context.
- **remove:** Remove files from the context.
- **diff:** Show git diff.
- **lint:** Run linting.
- **build:** Run build process.
- **test:** Run tests.
- **shell:** Execute a shell command.
- **switch_context:** Switch to a different context.
- **save_context:** Save the current context.
- **list_contexts:** List all available contexts.

## Contributors

ZAP is developed and maintained by a collaborative team of developers. Contributions are welcome!

## License

ZAP is licensed under the MIT License.
