from typing import Optional, Set

from zap.config import AppConfig
from zap.git_analyzer.models.exploration_result import ExplorationResult
from zap.git_analyzer.repo.git_repo import GitRepo


class AppState:
    def __init__(self):
        self.tokenizer = None
        self.repo_metadata: Optional[ExplorationResult] = None
        self._files: Set[str] = set()
        self.git_repo: Optional[GitRepo] = None
        self.config: Optional[AppConfig] = None

    def add_file(self, file: str) -> None:
        self._files.add(file)

    def remove_file(self, file: str) -> None:
        self._files.discard(file)

    def clear_files(self) -> None:
        self._files.clear()

    def get_files(self) -> Set[str]:
        return self._files.copy()

    def remove_files(self, files: Set[str]) -> None:
        self._files.difference_update(files)
