import asyncio
import os
from typing import Annotated, Optional

from zap.app_state import AppState
from zap.cliux import UIInterface
from zap.tools.tool import Tool
from zap.tools.tool_manager import ToolManager


class ShellCommandTool(Tool):
    def __init__(self, name: str, description: str, app_state: AppState):
        super().__init__(name, description)
        self.app_state = app_state

    async def run_command(self, command: str) -> dict:
        if not command:
            raise ValueError("Command not configured.")
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
        with open(full_path, "r", encoding='utf-8') as file:
            lines = file.readlines()

        # Prefix lines with line numbers
        # prefixed_lines = [f"|{idx + 1:03d}|{line}" for idx, line in enumerate(lines)]
        # content = "".join(prefixed_lines)
        content = "".join(lines)

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
        with open(full_path, "w", encoding="utf-8") as file:
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
        if directory == "./" or directory == "." or directory == "":
            raise ValueError(
                "You cannot list all files in the repository. Be more specific."
            )

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


class RawShellCommandTool(ShellCommandTool):
    ALLOWED_COMMANDS = [
        "ls",
        "pwd",
        "echo",
        "cat",
        "git",
        "python",
        "pip",
        "poetry",
        "pytest",
        "flake8",
        "black",
        "sed",
        "awk",
        "find",
        "grep",
        "sort",
        "uniq",
        "wc",
        "head",
        "tail",
        "touch",
        "cp",
        "dir",
        "cd",
        "type",
        "where",
        "set",
        "cls",
        "copy",
        "move",
        "ren",
        "mkdir",
        "xcopy",
        "md",
    ]

    def __init__(self, app_state: AppState):
        super().__init__("shell_command", "Run a raw shell command.", app_state)

    async def execute(self, command: Annotated[str, "Command to run"]):
        if not any(
            command.startswith(allowed_command)
            for allowed_command in self.ALLOWED_COMMANDS
        ):
            raise ValueError(
                f"Command not allowed. Allowed commands: {self.ALLOWED_COMMANDS}"
            )
        return await self.run_command(command)


class EditFileTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__(
            "edit_file",
            "Edit the content of a file within the repository boundary between start line and end line.",
        )
        self.app_state = app_state

    async def execute(
        self,
        filename: Annotated[str, "Path to the file to edit"],
        start_line: Annotated[int, "The starting line number (1-indexed)"],
        end_line: Annotated[int, "The ending line number (1-indexed)"],
        content: Annotated[str, "Content to replace in the specified lines"],
    ):
        full_path = os.path.join(self.app_state.git_repo.root, filename)
        if not full_path.startswith(self.app_state.git_repo.root):
            raise ValueError("Path is outside the repository boundary.")
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {filename} does not exist.")

        with open(full_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Adjust for zero-indexed list
        start_line -= 1
        end_line -= 1

        # Replace lines
        lines[start_line: end_line + 1] = [content + "\n"]

        with open(full_path, "w", encoding="utf-8") as file:
            file.writelines(lines)

        return {
            "status": "success" if abs(end_line - start_line) < 20 else "warning",
            "message": f"File {filename} edited successfully.",
            "edited_lines": f"{start_line + 1}-{end_line + 1}",
        }


class ReplaceBlockTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__("search_replace", "Replace a block of text in a file.")
        self.app_state = app_state

    async def execute(
        self,
        filename: Annotated[str, "Path to the file to edit"],
        search_block: Annotated[str, "Block of text to search for"],
        replace_block: Annotated[str, "Block of text to replace with"],
    ):
        full_path = os.path.join(self.app_state.git_repo.root, filename)
        if not full_path.startswith(self.app_state.git_repo.root):
            raise ValueError("Path is outside the repository boundary.")
        if not os.path.exists(full_path) or search_block is None or search_block == "":
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as file:
                file.write(replace_block)
            return {
                "status": "success",
                "message": f"File {filename} created successfully.",
            }

        with open(full_path, "r", encoding="utf-8") as file:
            content = file.read()

        if search_block not in content:
            return {
                "status": "failed",
                "message": f"Search block not found in file {filename}. Make sure everything including whitespace is correct.",
            }

        updated_content = content.replace(search_block, replace_block)

        with open(full_path, "w", encoding="utf-8") as file:
            file.write(updated_content)

        return {
            "status": "success",
            "message": f"Block replaced successfully in file {filename}.",
        }


class SearchTagTool(Tool):
    def __init__(self, app_state: AppState):
        super().__init__("search_symbol", "Search for a symbol within the repository boundary.")
        self.app_state = app_state

    async def execute(self, symbol: Annotated[str, "Symbol to search for"],
                      kind: Optional[Annotated[str, "Filter by kind (def or ref)"]] = None):
        tag_data = await self.app_state.code_analyzer.query_symbol(symbol)
        if kind:
            tag_data = [tag for tag in tag_data if tag.kind == kind]
        return {
            "status": "success",
            "tags": [tag.__dict__ for tag in tag_data],
            "count": len(tag_data)
        }


def register_tools(tool_manager: ToolManager, app_state: AppState, ui: UIInterface):
    tool_manager.register_tool(ReadFileTool(app_state))
    tool_manager.register_tool(WriteFileTool(app_state))
    tool_manager.register_tool(BuildProjectTool(app_state))
    tool_manager.register_tool(ListFilesTool(app_state))
    tool_manager.register_tool(AskHumanHelpTool(ui))
    tool_manager.register_tool(DeleteFileTool(app_state))
    tool_manager.register_tool(RunTestsTool(app_state))
    tool_manager.register_tool(LintProjectTool(app_state))
    tool_manager.register_tool(RawShellCommandTool(app_state))
    tool_manager.register_tool(EditFileTool(app_state))
    tool_manager.register_tool(ReplaceBlockTool(app_state))
    tool_manager.register_tool(SearchTagTool(app_state))
