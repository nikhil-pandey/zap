import aiofiles
import pytest

from zap.utils import get_files_content


@pytest.mark.asyncio
async def test_get_files_content(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "testfile.txt"
    async with aiofiles.open(p, "w") as f:
        await f.write("This is a test file.\nIt has multiple lines.\n")

    content = await get_files_content(d, ["testfile.txt"], prefix_lines=False)
    assert "This is a test file." in content


@pytest.mark.asyncio
async def test_get_files_content_with_prefix(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "testfile.txt"
    async with aiofiles.open(p, "w") as f:
        await f.write("This is a test file.\nIt has multiple lines.\n")

    content = await get_files_content(d, ["testfile.txt"], prefix_lines=True)
    assert "|001|" in content
