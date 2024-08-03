from dataclasses import dataclass
from typing import Optional


@dataclass
class CodeAnalyzerConfig:
    root_path: str
    cache_dir: str = '.zap_cache'
    encoding: str = 'utf-8'
    repo_url: Optional[str] = None  # Add this line

    def update_root_path(self, new_root_path: str):
        self.root_path = new_root_path
