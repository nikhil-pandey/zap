import os
from pathlib import Path
import asyncio

from zap.git_analyzer.repo_map.config import Config
from zap.git_analyzer.repo_map.models import FileInfo, GraphNode, Tag
from zap.git_analyzer.repo_map.tag_extractor import TagExtractor
from zap.git_analyzer.repo_map.cache_manager import CacheManager
from zap.git_analyzer.logger import LOGGER


class RepoAnalyzer:
    def __init__(self, config: Config):
        self.config = config
        self.tag_extractor = TagExtractor(config.root_path, config.encoding)
        self.cache_manager = CacheManager(os.path.join(self.config.root_path, config.cache_dir))

    async def analyze_files(self, file_paths: list[str]) -> dict[str, FileInfo]:
        file_infos = {}
        root_path = Path(self.config.root_path)
        tasks = []

        for path in file_paths:
            tasks.append(self._analyze_file(root_path, path))

        results = await asyncio.gather(*tasks)

        for path, file_info in results:
            if file_info:
                file_infos[path] = file_info

        return file_infos

    async def _analyze_file(self, root_path, path):
        abs_path = root_path / path
        rel_path = os.path.relpath(abs_path, self.config.root_path)
        mtime = os.path.getmtime(abs_path)

        cached_data = await self.cache_manager.get_cache(rel_path)
        if cached_data and cached_data['mtime'] == mtime:
            with open(abs_path, 'r', encoding=self.config.encoding) as f:
                content = f.read()
            file_info = FileInfo(
                path=path,
                mtime=mtime,
                content=content,
                tags=[Tag(**tag) for tag in cached_data['tags']]
            )
            return path, file_info

        try:
            with open(abs_path, 'r', encoding=self.config.encoding) as f:
                content = f.read()
            tags = self.tag_extractor.extract_tags(str(abs_path), content)
            file_info = FileInfo(path, mtime, content, tags)
            await self.cache_manager.set_cache(rel_path, mtime, [tag.to_dict() for tag in tags])
            return path, file_info
        except Exception as e:
            LOGGER.error(f"Error analyzing file {abs_path}: {str(e)}")
            return path, None

    async def build_graph(self, file_infos: dict[str, FileInfo]) -> dict[str, GraphNode]:
        graph = {}
        for file_path, file_info in file_infos.items():
            references = set()
            definitions = set()
            for tag in file_info.tags:
                if tag.kind == "def":
                    definitions.add(tag.name)
                elif tag.kind == "ref":
                    references.add(tag.name)
            graph[file_path] = GraphNode(file_path, references, definitions)

        # Adding relations between files based on references and definitions
        for file_path, file_info in file_infos.items():
            for tag in file_info.tags:
                if tag.kind == "ref":
                    for def_file_path, def_file_info in file_infos.items():
                        if tag.name in [d.name for d in def_file_info.tags if d.kind == "def"]:
                            # Ensure bi-directional edge
                            if file_path != def_file_path:
                                graph[file_path].references.add(def_file_path)
                                graph[def_file_path].references.add(file_path)  # Adding reverse reference
        return graph

    async def query_symbol(self, symbol: str) -> list[Tag]:
        tag_data = await self.cache_manager.query_symbol(symbol)
        return [Tag(**tag) for tag in tag_data]

    async def close(self):
        if hasattr(self, 'cache_manager'):
            await self.cache_manager.close()
