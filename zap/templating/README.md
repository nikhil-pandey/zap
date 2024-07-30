# Zap Templating Engine

## Quick Start

Get up and running quickly with the Zap Templating Engine.

```python
from zap.templating.engine import ZapTemplateEngine

templates = {
    "hello.txt": "Hello, {{ name }}!"
}

template_engine = ZapTemplateEngine(templates=templates)

async def render_hello():
    context = {"name": "World"}
    print(await template_engine.render_file("hello.txt", context))

import asyncio
asyncio.run(render_hello())
```

## Core Concepts

### Template Loading

Load templates from a dictionary or a directory.

**From a dictionary:**

```python
templates = {
    "template1.txt": "This is template 1",
}
template_engine = ZapTemplateEngine(templates=templates)
```

**From a directory:**

```python
template_engine = ZapTemplateEngine(templates_dir="path/to/templates")
```

### Rendering Templates

Templates can be rendered from strings or files.

**Render from string:**

```python
async def render_from_string():
    result = await template_engine.render("Hi {{ name }}", {"name": "Alice"})
    print(result)

import asyncio
asyncio.run(render_from_string())
```

**Render from file:**

```python
async def render_from_file():
    result = await template_engine.render_file("template1.txt", {"name": "Bob"})
    print(result)

import asyncio
asyncio.run(render_from_file())
```

### Including External Content

Include content from files or URLs.

```python
templates = {
    "index.html": "{% async %}{{ i('https://example.com') }}{% endasync %}"
}

template_engine = ZapTemplateEngine(templates=templates)

async def render_template():
    result = await template_engine.render_file("index.html")
    print(result)

import asyncio
asyncio.run(render_template())
```

## Examples and Use Cases

### Dynamic Context

```python
templates = {
    "welcome.txt": "Welcome, {{ user.name }}!"
}

template_engine = ZapTemplateEngine(templates=templates)

async def render_welcome():
    context = {"user": {"name": "Charlie"}}
    print(await template_engine.render_file("welcome.txt", context))

import asyncio
asyncio.run(render_welcome())
```

### Directory-based Templates

Given the directory structure:

```
/templates
    |-- greeting.txt
    |-- farewell.txt
```

**Load and Render:**

```python
template_engine = ZapTemplateEngine(templates_dir="path/to/templates")

async def render_greeting():
    context = {"name": "Dana"}
    print(await template_engine.render_file("greeting.txt", context))

import asyncio
asyncio.run(render_greeting())
```

### Fetching Remote Content

Use the URL resolver to include remote content.

```python
templates = {
    "remote.html": "{% async %}{{ i('https://example.com/data') }}{% endasync %}"
}

template_engine = ZapTemplateEngine(templates=templates)

async def render_remote():
    print(await template_engine.render_file("remote.html"))

import asyncio
asyncio.run(render_remote())
```

## Component Guide

### `ZapTemplateEngine`

The core component of the templating system, providing capabilities to render templates from strings and files, as well as include external content.

**Example Usage:**

```python
template_engine = ZapTemplateEngine(templates={"sample.txt": "Hello, {{ user }}!"})

async def render_sample():
    print(await template_engine.render_file("sample.txt", {"user": "Dave"}))

import asyncio
asyncio.run(render_sample())
```

**Best Practices:**
- Ensure context includes all necessary variables.
- Use directory-based template loading for large projects.

### `PathResolver`

Base class for custom path resolvers. Implement `resolve_file` and `resolve_http`.

### `DefaultPathResolver`

Resolves paths using the local filesystem and HTTP requests.

## Configuration

### Options

- `templates`: Dictionary of templates.
- `root_path`: Root directory for template resolution.
- `resolver`: Custom PathResolver instance.
- `templates_dir`: Directory containing templates.

**Example:**

```python
template_engine = ZapTemplateEngine(
    templates={"greet.txt": "Hi, {{ name }}!"},
    root_path="/my/root/path",
    resolver=CustomPathResolver(),
    templates_dir="/path/to/templates"
)
```

## Troubleshooting

### Template Not Found

**Error:**

`jinja2.exceptions.TemplateNotFound: <template_name>`

**Solution:**

Ensure template name is correct and exists.

### Invalid URL

**Error:**

`aiohttp.ClientResponseError: 404, message='Not Found'`

**Solution:**

Ensure URL is correct and accessible.

## Extending and Customizing

### Custom Path Resolver

Create a custom path resolver by inheriting `PathResolver`.

**Example:**

```python
from zap.templating.resolver import PathResolver

class CustomPathResolver(PathResolver):
    async def resolve_file(self, path: str) -> str:
        # Custom file resolution logic
        pass

    async def resolve_http(self, url: str) -> str:
        # Custom HTTP resolution logic
        pass

template_engine = ZapTemplateEngine(resolver=CustomPathResolver())
```
