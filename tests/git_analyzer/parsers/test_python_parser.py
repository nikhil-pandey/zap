import pytest

from zap.git_analyzer.models.enums import Language, PackageManager
from zap.git_analyzer.parsers.python import PythonParser


@pytest.mark.asyncio
async def test_python_parser_requirements_txt(sample_requirements_txt_content):
    parser = PythonParser()
    result = await parser.parse(sample_requirements_txt_content, 'requirements.txt')

    assert result.language == Language.PYTHON
    assert result.package_manager == PackageManager.PIP
    assert 'requests' in result.dependencies
    assert 'pytest' in result.dependencies
    assert len(result.dependencies) == 2
    assert 'requirements.txt' in result.config_files


@pytest.mark.asyncio
async def test_python_parser_pyproject_toml():
    content = '''
[tool.poetry]
name = "my-project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.25.1"

[tool.poetry.dev-dependencies]
pytest = "^6.2.3"
'''
    parser = PythonParser()
    result = await parser.parse(content, 'pyproject.toml')

    assert result.language == Language.PYTHON
    assert result.package_manager == PackageManager.POETRY
    assert 'requests' in result.dependencies
    assert 'pytest' in result.dependencies
    assert 'python' not in result.dependencies  # Ensure 'python' is not in dependencies
    assert len(result.dependencies) == 2
    assert 'pyproject.toml' in result.config_files
