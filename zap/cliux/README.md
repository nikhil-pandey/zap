# CLIUX

CLIUX allows you to customize various aspects of the UI through configuration settings. You can provide the configuration as a dictionary, a file path (JSON, YAML, TOML), or a `Config` dataclass instance.

## Features

- Rich console output with syntax highlighting, tables, and panels
- Interactive prompts for various types of user input
- Asynchronous input handling
- Input logging to a history file
- Background exporting of console output to HTML, SVG, and text formats
- Progress bars and spinners for long-running tasks
- Markdown rendering in the console
- File tree visualization
- Exception handling with rich tracebacks
- Customizable configuration through dictionary or file input

## Configuration

CLIUX allows you to customize various aspects of the UI through configuration settings. You can provide the configuration as a dictionary, a file path (JSON, YAML, TOML), or a `Config` dataclass instance.

### Example Configuration

Here's an example of how the configuration might look in different formats:

#### JSON
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

#### YAML
```yaml
theme: monokai
history_file: my_history.log
panel_border_style: bold magenta
table_header_style: bold blue
spinner_type: line
live_refresh_per_second: 5
verbose: true
```

#### TOML
```toml
theme = "monokai"
history_file = "my_history.log"
panel_border_style = "bold magenta"
table_header_style = "bold blue"
spinner_type = "line"
live_refresh_per_second = 5
verbose = true
```

## Usage

Here's a basic example of how to use CLIUX with configuration:

```python
import asyncio
from zap.cliux import UI, Config

# Example configuration dictionary
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
    ui.panel("Welcome to CLIUX Demo", title="Hello")
    
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

    ui.tree(["/home/user/documents", "/home/user/downloads", "/home/user/pictures"])

    component = Panel(...)
    with ui.live_output(component) as live:
        for i in range(10):
            live.update(f"Updating live output: {i}")
            await asyncio.sleep(0.5)

    await ui.export_async("output.html", "html")

if __name__ == "__main__":
    asyncio.run(main())
```