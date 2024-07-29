import os
import tempfile

import aiofiles
import pytest

from zap.templating.engine import ZapTemplateEngine


@pytest.fixture
def engine():
    return ZapTemplateEngine()


@pytest.mark.asyncio
async def test_simple_render(engine):
    template = "Hi {{ simple }} demo"
    context = {"simple": "there"}
    expected_output = "Hi there demo"
    result = await engine.render(template, context)
    assert result == expected_output


@pytest.mark.asyncio
async def test_nested_context_render(engine):
    template = "{{ chat[-1].content }}"
    context = {"chat": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]}
    expected_output = "Hi there!"
    result = await engine.render(template, context)
    assert result == expected_output


@pytest.mark.asyncio
async def test_deeply_nested_context_render(engine):
    template = "{{ coding.chat[-1].content }}"
    context = {"coding": {"chat": [{"role": "assistant", "content": "Use def for functions."}]}}
    expected_output = "Use def for functions."
    result = await engine.render(template, context)
    assert result == expected_output


@pytest.mark.asyncio
async def test_render_with_file_include(engine):
    with tempfile.TemporaryDirectory() as tmpdirname:
        readme_path = os.path.join(tmpdirname, "README.md")
        async with aiofiles.open(readme_path, "w") as f:
            await f.write("# Project README")
        readme_path = readme_path.replace("\\", "/")
        template = rf"The content is: {{{{ i('{readme_path}') }}}}"
        expected_output = "The content is: # Project README"
        result = await engine.render(template, {})
        assert result == expected_output


@pytest.mark.asyncio
async def test_render_with_absolute_file_include(engine):
    with tempfile.TemporaryDirectory() as tmpdirname:
        readme_path = os.path.join(tmpdirname, "README.md")
        with open(readme_path, "w") as f:
            f.write("# Project README")
        readme_path = readme_path.replace("\\", "/")
        template = rf"The content is: {{{{ i('{readme_path}') }}}}"
        expected_output = "The content is: # Project README"
        result = await engine.render(template, {})
        assert result == expected_output


@pytest.mark.asyncio
async def test_render_with_http_include(engine):
    template = "Documentation: {{ i('https://nikhil.com.np') }}"
    result = await engine.render(template, {})
    assert 'favico' in result
