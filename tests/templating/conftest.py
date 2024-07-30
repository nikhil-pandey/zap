import pytest
import os

@pytest.fixture
async def template_engine():
    from zap.templating.engine import ZapTemplateEngine
    return ZapTemplateEngine()


@pytest.fixture
async def setup_file_system():
    file_path = 'greeting.txt'
    with open(file_path, 'w') as f:
        f.write("Hello, {{ name }}!")
    yield
    if os.path.exists(file_path):
        os.remove(file_path)