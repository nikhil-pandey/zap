# cliux Module Documentation

## Quick Start
Here’s how to quickly get started with the `cliux` module:

```python
from zap.cliux import UI, Config

# Basic configuration dictionary
config_dict = {
    "theme": "default",
    "verbose": True
}

# Initialize the UI component
ui = UI(config_dict)

# Print an info message
ui.info("Hello, welcome to zap CLI!")

# Display a table
columns = ["Name", "Age"]
rows = [["Alice", 30], ["Bob", 25]]
ui.table(title="User Data", columns=columns, rows=rows)

# Display a spinner
with ui.spinner("Processing..."):
    import time
    time.sleep(2)
```

## Core Concepts

### UI Interface
The `UIInterface` class defines the expected methods that any UI implementation must provide. It includes methods for logging, displaying tables and panels, and more. Below is an example of how you might create a custom UI by extending this class.

```python
class CustomUI(UIInterface):
    def raw(self, obj: any):
        print(obj)

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    # Implement other required methods...
```

### Configuration
`Config` is a dataclass that holds the configuration settings of the UI component. You can load this configuration from a dictionary, JSON, YAML, or TOML file.

```python
config = Config.from_file("config.toml")
ui = UI(config)
```

## Examples and Use Cases

### Displaying Rich Tables

```python
columns = ["ID", "Name", "Age"]
rows = [
    ["1", "Alice", "29"],
    ["2", "Bob", "34"]
]

ui.table("User Information", columns, rows)
```

### Logging Messages
Log messages at different levels such as `info`, `debug`, `warning`, `error`, and `exception`.

```python
ui.info("This is an info message")
ui.warning("This is a warning message")
ui.error("This is an error message")
```

### Exporting Outputs
Export console outputs to different formats:

```python
ui.export_html("output.html")
ui.export_svg("output.svg")
ui.export_text("output.txt")
```

### Using Spinner for Long-running Tasks

```python
with ui.spinner("Loading..."):
    time.sleep(3)
```

### Displaying Syntax Highlighted Code

```python
code_snippet = '''
def hello_world():
    print("Hello, world!")
'''

ui.syntax_highlight(code_snippet, language="python")
```

## Configuration

### Example Configuration
```toml
# config.toml
theme = "monokai"
history_file = "command_history.log"
panel_border_style = "bold"
table_header_style = "bold magenta"
spinner_type = "dots"
live_refresh_per_second = 4
syntax_theme = "monokai"
verbose = true
```

### Loading Configuration from File
```python
config = Config.from_file("config.toml")
ui = UI(config)
```

### Loading Configuration from Dictionary
```python
config_dict = {
    "theme": "default",
    "verbose": True,
}
config = Config.from_dict(config_dict)
ui = UI(config)
```

## Troubleshooting

### Common Issues

**Error**: Unsupported file format while loading configuration.
- **Solution**: Ensure the configuration file is either `.json`, `.yaml`, or `.toml`.

**Error**: Unknown theme specified.
- **Solution**: Use one of the predefined themes or ensure your custom theme is correctly defined.

### Example Error Messages and Resolutions
```python
try:
    config = Config.from_file("unknown_format.txt")
except ValueError as e:
    print(e)
    # Output: Unsupported file format. Use JSON, YAML, or TOML.
```

## Extending the Module

### Adding a new Theme

```python
ui.KNOWN_THEMES["dracula"] = {
    "default": "purple",
    "dim": "dim purple",
    # Add more style mappings
}
```

### Custom UI Implementation
Create a custom implementation of the `UIInterface` to add new behavior.

```python
class CustomUI(UIInterface):
    def raw(self, obj: any):
        # Custom raw object printing
        print("Raw object:", obj)
        
    def print(self, *args, **kwargs):
        # Custom print method
        print("Custom print:", *args)

    # Implement other required methods...
```
