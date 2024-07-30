import pytest

from zap.git_analyzer.parsers.dotnet import DotNetParser
from zap.git_analyzer.parsers.factory import ParserFactory
from zap.git_analyzer.parsers.javascript import JavaScriptParser
from zap.git_analyzer.parsers.pipfile import PipfileParser
from zap.git_analyzer.parsers.python import PythonParser


def test_parser_factory_get_parser():
    assert isinstance(ParserFactory.get_parser("requirements.txt"), PythonParser)
    assert isinstance(ParserFactory.get_parser("pyproject.toml"), PythonParser)
    assert isinstance(ParserFactory.get_parser("package.json"), JavaScriptParser)
    assert isinstance(ParserFactory.get_parser("project.csproj"), DotNetParser)
    assert isinstance(ParserFactory.get_parser("Pipfile"), PipfileParser)


def test_parser_factory_is_dependency_file():
    assert ParserFactory.is_dependency_file("requirements.txt")
    assert ParserFactory.is_dependency_file("pyproject.toml")
    assert ParserFactory.is_dependency_file("package.json")
    assert ParserFactory.is_dependency_file("project.csproj")
    assert ParserFactory.is_dependency_file("Pipfile")
    assert not ParserFactory.is_dependency_file("somefile.txt")


def test_parser_factory_invalid_file():
    with pytest.raises(ValueError):
        ParserFactory.get_parser("invalid.txt")
