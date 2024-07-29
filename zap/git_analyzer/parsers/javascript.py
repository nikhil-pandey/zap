import json

from .base import DependencyParser
from ..models.dependency import DependencyInfo, FileInfo
from ..models.enums import Language, PackageManager


class JavaScriptParser(DependencyParser):
    async def parse(self, content: str, file_path: str) -> DependencyInfo:
        try:
            data = json.loads(content)
            dependencies = list(data.get("dependencies", {}).keys())
            dependencies.extend(data.get("devDependencies", {}).keys())
            dependencies.extend(data.get("peerDependencies", {}).keys())

            return DependencyInfo(
                language=Language.JAVASCRIPT,
                package_manager=PackageManager.NPM,
                dependencies=dependencies,
                config_files={file_path: FileInfo(file_path, content)},
            )
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in file: {file_path}")
