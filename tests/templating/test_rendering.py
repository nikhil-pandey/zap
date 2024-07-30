import pytest
from zap.templating.engine import ZapTemplateEngine

@pytest.mark.asyncio
async def test_render_from_string_basic():
    template_engine = ZapTemplateEngine()
    result = await template_engine.render('Hello, {{ name }}!', {'name': 'World'})
    assert result == 'Hello, World!'

@pytest.mark.asyncio
async def test_render_from_string_missing_context():
    template_engine = ZapTemplateEngine()
    result = await template_engine.render('Hello, {{ name }}!')
    assert result == 'Hello, !'

@pytest.mark.asyncio
async def test_render_from_string_nested_context():
    template_engine = ZapTemplateEngine()
    result = await template_engine.render('Hello, {{ user.name }}!', {'user': {'name': 'Alice'}})
    assert result == 'Hello, Alice!'
