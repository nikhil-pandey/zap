# Zap Templating Engine

The Zap Templating Engine is a powerful tool designed for asynchronously rendering Jinja2 templates, capable of accommodating content from custom URLs and local files. It's ideal for rendering dynamic content.

## Usage

Begin by importing the `ZapTemplateEngine`:

```python
from zap.templating import ZapTemplateEngine
```

## Key Features

### Rendering Templates
Render templates using the `render` method inside the `ZapTemplateEngine` class. Here's a simple example:

```python
engine = ZapTemplateEngine()
template = "Hello, {{ name }}!"
context = {"name": "World"}
result = await engine.render(template, context)
print(result) # Outputs: "Hello, World!"
```

### Including File Content
Leverage the `i` function in your templates to insert content from local files:

```python
engine = ZapTemplateEngine()
template = "The content is: {{ i('/path/to/your/file.txt') }}"
result = await engine.render(template)
# Outputs the content of "/path/to/your/file.txt".
```

### Including URL Content
Use the same `i` function to include content from a URL:

```python
engine = ZapTemplateEngine()
template = "The content is: {{ i('https://example.com') }}"
result = await engine.render(template)
# Outputs the content of "https://example.com".
```

### Utilizing Custom Path Resolvers
By extending the `PathResolver` class, you can create a custom path resolver. You'll need to implement the `resolve_file` and `resolve_http` async methods:

```python
import asyncio
from zap.templating import ZapTemplateEngine
from custom_resolver import CustomPathResolver

custom_resolver = CustomPathResolver('/custom/base/path')
engine = ZapTemplateEngine(resolver=custom_resolver)
template = "The content is: {{ i('custom_file.txt') }}"
result = await engine.render(template)
print(result) # Outputs content of "custom_file.txt" using "/custom/base/path" as the base path.
```

## Testing

Confirm the engine's functionality by running the test cases:

```sh
poetry run pytest
```

For more comprehensive usage examples and advanced use cases, please consult the API documentation.