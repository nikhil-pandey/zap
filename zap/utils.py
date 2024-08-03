import os
import platform
import aiofiles
import re


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


async def get_shell():
    if platform.system() == "Windows":
        shell = os.getenv('COMSPEC')
        if shell:
            return shell
        else:
            return "Unknown (no COMSPEC variable)"
    else:
        shell = os.getenv('SHELL')
        if shell:
            return shell
        else:
            return "Unknown (no SHELL variable)"


async def extract_xml_blocks(tag: str, text: str) -> list[tuple[str, dict]]:
    pattern = re.compile(rf"<{tag}(.*?)>(.*?)</{tag}>", re.DOTALL)
    blocks = pattern.findall(text)
    items = []
    for block in blocks:
        attributes_dict = {}
        attributes = block[0].strip()
        if attributes:
            for attribute in attributes.split():
                key, value = attribute.split("=")
                attributes_dict[key] = value.strip('"')
        items.append((block[1], attributes_dict))
    return items


async def extract_search_replace_blocks(text: str) -> tuple[str, str]:
    if not text.startswith("<<<<<<< SEARCH"):
        return '', text
    pattern = re.compile(r"<<<<<<< SEARCH\n(.*?)=======\n(.*?)\n>>>>>>> REPLACE", re.DOTALL)
    blocks = pattern.findall(text)
    search_block = blocks[0][0].rstrip('\n')
    replace_block = blocks[0][1]
    return search_block, replace_block
