import pytest
from zap.templating.engine import ZapTemplateEngine


@pytest.mark.asyncio
async def test_initialize_with_templates():
    templates = {"hello.txt": "Hello, {{ name }}!"}
    engine = ZapTemplateEngine(templates=templates)
    assert "hello.txt" in engine.templates


@pytest.mark.asyncio
async def test_render_simple_template():
    templates = {"greeting.txt": "Hello, {{ name }}!"}
    engine = ZapTemplateEngine(templates=templates)
    rendered = await engine.render_file("greeting.txt", {"name": "World"})
    assert rendered == "Hello, World!"


@pytest.mark.asyncio
async def test_render_complex_template():
    templates = {"complex.txt": "Hello, {{ user.name }}! Your role is {{ user.role }}."}
    engine = ZapTemplateEngine(templates=templates)
    context = {"user": {"name": "Alice", "role": "Administrator"}}
    rendered = await engine.render_file("complex.txt", context)
    assert rendered == "Hello, Alice! Your role is Administrator."


@pytest.mark.asyncio
async def test_render_deeply_nested_context():
    templates = {"nested.txt": "Hello, {{ user.details.personal.name }}!"}
    engine = ZapTemplateEngine(templates=templates)
    context = {"user": {"details": {"personal": {"name": "Deep Nested Name"}}}}
    rendered = await engine.render_file("nested.txt", context)
    assert rendered == "Hello, Deep Nested Name!"


@pytest.mark.asyncio
async def test_render_dynamic_context_updates():
    templates = {"dynamic.txt": "Hello, {{ user }}!"}
    engine = ZapTemplateEngine(templates=templates)
    context = {"user": "Initial Name"}

    # Update context dynamically
    context["user"] = "Updated Name"
    rendered = await engine.render_file("dynamic.txt", context)
    assert rendered == "Hello, Updated Name!"
