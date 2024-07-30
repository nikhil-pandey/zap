import os

import aiofiles
import aiohttp

from .resolver import PathResolver


class DefaultPathResolver(PathResolver):
    def __init__(self, root_path: str = None):
        self.root_path = root_path or os.getcwd()

    async def resolve_file(self, path: str) -> str:
        if os.path.isabs(path):
            file_path = path
        else:
            file_path = os.path.join(self.root_path, path)

        async with aiofiles.open(file_path, mode="r", encoding='utf-8') as file:
            content = await file.read()
        return content

    async def resolve_http(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
