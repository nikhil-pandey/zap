from dataclasses import dataclass, asdict
from typing import List, Set


@dataclass
class Tag:
    path: str
    line: int
    name: str
    kind: str

    def to_dict(self):
        return asdict(self)


@dataclass
class FileInfo:
    path: str
    mtime: float
    content: str
    tags: List[Tag]

    def to_dict(self):
        return {
            'path': self.path,
            'mtime': self.mtime,
            'content': self.content,
            'tags': [tag.to_dict() for tag in self.tags]
        }


@dataclass
class GraphNode:
    file: str
    references: Set[str]
    definitions: Set[str]

    def to_dict(self):
        return asdict(self)
