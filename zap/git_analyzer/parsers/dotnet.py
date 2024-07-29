# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from typing import Dict

from .base import DependencyParser
from ..models.dependency import DependencyInfo, FileInfo
from ..models.enums import Language, PackageManager


class MSBuildContext:
    def __init__(self):
        self.variables: Dict[str, str] = {}

    def set_variable(self, name: str, value: str):
        self.variables[name] = value

    def get_variable(self, name: str) -> str:
        return self.variables.get(name, "")

    def resolve_path(self, path: str) -> str:
        for var, value in self.variables.items():
            path = path.replace(f"$({var})", value)
        return path


class DotNetParser(DependencyParser):
    async def parse(self, content: str, file_path: str) -> DependencyInfo:
        context = MSBuildContext()
        dependencies = []

        try:
            root = ET.fromstring(content)

            # Parse PropertyGroup elements
            for property_group in root.findall(".//PropertyGroup"):
                for prop in property_group:
                    context.set_variable(prop.tag, prop.text or "")

            # Parse PackageReference elements
            for item_group in root.findall(".//ItemGroup"):
                for package_ref in item_group.findall("PackageReference"):
                    if "Include" in package_ref.attrib:
                        dependencies.append(package_ref.attrib["Include"])
                for project_ref in item_group.findall("ProjectReference"):
                    if "Include" in project_ref.attrib:
                        resolved_path = context.resolve_path(
                            project_ref.attrib["Include"]
                        )
                        dependencies.append(f"ProjectReference:{resolved_path}")

            return DependencyInfo(
                language=Language.CSHARP,
                package_manager=PackageManager.NUGET,
                dependencies=dependencies,
                config_files={file_path: FileInfo(file_path, content)},
            )
        except ET.ParseError:
            raise ValueError(f"Invalid XML in file: {file_path}")
