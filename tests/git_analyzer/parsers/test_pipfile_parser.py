import pytest

from zap.git_analyzer.models.enums import Language, PackageManager
from zap.git_analyzer.parsers.pipfile import PipfileParser


@pytest.mark.asyncio
async def test_pipfile_parser():
    content = """
[packages]
requests = "*"
flask = "==1.1.2"

[dev-packages]
pytest = ">=5.0.0"
"""
    parser = PipfileParser()
    result = await parser.parse(content, 'Pipfile')

    assert result.language == Language.PYTHON
    assert result.package_manager == PackageManager.PIPENV
    assert 'requests' in result.dependencies
    assert 'flask' in result.dependencies
    assert 'pytest' in result.dependencies
    assert len(result.dependencies) == 3
    assert 'Pipfile' in result.config_files


@pytest.mark.asyncio
async def test_pipfile_parser_empty():
    content = """
[packages]

[dev-packages]
"""
    parser = PipfileParser()
    result = await parser.parse(content, 'Pipfile')

    assert result.language == Language.PYTHON
    assert result.package_manager == PackageManager.PIPENV
    assert len(result.dependencies) == 0


@pytest.mark.asyncio
async def test_pipfile_parser_invalid():
    content = "This is not a valid TOML file"
    parser = PipfileParser()
    with pytest.raises(ValueError):
        await parser.parse(content, 'Pipfile')
