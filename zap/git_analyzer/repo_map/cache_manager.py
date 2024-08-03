import aiosqlite
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

CACHE_VERSION = 1


class CacheManager:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "file_cache.db"

    async def _create_table(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS file_cache (
                    file_path TEXT PRIMARY KEY,
                    mtime REAL,
                    tags TEXT,
                    version INTEGER
                )
            ''')
            await db.commit()

    async def get_cache(self, file_path: str) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT mtime, tags, version FROM file_cache WHERE file_path = ?",
                (file_path,)
            )
            result = await cursor.fetchone()
        if result and result[2] == CACHE_VERSION:
            return {
                'mtime': result[0],
                'tags': json.loads(result[1])
            }
        return None

    async def set_cache(self, file_path: str, mtime: float, tags: list[dict[str, Any]]):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO file_cache (file_path, mtime, tags, version) VALUES (?, ?, ?, ?)",
                (file_path, mtime, json.dumps(tags), CACHE_VERSION)
            )
            await db.commit()

    async def clear_cache(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM file_cache")
            await db.commit()

    async def query_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT file_path, tags FROM file_cache WHERE tags LIKE ?",
                (f'%{symbol}%',)
            )
            rows = await cursor.fetchall()

        tags = []
        for row in rows:
            file_path, tags_json = row
            tags_data = json.loads(tags_json)
            for tag_data in tags_data:
                if tag_data['name'] == symbol:
                    tags.append(tag_data)
        return tags
