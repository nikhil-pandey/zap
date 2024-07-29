from dataclasses import dataclass
from typing import Dict, List, Tuple
from .dependency import ProjectInfo, CommitInfo


@dataclass
class ExplorationResult:
    project_info: ProjectInfo
    relevant_files: Dict[str, int]
    git_status: Dict[str, List[str]]
    recent_commits: List[CommitInfo]
    most_changed_files: List[Tuple[str, int]]
    least_changed_files: List[Tuple[str, int]]
    file_change_count: Dict[str, int]
