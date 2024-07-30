import asyncio
import pytest
from zap.templating.engine import ZapTemplateEngine, ZapTemplateLoader
from zap.templating.default_resolver import DefaultPathResolver


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
