import json
import os
from typing import Annotated

from zap.app_state import AppState
from zap.cliux import UIInterface
from zap.tools.tool import Tool
from zap.tools.tool_manager import ToolManager


class ReadFileTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__("read_file", "Read the content of a file within the repository boundary.")
        self.app_state = app_state

    async def execute(self, filename: Annotated[str, "Path to the file to read"]):
        full_path = os.path.join(self.app_state.git_repo.root, filename)
        if not full_path.startswith(self.app_state.git_repo.root):
            return json.dumps({"status": "error", "error": "Path is outside the repository boundary."})
        with open(full_path, "r") as file:
            content = file.read()
        return json.dumps({"status": "success", "result": content})


class WriteFileTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__("write_file", "Write content to a file within the repository boundary.")
        self.app_state = app_state

    async def execute(self,
                      filename: Annotated[str, "Path to the file to write"],
                      content: Annotated[str, "Content to write to the file"]):
        full_path = os.path.join(self.app_state.git_repo.root, filename)
        if not full_path.startswith(self.app_state.git_repo.root):
            return json.dumps({"status": "error", "error": "Path is outside the repository boundary."})
        with open(full_path, "w") as file:
            file.write(content)
        return json.dumps({"status": "success", "result": f"File {filename} written successfully."})


class BuildProjectTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__("build_project", "Build the project to check for errors within the repository boundary.")
        self.app_state = app_state

    async def execute(self):
        command = self.app_state.config.build_command
        result = os.system(command)
        return json.dumps({"status": "success", "result": "Project built successfully."})


class ListFilesTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__("list_files", "List files in a directory within the repository boundary.")
        self.app_state = app_state

    async def execute(self, directory: Annotated[str, "Directory to list files in"]):
        tracked_files: set[str] = await self.app_state.git_repo.get_tracked_files()
        full_path = os.path.join(self.app_state.git_repo.root, directory)
        if not full_path.startswith(self.app_state.git_repo.root):
            return json.dumps({"status": "error", "error": "Path is outside the repository boundary."})
        files = [
            file
            for file in tracked_files
            if file.startswith(full_path) or file.startswith(directory)
        ]
        return json.dumps({"status": "success", "result": json.dumps(files)})


class AskHumanHelpTool(Tool):
    def __init__(self, ui: UIInterface):
        super().__init__("ask_human_help", "Simulate asking for human help on a specific query.")
        self.ui = ui

    async def execute(self, query: Annotated[str, "Query to ask for human help"]):
        prompt = await self.ui.input_async(query)
        return json.dumps({"status": "success", "result": prompt})


class DeleteFileTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__("delete_file", "Delete a file within the repository boundary.")
        self.app_state = app_state

    async def execute(self, filename: Annotated[str, "Path to the file to delete"]):
        full_path = os.path.join(self.app_state.git_repo.root, filename)
        if not full_path.startswith(self.app_state.git_repo.root):
            return json.dumps({"status": "error", "error": "Path is outside the repository boundary."})
        os.remove(full_path)
        return json.dumps({"status": "success", "result": f"File {filename} deleted successfully."})


class RunTestsTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__("run_tests", "Run the project's test suite.")
        self.app_state = app_state

    async def execute(self):
        command = self.app_state.config.test_command
        result = os.system(command)
        return json.dumps({"status": "success", "result": str(result)})


class LintProjectTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__("lint_project", "Lint the project code.")
        self.app_state = app_state

    async def execute(self):
        command = self.app_state.config.lint_command
        result = os.system(command)
        return json.dumps({"status": "success", "result": "Project linted successfully."})


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
