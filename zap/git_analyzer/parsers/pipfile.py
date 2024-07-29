import toml

from .base import DependencyParser
from ..models.dependency import DependencyInfo, FileInfo
from ..models.enums import Language, PackageManager


class PipfileParser(DependencyParser):
    async def parse(self, content: str, file_path: str) -> DependencyInfo:
        try:
            data = toml.loads(content)
            dependencies = list(data.get("packages", {}).keys())
            dependencies.extend(data.get("dev-packages", {}).keys())
            return DependencyInfo(
                language=Language.PYTHON,
                package_manager=PackageManager.PIPENV,
                dependencies=dependencies,
                config_files={file_path: FileInfo(file_path, content)},
            )
        except toml.TomlDecodeError:
            raise ValueError(f"Invalid TOML in Pipfile: {file_path}")
