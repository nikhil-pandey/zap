import os
from pathlib import Path
from typing import List, Dict
from models import FileInfo, GraphNode
from tag_extractor import TagExtractor


class RepoAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.tag_extractor = TagExtractor()

    def analyze_files(self, file_paths: List[str]) -> Dict[str, FileInfo]:
        file_infos = {}
        for path in file_paths:
            abs_path = self.repo_path / path
            mtime = os.path.getmtime(abs_path)
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tags = self.tag_extractor.extract_tags(str(abs_path), content)
            file_infos[path] = FileInfo(path, mtime, content, tags)
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
