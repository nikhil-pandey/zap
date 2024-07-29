import asyncio

from zap.app_state import AppState
from zap.cliux import UIInterface


class GitManager:
    def __init__(self, state: AppState, ui: UIInterface):
        self.ui = ui
        self.state = state

    async def execute(self, *args):
        """Execute a git command."""
        cmd = ["git"] + list(args)
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                self.ui.print(
                    stdout.decode(),
                    language="diff" if "diff" in args else "shell",
                    line_numbers=False,
                )
            else:
                self.ui.error(f"Git command failed: {stderr.decode()}")
        except Exception as e:
            self.ui.exception(e, "Git command failed")

    async def diff(self):
        """Show git diff."""
        await self.execute("diff")
