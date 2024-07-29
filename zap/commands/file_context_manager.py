import pathlib
from collections import defaultdict

from rich.text import Text
from rich.tree import Tree

from zap.app_state import AppState
from zap.cliux import UIInterface
from ..constants import FILE_ICONS
from ..git_analyzer.utils.file import get_normalized_path_relative_to_repo


class FileContextManager:
    def __init__(self, state: AppState, ui: UIInterface):
        self.state = state
        self.ui = ui

    async def add(self, *files):
        """Add files to the context."""
        added_files_count = 0
        for file in files:
            file = get_normalized_path_relative_to_repo(file, self.state.git_repo.root)
            if file in await self.state.git_repo.get_tracked_files():
                self.state.add_file(file)
                added_files_count += 1
                self.ui.debug(f"Added {file} to context.")
            else:
                files = await self.state.git_repo.query_folder_async(file)
                if files:
                    for f in files:
                        self.state.add_file(f)
                    added_files_count += len(files)
                    self.ui.debug(f"Added {files} to context.")

        self.ui.print(f"Added {added_files_count} files to context.")

    async def remove(self, *files):
        """Remove files from the context."""
        for file in files:
            file = get_normalized_path_relative_to_repo(file, self.state.git_repo.root)
            if file in await self.state.git_repo.get_tracked_files():
                self.state.remove_file(file)
                self.ui.print(f"Removed {file} from context.")
            else:
                files = await self.state.git_repo.query_folder_async(file)
                if files:
                    self.state.remove_files(files)
                    self.ui.print(f"Removed {len(files)} files from context.")

    async def clear(self):
        """Clear all files from the context."""
        self.ui.print("Cleared all files from context.")
        self.state.clear_files()

    async def list(self):
        """List all files in the context."""
        self.tree(self.state.get_files())

    def tree(self, paths: set[str]) -> None:
        if not paths:
            self.ui.print("No files found.")
            return

        root_path = pathlib.Path(self.state.git_repo.root)
        paths = [root_path / path for path in paths]
        paths.append(root_path)
        paths.sort(key=lambda x: (len(x.parts), x))
        branch_sizes = defaultdict(int)
        # First pass: calculate token counts
        total = 0
        for path in paths:
            if path.is_file():
                try:
                    token_count = len(self.state.tokenizer.encode(path.read_text(encoding='utf-8')))
                    total += token_count
                except Exception as e:
                    self.ui.error(f"Error reading file {path}: {e}")
                    token_count = 0
                current = path
                while current != root_path:
                    branch_sizes[current] += token_count
                    current = current.parent

        root = Tree(f"{FILE_ICONS['dir']} Root ({total} tokens)")
        branches = {root_path: root}
        # Second pass: create tree structure
        for path in paths:
            if path.is_file():
                branch = self._get_or_create_branch(path.parent, branches, branch_sizes)
                icon = FILE_ICONS.get(path.suffix.lstrip('.'), FILE_ICONS['default'])
                text_filename = Text(f"{icon} {path.name}", "green")
                text_filename.highlight_regex(r"\..*$", "bold red")
                text_filename.stylize(f"link file://{path}")
                if branch_sizes[path] > 0:
                    text_filename.append(f" ({branch_sizes[path]} tokens)", "blue")
                branch.add(text_filename)

        self.ui.print(root)

    def _get_or_create_branch(self, path: pathlib.Path, branches: dict[pathlib.Path, Tree],
                              branch_sizes: dict[pathlib.Path, int]) -> Tree:
        if path in branches:
            return branches[path]
        else:
            parent_branch = self._get_or_create_branch(path.parent, branches, branch_sizes)
            token_count = branch_sizes[path]
            label = f"{FILE_ICONS['dir']} {path.name}"
            if token_count > 0:
                label += f" ({token_count} tokens)"
            new_branch = parent_branch.add(label)
            branches[path] = new_branch
            return new_branch
