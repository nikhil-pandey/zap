# filename: zap/git_analyzer/repo_map/config.py
from dataclasses import dataclass, field


@dataclass
class Config:
    root_path: str
    max_files: int = 20
    max_tags_per_file: int = 50
    languages: list[str] = field(default_factory=lambda: ['python', 'javascript', 'typescript', 'csharp'])
    cache_dir: str = '.zap_cache'
    graph_personalization_weight: float = 1.0
    encoding: str = 'utf-8'
