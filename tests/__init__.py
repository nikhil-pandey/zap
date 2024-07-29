import os

import pytest


@pytest.mark.asyncio
async def test_resolve_file_absolute_path(resolver):
    with open("README.md", "w") as f:
        f.write("# Project README")
    result = await resolver.resolve_file("file://README.md")
    os.remove("README.md")
    assert result == "# Project README"


@pytest.mark.asyncio
async def test_resolve_file_relative_path(resolver):
    os.makedirs("docs", exist_ok=True)
    with open("docs/guide.txt", "w") as f:
        f.write("User guide content")
    result = await resolver.resolve_file("path://docs/guide.txt")
    os.remove("docs/guide.txt")
    os.rmdir("docs")
    assert result == "User guide content"


@pytest.mark.asyncio
async def test_resolve_file_relative_scheme(resolver):
    os.makedirs("src", exist_ok=True)
    with open("src/main.py", "w") as f:
        f.write("content from relative path")
    result = await resolver.resolve_file("rel://src/main.py")
    os.remove("src/main.py")
    os.rmdir("src")
    assert result == "content from relative path"


@pytest.mark.asyncio
async def test_resolve_http(mocker, resolver):
    url = 'https://example.com'

    # Mock aiohttp.ClientSession().get().text() to return "Website content here"
    mocker.patch('aiohttp.ClientSession.get',
                 return_value=mocker.AsyncMock(status=200, text=mocker.AsyncMock(return_value="Website content here")))

    result = await resolver.resolve_http(url)
    assert result == "Website content here"
