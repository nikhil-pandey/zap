import os

from .constants import SEPARATOR


def get_normalized_path_relative_to_repo(path: str, repo_path: str) -> str:
    """
    Get the normalized path relative to the repository path.
    """
    if not os.path.isabs(path):
        path = os.path.join(repo_path, path)

    rel_path = os.path.relpath(path, repo_path)
    if rel_path.startswith(".."):
        raise ValueError(f"Path {path} is not inside the repository {repo_path}")

    if rel_path == ".":
        return ""
    return rel_path.replace(os.sep, SEPARATOR)
