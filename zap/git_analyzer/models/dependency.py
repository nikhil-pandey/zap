from dataclasses import dataclass
from typing import List, Dict

from .enums import Language, PackageManager


@dataclass
class FileInfo:
    path: str
    content: str


@dataclass
class DependencyInfo:
    language: Language
    package_manager: PackageManager
    dependencies: List[str]
    config_files: Dict[str, FileInfo]


@dataclass
class ProjectInfo:
    dependencies: Dict[str, DependencyInfo]


@dataclass
class CommitInfo:
    hash: str
    message: str
    author: str
    time: int
