import subprocess

import pyperclip

from zap.app_state import AppState
from zap.cliux import UIInterface
from zap.utils import get_files_content


class UtilityCommands:
    def __init__(self, state: AppState, ui: UIInterface):
        self.state = state
        self.ui = ui

    async def copy_to_clipboard(self):
        """Copy content of all files in context to clipboard."""

        if not self.state.get_files():
            self.ui.print("No files in context to copy.")
            return

        comment_styles = {
            "py": ("#", "#"),
            "js": ("//", "//"),
            "java": ("//", "//"),
            "c": ("//", "//"),
            "cpp": ("//", "//"),
            "html": ("<!--", "-->"),
            "css": ("/*", "*/"),
            "sh": ("#", "#"),
            "rb": ("#", "#"),
            "go": ("//", "//"),
            "rs": ("//", "//"),
            "php": ("//", "//"),
            "xml": ("<!--", "-->"),
            "yml": ("#", "#"),
            "yaml": ("#", "#"),
            "json": ("//", "//"),
            "md": ("<!--", "-->"),
            "txt": ("#", "#"),
        }
        root = self.state.git_repo.root

        content = await get_files_content(root, self.state.get_files())
        try:
            pyperclip.copy(content)
            encoded = (
                self.state.tokenizer.encode(content) if self.state.tokenizer else []
            )
            self.ui.print(f"Copied {len(encoded)} tokens to clipboard.")
        except Exception as e:
            self.ui.error(f"Failed to copy to clipboard: {str(e)}")

    async def shell(self, command: str):
        """Execute a shell command."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            self.ui.syntax_highlight(result.stdout, "shell", False)
        except subprocess.CalledProcessError as e:
            self.ui.error(f"Shell command failed: {e.stderr}")
