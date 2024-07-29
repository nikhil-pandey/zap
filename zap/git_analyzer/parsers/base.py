from abc import ABC, abstractmethod

from ..models.dependency import DependencyInfo


class DependencyParser(ABC):
    @abstractmethod
    async def parse(self, content: str, file_path: str) -> DependencyInfo:
        """Parse the content of a dependency file and return DependencyInfo."""
        pass
