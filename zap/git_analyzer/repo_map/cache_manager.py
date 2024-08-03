# filename: zap/git_analyzer/repo_map/cache_manager.py
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
import json

CACHE_VERSION = 1

class CacheManager:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "file_cache.db"
        self.conn = sqlite3.connect(str(self.db_path))
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS file_cache (
                    file_path TEXT PRIMARY KEY,
                    mtime REAL,
                    tags TEXT,
                    version INTEGER
                )
            ''')

    def get_cache(self, file_path: str) -> Optional[Dict[str, Any]]:
        with self.conn:
            cursor = self.conn.execute(
                "SELECT mtime, tags, version FROM file_cache WHERE file_path = ?",
                (file_path,)
            )
            result = cursor.fetchone()
        if result and result[2] == CACHE_VERSION:
            return {
                'mtime': result[0],
                'tags': json.loads(result[1])
            }
        return None

    def set_cache(self, file_path: str, mtime: float, tags: list[dict[str, Any]]):
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO file_cache (file_path, mtime, tags, version) VALUES (?, ?, ?, ?)",
                (file_path, mtime, json.dumps(tags), CACHE_VERSION)
            )

    def clear_cache(self):
        with self.conn:
            self.conn.execute("DELETE FROM file_cache")

    def close(self):
        self.conn.close()
