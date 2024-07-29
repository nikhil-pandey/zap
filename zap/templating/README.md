# Zap Templating Engine

The Zap Templating Engine is designed to asynchronously render Jinja2 templates while accommodating custom URL and local file inclusions. It's built for dynamic content rendering from both local files and URLs.

## Usage

To use the Zap Templating Engine, import the `ZapTemplateEngine`.

```python
from zap.templating import ZapTemplateEngine
```

### Render Templates

Render templates by utilizing the `render` method from `ZapTemplateEngine`.

```python
engine = ZapTemplateEngine()
template = "Hello, {{ name }}!"
context = {"name": "World"}
result = await engine.render(template, context)
print(result)  # Outputs: "Hello, World!"
```

### Include File Content

Use the `i` function in your templates to include content from local files.

```python
engine = ZapTemplateEngine()
template = "The content is: {{ i('/path/to/your/file.txt') }}"
result = await engine.render(template)
# Outputs the content of "/path/to/your/file.txt".
```

### Include URL Content

You can also include content from a URL using the same `i` function.

```python
engine = ZapTemplateEngine()
template = "The content is: {{ i('https://example.com') }}"
result = await engine.render(template)
# Outputs the content of "https://example.com".
```

### Custom Resolver Usage

Create a custom resolver by extending `PathResolver` and implementing `resolve_file` and `resolve_http` asynchronous methods.

```python
import asyncio
from zap.templating import ZapTemplateEngine
from custom_resolver import CustomPathResolver

custom_resolver = CustomPathResolver('/custom/base/path')
engine = ZapTemplateEngine(resolver=custom_resolver)
template = "The content is: {{ i('custom_file.txt') }}"
result = await engine.render(template)
print(result)  # Outputs content of "custom_file.txt" using "/custom/base/path" as the base path.
```

## Running Test Cases

Validate functionality with test cases by running:

```sh
poetry run pytest
```

For detailed usage examples and advanced scenarios, please refer to the API documentation.