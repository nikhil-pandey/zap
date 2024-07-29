import re

import toml

from .base import DependencyParser
from ..exceptions import ParserError
from ..models.dependency import DependencyInfo, FileInfo
from ..models.enums import Language, PackageManager


class PythonParser(DependencyParser):
    async def parse(self, content: str, file_path: str) -> DependencyInfo:
        if file_path.endswith("requirements.txt"):
            return await self._parse_requirements(content, file_path)
        elif file_path.endswith("pyproject.toml"):
            return await self._parse_pyproject_toml(content, file_path)
        else:
            raise ParserError(f"Unsupported file type: {file_path}")

    @staticmethod
    async def _parse_requirements(content: str, file_path: str) -> DependencyInfo:
        try:
            dependencies = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    # Split on first occurrence of any comparison operator
                    parts = re.split(r"([=<>!~]=|[<>])", line, 1)
                    if len(parts) < 2:
                        raise ParserError(f"Invalid requirement format: {line}")
                    dependencies.append(parts[0].strip())

            return DependencyInfo(
                language=Language.PYTHON,
                package_manager=PackageManager.PIP,
                dependencies=dependencies,
                config_files={file_path: FileInfo(file_path, content)},
            )
        except Exception as e:
            raise ParserError(f"Error parsing {file_path}: {str(e)}")

    @staticmethod
    async def _parse_pyproject_toml(content: str, file_path: str) -> DependencyInfo:
        try:
            data = toml.loads(content)
            dependencies = list(
                data.get("tool", {}).get("poetry", {}).get("dependencies", {}).keys()
            )
            dependencies += list(
                data.get("tool", {})
                .get("poetry", {})
                .get("dev-dependencies", {})
                .keys()
            )

            # Exclude 'python' from dependencies
            dependencies = [dep for dep in dependencies if dep.lower() != "python"]

            return DependencyInfo(
                language=Language.PYTHON,
                package_manager=PackageManager.POETRY,
                dependencies=dependencies,
                config_files={file_path: FileInfo(file_path, content)},
            )
        except toml.TomlDecodeError:
            raise ValueError(f"Invalid TOML in file: {file_path}")
