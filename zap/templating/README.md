# Zap Templating Engine

The Zap Templating Engine is an asynchronous, extensible templating engine designed for rendering Jinja2 templates with
custom URL and file inclusion capabilities. This engine allows you to render templates and include content from both
local files and URLs dynamically.

## Usage

## Example Code

### Simple Render

```python
import asyncio
from zap.templating.engine import ZapTemplateEngine


async def main():
    engine = ZapTemplateEngine()
    template = "Hello, {{ name }}!"
    context = {"name": "World"}
    result = await engine.render(template, context)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

### File Inclusion

```python
import asyncio
from zap.templating.engine import ZapTemplateEngine


async def main():
    engine = ZapTemplateEngine()
    template = "The content is: {{ i('/path/to/your/file.txt') }}"
    context = {}
    result = await engine.render(template, context)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

### URL Inclusion

```python
import asyncio
from zap.templating.engine import ZapTemplateEngine


async def main():
    engine = ZapTemplateEngine()
    template = "The content is: {{ i('https://example.com') }}"
    context = {}
    result = await engine.render(template, context)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

### Using Custom Resolver

```python
import asyncio
from zap.templating.engine import ZapTemplateEngine
from custom_resolver import CustomPathResolver


async def main():
    custom_resolver = CustomPathResolver('/custom/base/path')
    engine = ZapTemplateEngine(resolver=custom_resolver)
    template = "The content is: {{ i('custom_file.txt') }}"
    context = {}
    result = await engine.render(template, context)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

This setup allows you to initialize the PromptManager once and use it throughout your application. You'll need to pass the PromptManager instance to functions that require it.
### Test Cases

To run test cases and verify the functionality:

```sh
poetry run pytest
```