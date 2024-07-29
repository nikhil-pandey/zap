import os
import tempfile

import pytest

from zap.templating.default_resolver import DefaultPathResolver


@pytest.fixture
def resolver():
    return DefaultPathResolver()


@pytest.mark.asyncio
async def test_resolve_file_absolute_path(resolver):
    with tempfile.TemporaryDirectory() as tmpdirname:
        readme_path = os.path.join(tmpdirname, "README.md")
        with open(readme_path, "w") as f:
            f.write("# Project README")
        result = await resolver.resolve_file(readme_path)
        assert result == "# Project README"


@pytest.mark.asyncio
async def test_resolve_file_relative_path(resolver):
    with tempfile.TemporaryDirectory() as tmpdirname:
        docs_path = os.path.join(tmpdirname, "docs")
        os.makedirs(docs_path, exist_ok=True)
        guide_path = os.path.join(docs_path, "guide.txt")
        with open(guide_path, "w") as f:
            f.write("User guide content")
        result = await resolver.resolve_file(os.path.relpath(guide_path))
        assert result == "User guide content"


@pytest.mark.asyncio
async def test_resolve_http(resolver):
    url = 'https://nikhil.com.np'
    result = await resolver.resolve_http(url)
    assert 'favicon' in result
