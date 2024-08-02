import os
from pathlib import Path
from typing import List, Dict
from models import FileInfo, GraphNode, Tag
from tag_extractor import TagExtractor
from zap.git_analyzer.repo_map.cache_manager import CacheManager
from zap.git_analyzer.repo_map.config import Config


class RepoAnalyzer:
    def __init__(self, repo_path: str, config: Config):
        self.repo_path = Path(repo_path)
        self.tag_extractor = TagExtractor()
        self.cache_manager = CacheManager(repo_path + '/.zap_cache')

    def analyze_files(self, file_paths: List[str]) -> Dict[str, FileInfo]:
        file_infos = {}
        for path in file_paths:
            abs_path = self.repo_path / path
            mtime = os.path.getmtime(abs_path)

            cached_data = self.cache_manager.get_cache(str(abs_path))
            if cached_data and cached_data['mtime'] == mtime:
                file_infos[path] = FileInfo(
                    path=cached_data['file_info']['path'],
                    mtime=cached_data['file_info']['mtime'],
                    content=cached_data['file_info']['content'],
                    tags=[Tag(**tag) for tag in cached_data['file_info']['tags']]
                )
                continue

            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tags = self.tag_extractor.extract_tags(str(abs_path), content)
            file_info = FileInfo(path, mtime, content, tags)
            file_infos[path] = file_info

            self.cache_manager.set_cache(str(abs_path), {
                'mtime': mtime,
                'file_info': file_info.to_dict()
            })

        return file_infos

    def build_graph(self, file_infos: Dict[str, FileInfo]) -> Dict[str, GraphNode]:
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
        return graph
