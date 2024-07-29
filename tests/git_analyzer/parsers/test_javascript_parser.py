import pytest

from zap.git_analyzer.models.enums import Language, PackageManager
from zap.git_analyzer.parsers.javascript import JavaScriptParser


@pytest.mark.asyncio
async def test_javascript_parser(sample_package_json_content):
    parser = JavaScriptParser()
    result = await parser.parse(sample_package_json_content, 'package.json')

    assert result.language == Language.JAVASCRIPT
    assert result.package_manager == PackageManager.NPM
    assert 'express' in result.dependencies
    assert 'lodash' in result.dependencies
    assert 'jest' in result.dependencies
    assert len(result.dependencies) == 3
    assert 'package.json' in result.config_files
