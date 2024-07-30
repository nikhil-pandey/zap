import pytest
import os
from zap.templating.engine import ZapTemplateEngine

@pytest.mark.asyncio
async def test_load_templates_from_directory():
    # Assuming 'templates' directory contains 'greeting.txt' with content 'Hello, {{ name }}!'
    os.makedirs('templates', exist_ok=True)
    with open('templates/greeting.txt', 'w') as f:
        f.write('Hello, {{ name }}!')
    template_engine = ZapTemplateEngine(templates_dir='templates')
    rendered = await template_engine.render_file('greeting.txt', {'name': 'World'})
    assert rendered == 'Hello, World!'
    # Clean up
    os.remove('templates/greeting.txt')
    os.rmdir('templates')

@pytest.mark.asyncio
async def test_invalid_template_directory():
    template_engine = ZapTemplateEngine(templates_dir='non_existent_dir')
    assert len(template_engine.templates) == 0
