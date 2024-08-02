import os
from typing import List
from models import Tag


def read_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()


def get_file_mtime(path: str) -> float:
    return os.path.getmtime(path)


def extract_tags(content: str, filename: str) -> List[Tag]:
    # This is a placeholder. In a real implementation, you'd use a proper
    # parser to extract tags from the file content.
    tags = []
    for i, line in enumerate(content.split('\n')):
        if 'def ' in line:
            name = line.split('def ')[1].split('(')[0]
            tags.append(Tag(filename, filename, i + 1, name, 'def'))
        elif 'class ' in line:
            name = line.split('class ')[1].split('(')[0]
            tags.append(Tag(filename, filename, i + 1, name, 'def'))
    return tags
