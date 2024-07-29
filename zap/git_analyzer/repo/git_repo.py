import asyncio
import os
from typing import Set, List, Dict

import aiofiles
import pygit2
import pygtrie

from ..exceptions import RepoError
from ..models.dependency import CommitInfo
from ..utils.constants import SEPARATOR


class GitRepo:
    def __init__(self, path: str = None):
        if path is None:
            path = os.getcwd()
        self.path = path
        if not os.path.exists(path):
            raise RepoError(f"Path {path} does not exist")
        self.repo: pygit2.Repository = pygit2.Repository(path)
        self.root = self.repo.workdir
        self.file_trie = pygtrie.StringTrie(separator=SEPARATOR)
        # TODO: this is probably unused with the latest implemetnation
        self.suffix_trie = pygtrie.StringTrie(separator=SEPARATOR)

    async def refresh(self):
        # TODO: make refresh less frequent for performance
        self.repo = pygit2.Repository(self.path)
        self.file_trie.clear()
        self.suffix_trie.clear()
        for entry in self.repo.index:
            self.file_trie[entry.path] = True
            path = SEPARATOR.join(reversed(entry.path.split(SEPARATOR)))
            self.suffix_trie[path] = entry.path

    async def get_tracked_files(self) -> Set[str]:
        await self.refresh()
        return set(self.file_trie.keys())

    async def get_file_content(self, path: str) -> str:
        await self.refresh()
        full_path = os.path.join(self.root, path)
        async with aiofiles.open(full_path, "r") as file:
            return await file.read()

    async def get_status(self) -> Dict[str, List[str]]:
        await self.refresh()

        def _get_status():
            status = self.repo.status()
            return {
                "new": [
                    file
                    for file, flags in status.items()
                    if flags & pygit2.GIT_STATUS_WT_NEW
                ],
                "modified": [
                    file
                    for file, flags in status.items()
                    if flags & pygit2.GIT_STATUS_WT_MODIFIED
                ],
                "deleted": [
                    file
                    for file, flags in status.items()
                    if flags & pygit2.GIT_STATUS_WT_DELETED
                ],
            }

        return await asyncio.to_thread(_get_status)

    async def get_recent_commits(self, limit: int = 10) -> List[CommitInfo]:
        await self.refresh()

        def _get_recent_commits():
            commits = []
            if self.repo.is_empty:
                return commits  # Return an empty list for empty repositories
            for commit in self.repo.walk(self.repo.head.target, pygit2.GIT_SORT_TIME):
                commits.append(
                    CommitInfo(
                        hash=str(commit.id),
                        message=commit.message.strip(),
                        author=commit.author.name,
                        time=commit.author.time,
                    )
                )
                if len(commits) >= limit:
                    break
            return commits

        return await asyncio.to_thread(_get_recent_commits)

    async def get_file_change_count(self) -> Dict[str, int]:
        await self.refresh()

        def _get_file_change_count():
            file_change_count = {}
            if self.repo.is_empty:
                return file_change_count
            for commit in self.repo.walk(self.repo.head.target, pygit2.GIT_SORT_TIME):
                if len(commit.parents) == 0:  # Initial commit
                    for entry in commit.tree:
                        file_change_count[entry.name] = (
                            file_change_count.get(entry.name, 0) + 1
                        )
                else:
                    diff = commit.tree.diff_to_tree(commit.parents[0].tree)
                    for patch in diff:
                        if patch.delta.new_file.path:
                            file_change_count[patch.delta.new_file.path] = (
                                file_change_count.get(patch.delta.new_file.path, 0) + 1
                            )
            return file_change_count

        return await asyncio.to_thread(_get_file_change_count)

    def close(self):
        self.repo.free()

    async def query_folder_async(self, path: str) -> Set[str]:
        if path == "":
            return await self.get_tracked_files()

        files = set()
        try:
            return {k for k, v in self.file_trie.items(path)}
        except KeyError:
            pass
        return files
