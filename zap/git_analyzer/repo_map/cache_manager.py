# In cache_manager.py
import json
from pathlib import Path
from typing import Dict, Any
import os

class CacheManager:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "file_cache.json"
        self.cache: Dict[str, Any] = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if self.cache_file.exists():
            with self.cache_file.open('r') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with self.cache_file.open('w') as f:
            json.dump(self.cache, f)

    def get_cache(self, file_path: str) -> Dict[str, Any] | None:
        return self.cache.get(file_path)

    def set_cache(self, file_path: str, data: Dict[str, Any]):
        self.cache[file_path] = data
        self._save_cache()

    def clear_cache(self):
        self.cache.clear()
        self._save_cache()
