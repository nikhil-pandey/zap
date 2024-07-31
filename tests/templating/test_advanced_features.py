import pytest
import asyncio
from zap.templating.engine import ZapTemplateEngine


@pytest.mark.asyncio
async def test_include_valid_url(mocker):
    template_engine = ZapTemplateEngine(
        templates={"index.html": '{{ i("https://valid.url") }}'}
    )

    # Mock aiohttp.ClientSession().get() to return valid content for a valid URL
    mock_response = mocker.AsyncMock()
    mock_response.__aenter__.return_value.text = mocker.AsyncMock(
        return_value="Valid content"
    )
    mocker.patch("aiohttp.ClientSession.get", return_value=mock_response)

    rendered = await template_engine.render_file("index.html")
    assert rendered == "Valid content"


@pytest.mark.asyncio
async def test_include_slow_response_url(mocker):
    template_engine = ZapTemplateEngine(
        templates={"index.html": '{{ i("https://slow.url") }}'}
    )

    # Mock aiohttp.ClientSession().get() to simulate a slow response
    async def slow_response(*args, **kwargs):
        await asyncio.sleep(2)  # Simulate network delay
        raise Exception("Slow response")

    mock_response = mocker.AsyncMock()
    mock_response.__aenter__.side_effect = slow_response
    mocker.patch("aiohttp.ClientSession.get", return_value=mock_response)

    with pytest.raises(Exception, match="Slow response"):
        await template_engine.render_file("index.html")
