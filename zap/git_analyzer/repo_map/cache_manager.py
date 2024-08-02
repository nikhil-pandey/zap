import json
from pathlib import Path


class CacheManager:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache(self, file_path: str):
        cache_file = self.cache_dir / f"{hash(file_path)}.json"
        if cache_file.exists():
            with cache_file.open('r') as f:
                return json.load(f)
        return None

    def set_cache(self, file_path: str, data: dict):
        cache_file = self.cache_dir / f"{hash(file_path)}.json"
        with cache_file.open('w') as f:
            json.dump(data, f)
