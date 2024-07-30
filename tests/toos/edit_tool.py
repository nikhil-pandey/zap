import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

from zap.tools.basic_tools import EditFileTool


class TestEditFileTool(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.app_state = MagicMock()
        self.app_state.git_repo.root = self.temp_dir
        self.edit_file_tool = EditFileTool(self.app_state)

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.temp_dir)

    def create_temp_file(self, content):
        fd, path = tempfile.mkstemp(dir=self.temp_dir, text=True)
        with os.fdopen(fd, "w") as temp_file:
            temp_file.write(content)
        return os.path.relpath(path, self.temp_dir)

    async def test_replace_single_line(self):
        content = "line1\nline2\nline3\n"
        filename = self.create_temp_file(content)

        result = await self.edit_file_tool.execute(
            filename=filename, start_line=2, end_line=2, content="new line2"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["edited_lines"], "2-2")

        with open(os.path.join(self.temp_dir, filename), "r") as file:
            self.assertEqual(file.read(), "line1\nnew line2\nline3\n")

    async def test_replace_multiple_lines(self):
        content = "line1\nline2\nline3\nline4\n"
        filename = self.create_temp_file(content)

        result = await self.edit_file_tool.execute(
            filename=filename, start_line=2, end_line=3, content="new line2\nnew line3"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["edited_lines"], "2-3")

        with open(os.path.join(self.temp_dir, filename), "r") as file:
            self.assertEqual(file.read(), "line1\nnew line2\nnew line3\nline4\n")

    async def test_insert_new_line(self):
        content = "line1\nline2\n"
        filename = self.create_temp_file(content)

        result = await self.edit_file_tool.execute(
            filename=filename, start_line=3, end_line=2, content="new line3"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["edited_lines"], "3-2")

        with open(os.path.join(self.temp_dir, filename), "r") as file:
            self.assertEqual(file.read(), "line1\nline2\nnew line3\n")

    async def test_delete_lines(self):
        content = "line1\nline2\nline3\nline4\n"
        filename = self.create_temp_file(content)

        result = await self.edit_file_tool.execute(
            filename=filename, start_line=2, end_line=3, content=""
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["edited_lines"], "2-3")

        with open(os.path.join(self.temp_dir, filename), "r") as file:
            self.assertEqual(file.read(), "line1\nline4\n")

    async def test_replace_block_of_code(self):
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        filename = self.create_temp_file(content)

        new_content = "def new_func():\n    print('Hello')\n    return True"
        result = await self.edit_file_tool.execute(
            filename=filename, start_line=1, end_line=5, content=new_content
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["edited_lines"], "1-5")

        with open(os.path.join(self.temp_dir, filename), "r") as file:
            self.assertEqual(file.read(), new_content + "\n")

    async def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            await self.edit_file_tool.execute(
                filename="non_existent_file.py",
                start_line=1,
                end_line=1,
                content="new content",
            )

    async def test_path_outside_repository(self):
        with self.assertRaises(ValueError):
            await self.edit_file_tool.execute(
                filename="../outside_repo.py",
                start_line=1,
                end_line=1,
                content="new content",
            )


if __name__ == "__main__":
    unittest.main()
