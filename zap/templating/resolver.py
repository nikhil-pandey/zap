from abc import ABC, abstractmethod


class PathResolver(ABC):

    @abstractmethod
    async def resolve_file(self, path: str) -> str:
        pass

    @abstractmethod
    async def resolve_http(self, url: str) -> str:
        pass
