from dataclasses import dataclass
from typing import List, Set

@dataclass
class Tag:
    rel_fname: str
    fname: str
    line: int
    name: str
    kind: str

@dataclass
class FileInfo:
    path: str
    mtime: float
    content: str
    tags: List[Tag]

@dataclass
class GraphNode:
    file: str
    references: Set[str]
    definitions: Set[str]
