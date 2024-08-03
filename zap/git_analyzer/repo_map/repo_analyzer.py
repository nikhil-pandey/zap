import os
from pathlib import Path
from zap.git_analyzer.repo_map.models import FileInfo, GraphNode, Tag
from zap.git_analyzer.repo_map.tag_extractor import TagExtractor
from zap.git_analyzer.repo_map.cache_manager import CacheManager
from zap.git_analyzer.logger import LOGGER


class RepoAnalyzer:
    def __init__(self, repo_path: str, config):
        self.repo_path = Path(repo_path)
        self.tag_extractor = TagExtractor(repo_path)
        self.cache_manager = CacheManager(os.path.join(repo_path, config.cache_dir))
        self.config = config

    def analyze_files(self, file_paths: list[str]) -> dict[str, FileInfo]:
        file_infos = {}
        for path in file_paths:
            abs_path = self.repo_path / path
            rel_path = os.path.relpath(abs_path, self.repo_path)
            mtime = os.path.getmtime(abs_path)

            cached_data = self.cache_manager.get_cache(rel_path)
            if cached_data and cached_data['mtime'] == mtime:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                file_infos[path] = FileInfo(
                    path=path,
                    mtime=mtime,
                    content=content,
                    tags=[Tag(**tag) for tag in cached_data['tags']]
                )
                continue

            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tags = self.tag_extractor.extract_tags(str(abs_path), content)
                file_info = FileInfo(path, mtime, content, tags)
                file_infos[path] = file_info

                self.cache_manager.set_cache(rel_path, mtime, [tag.to_dict() for tag in tags])
            except Exception as e:
                LOGGER.error(f"Error analyzing file {abs_path}: {str(e)}")

        return file_infos

    def build_graph(self, file_infos: dict[str, FileInfo]) -> dict[str, GraphNode]:
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

    def query_symbol(self, symbol: str) -> list[Tag]:
        file_infos = self.analyze_files(list(self.repo_path.rglob("*.py")))
        tags_by_file = {file: info.tags for file, info in file_infos.items()}
        return self.tag_extractor.query_by_symbol(tags_by_file, symbol)

    def __del__(self):
        if hasattr(self, 'cache_manager'):
            self.cache_manager.close()
