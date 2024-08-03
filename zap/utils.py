import os
import platform
import aiofiles
import re
from collections import defaultdict
from itertools import groupby

from zap.constants import EXTENSION_TO_COMMENT
from zap.git_analyzer.repo_map.models import Tag


async def get_files_content(root, files, prefix_lines=True):
    """Get content of multiple files."""
    content = ""
    for file in files:
        file_content = await get_file_content(root, file, prefix_lines)
        if file_content:
            content += file_content + "\n"
    return content.strip()


async def get_file_content(root, file, prefix_lines=True):
    ext = os.path.splitext(file)[1].lstrip(".").lower()
    comment_start = EXTENSION_TO_COMMENT.get(ext, "#")

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


async def get_files_content_from_tags(root: str, tags: list[Tag], prepend_line_numbers: bool = False) -> str:
    files_content = {}

    # Collect unique file paths
    file_paths = set(tag.path for tag in tags)

    # Read each file's content
    for file_path in file_paths:
        p = os.path.join(root, file_path)
        async with aiofiles.open(p, 'r', encoding='utf-8') as f:
            files_content[file_path] = await f.readlines()

    # Preprocess and merge tags ranges
    merged_ranges = defaultdict(list)

    for file_path in file_paths:
        tags_in_file = sorted([tag for tag in tags if tag.path == file_path], key=lambda x: x.start_line)
        merged_range = []

        for tag in tags_in_file:
            if not merged_range:
                merged_range = [tag.start_line, tag.end_line]
            else:
                if tag.start_line <= merged_range[1] + 1:
                    merged_range[1] = max(merged_range[1], tag.end_line)
                else:
                    merged_ranges[file_path].append(merged_range)
                    merged_range = [tag.start_line, tag.end_line]

        if merged_range:
            merged_ranges[file_path].append(merged_range)

    # Collect content based on merged ranges and format it as markdown
    final_content = []

    for file_path in file_paths:
        lines = files_content[file_path]
        current_line = 0
        ext = os.path.splitext(file_path)[1].lstrip(".").lower()
        comment_start = EXTENSION_TO_COMMENT.get(ext, "#")
        file_content = []

        # Always include the first line
        first_line = lines[0]
        if prepend_line_numbers:
            first_line = f"001| {first_line}"
        file_content.append(first_line)
        current_line = 1

        for start_line, end_line in merged_ranges[file_path]:
            if current_line < start_line - 1:
                file_content.append("...\n")
            for i in range(start_line - 1, end_line):
                line = lines[i]
                if prepend_line_numbers:
                    line = f"{i + 1:03d}| {line}"
                file_content.append(line)
            current_line = end_line

        if current_line < len(lines):
            file_content.append("...\n")

        # Always include the last line
        last_line = lines[-1]
        if prepend_line_numbers:
            last_line = f"{len(lines):03d}| {last_line}"
        if lines[-1] not in file_content:
            file_content.append(last_line)

        formatted_content = (
            f"```{ext}\n{comment_start} filename: {file_path}\n" + ''.join(file_content) + "\n```"
        )
        final_content.append(formatted_content)

    return '\n'.join(final_content)


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
