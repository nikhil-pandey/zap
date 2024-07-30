import pytest
from zap.templating.engine import ZapTemplateEngine


@pytest.mark.asyncio
async def test_render_with_missing_variables():
    template_engine = ZapTemplateEngine(
        templates={"greeting.txt": "Hello, {{ name }}!"}
    )
    rendered = await template_engine.render_file(
        "greeting.txt", {}
    )  # No 'name' provided
    assert rendered == "Hello, !"


@pytest.mark.asyncio
async def test_include_invalid_url(mocker):
    template_engine = ZapTemplateEngine(
        templates={"index.html": '{{ i("https://invalid.url") }}'}
    )

    # Mock aiohttp.ClientSession().get() to raise an exception for invalid URL
    mocker.patch("aiohttp.ClientSession.get", side_effect=Exception("Invalid URL"))

    with pytest.raises(Exception, match="Invalid URL"):
        await template_engine.render_file("index.html")
