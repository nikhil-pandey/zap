import os
import asyncio
from typing import Annotated

from zap.app_state import AppState
from zap.cliux import UIInterface
from zap.tools.tool import Tool
from zap.tools.tool_manager import ToolManager


class ShellCommandTool(Tool):
    def __init__(self, name: str, description: str, app_state: AppState):
        super().__init__(name, description)
        self.app_state = app_state

    async def run_command(self, command: str) -> dict:
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        stdout_str = stdout.decode().strip()
        stderr_str = stderr.decode().strip()

        return {
            "status": "success" if process.returncode == 0 else "failed",
            "exit_code": process.returncode,
            "stdout": stdout_str,
            "stderr": stderr_str,
        }


class ReadFileTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__(
            "read_file", "Read the content of a file within the repository boundary."
        )
        self.app_state = app_state

    async def execute(self, filename: Annotated[str, "Path to the file to read"]):
        full_path = os.path.join(self.app_state.git_repo.root, filename)
        if not full_path.startswith(self.app_state.git_repo.root):
            raise ValueError("Path is outside the repository boundary.")
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {filename} does not exist.")
        with open(full_path, "r") as file:
            content = file.read()
        return {"status": "success", "content": content, "size": len(content)}


class WriteFileTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__(
            "write_file", "Write content to a file within the repository boundary."
        )
        self.app_state = app_state

    async def execute(
        self,
        filename: Annotated[str, "Path to the file to write"],
        content: Annotated[str, "Content to write to the file"],
    ):
        full_path = os.path.join(self.app_state.git_repo.root, filename)
        if not full_path.startswith(self.app_state.git_repo.root):
            raise ValueError("Path is outside the repository boundary.")
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as file:
            file.write(content)
        return {
            "status": "success",
            "message": f"File {filename} written successfully.",
            "size": len(content),
        }


class BuildProjectTool(ShellCommandTool):
    def __init__(self, app_state: AppState):
        super().__init__(
            "build_project",
            "Build the project to check for errors within the repository boundary.",
            app_state,
        )

    async def execute(self):
        result = await self.run_command(self.app_state.config.build_command)
        result["message"] = (
            "Project built successfully."
            if result["status"] == "success"
            else "Build failed."
        )
        return result


class ListFilesTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__(
            "list_files", "List files in a directory within the repository boundary."
        )
        self.app_state = app_state

    async def execute(self, directory: Annotated[str, "Directory to list files in"]):
        tracked_files: set[str] = await self.app_state.git_repo.get_tracked_files()
        full_path = os.path.join(self.app_state.git_repo.root, directory)
        if not full_path.startswith(self.app_state.git_repo.root):
            raise ValueError("Path is outside the repository boundary.")
        files = [
            file
            for file in tracked_files
            if file.startswith(full_path) or file.startswith(directory)
        ]
        return {"status": "success", "files": files, "count": len(files)}


class AskHumanHelpTool(Tool):
    def __init__(self, ui: UIInterface):
        super().__init__(
            "ask_human_help", "Simulate asking for human help on a specific query."
        )
        self.ui = ui

    async def execute(self, query: Annotated[str, "Query to ask for human help"]):
        response = await self.ui.input_async(query)
        return {"status": "success", "response": response}


class DeleteFileTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__("delete_file", "Delete a file within the repository boundary.")
        self.app_state = app_state

    async def execute(self, filename: Annotated[str, "Path to the file to delete"]):
        full_path = os.path.join(self.app_state.git_repo.root, filename)
        if not full_path.startswith(self.app_state.git_repo.root):
            raise ValueError("Path is outside the repository boundary.")
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {filename} does not exist.")
        os.remove(full_path)
        return {
            "status": "success",
            "message": f"File {filename} deleted successfully.",
        }


class RunTestsTool(ShellCommandTool):
    def __init__(self, app_state: AppState):
        super().__init__("run_tests", "Run the project's test suite.", app_state)

    async def execute(self):
        result = await self.run_command(self.app_state.config.test_command)
        result["message"] = (
            "Tests ran successfully."
            if result["status"] == "success"
            else "Tests failed."
        )
        return result


class LintProjectTool(ShellCommandTool):
    def __init__(self, app_state: AppState):
        super().__init__("lint_project", "Lint the project code.", app_state)

    async def execute(self):
        result = await self.run_command(self.app_state.config.lint_command)
        result["message"] = (
            "Project linted successfully."
            if result["status"] == "success"
            else "Linting failed."
        )
        return result


# Tool registration
def register_tools(tool_manager: ToolManager, app_state: AppState, ui: UIInterface):
    tool_manager.register_tool(ReadFileTool(app_state))
    tool_manager.register_tool(WriteFileTool(app_state))
    tool_manager.register_tool(BuildProjectTool(app_state))
    tool_manager.register_tool(ListFilesTool(app_state))
    tool_manager.register_tool(AskHumanHelpTool(ui))
    tool_manager.register_tool(DeleteFileTool(app_state))
    tool_manager.register_tool(RunTestsTool(app_state))
    tool_manager.register_tool(LintProjectTool(app_state))
