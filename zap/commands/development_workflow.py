import asyncio

from zap.cliux import UIInterface
from zap.config import AppConfig


class DevelopmentWorkflow:
    def __init__(self, config: AppConfig, ui: UIInterface):
        self.config = config
        self.ui = ui

    async def _run_command(self, command: str):
        try:
            proc = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                self.ui.print(stdout.decode())
            else:
                self.ui.error(f"Command failed: {stderr.decode()}")
        except Exception as e:
            self.ui.exception(e, "Command failed")

    async def lint(self):
        """Run linting."""
        lint_command = self.config.lint_command
        await self._run_command(lint_command)

    async def build(self):
        """Run build process."""
        build_command = self.config.build_command
        await self._run_command(build_command)

    async def test(self):
        """Run tests."""
        test_command = self.config.test_command
        await self._run_command(test_command)
