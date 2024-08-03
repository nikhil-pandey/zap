# filename: zap/git_analyzer/repo_map/config.py
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    root_path: str
    max_files: int = 20
    max_tags_per_file: int = 50
    languages: list[str] = field(default_factory=lambda: ['python', 'javascript', 'typescript', 'csharp'])
    cache_dir: str = '.zap_cache'
    graph_personalization_weight: float = 1.0
    encoding: str = 'utf-8'
    repo_url: Optional[str] = None  # Add this line

    def update_root_path(self, new_root_path: str):
        self.root_path = new_root_path
