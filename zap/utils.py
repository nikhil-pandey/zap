import os

import aiofiles


async def get_files_content(root, files):
    """Get content of multiple files."""
    content = ""
    for file in files:
        file_content = await get_file_content(root, file)
        if file_content:
            content += file_content + "\n"
    return content.strip()


async def get_file_content(root, file):
    comment_styles = {
        "py": "#",
        "js": "//",
        "java": "//",
        "c": "//",
        "cpp": "//",
        "html": "<!--",
        "css": "/*",
        "sh": "#",
        "rb": "#",
        "go": "//",
        "rs": "//",
        "php": "//",
        "xml": "<!--",
        "yml": "#",
        "yaml": "#",
        "json": "//",
        "md": "<!--",
        "txt": "#",
    }
    ext = os.path.splitext(file)[1].lstrip(".").lower()
    comment_start = comment_styles.get(ext, "#")

    try:
        async with aiofiles.open(os.path.join(root, file), "r") as f:
            file_content = await f.read()

        formatted_content = (
            f"```{ext}\n{comment_start} filename: {file}\n" + file_content + "\n```"
        )
        return formatted_content
    except Exception as e:
        return None
