from typing import Dict, Type

from .base import DependencyParser
from .dotnet import DotNetParser
from .javascript import JavaScriptParser
from .pipfile import PipfileParser
from .python import PythonParser
from ..models.enums import DependencyFileType


class ParserFactory:
    _parsers: Dict[DependencyFileType, Type[DependencyParser]] = {
        DependencyFileType.REQUIREMENTS_TXT: PythonParser,
        DependencyFileType.PYPROJECT_TOML: PythonParser,
        DependencyFileType.PACKAGE_JSON: JavaScriptParser,
        DependencyFileType.CSPROJ: DotNetParser,
        DependencyFileType.PIPFILE: PipfileParser,
    }

    @classmethod
    def get_parser(cls, file_path: str) -> DependencyParser:
        for file_type, parser_class in cls._parsers.items():
            if file_path.endswith(file_type.value):
                return parser_class()
        raise ValueError(f"No parser available for {file_path}")

    @classmethod
    def is_dependency_file(cls, file_path: str) -> bool:
        return any(
            file_path.endswith(file_type.value) for file_type in cls._parsers.keys()
        )
