import os

import aiofiles


async def get_files_content(root, files, prefix_lines=True):
    """Get content of multiple files."""
    content = ""
    for file in files:
        file_content = await get_file_content(root, file, prefix_lines)
        if file_content:
            content += file_content + "\n"
    return content.strip()


async def get_file_content(root, file, prefix_lines=True):
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

        if prefix_lines:
            lines = file_content.splitlines()
            prefixed_lines = [
                f"|{idx + 1:03d}|{line}" for idx, line in enumerate(lines)
            ]
            file_content = "\n".join(prefixed_lines)

        formatted_content = (
            f"```{ext}\n{comment_start} filename: {file}\n" + file_content + "\n```"
        )
        return formatted_content
    except Exception as e:
        return None


async def get_lite_llm_model(provider: str, model: str):
    if provider == "azure":
        return f"azure/{model}"
    else:
        return model


async def get_tokenizer_model(provider: str, model: str):
    if provider == "azure":
        return model
    return "gpt-4o"
