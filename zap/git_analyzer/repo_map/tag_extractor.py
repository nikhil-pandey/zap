import os
from typing import List
from pathlib import Path
from tree_sitter_languages import get_language, get_parser

from zap.git_analyzer.repo_map.constants import filename_to_lang
from zap.git_analyzer.repo_map.models import Tag
import logging

LOGGER = logging.getLogger("git_analyzer")

class TagExtractor:
    def __init__(self, root_path: str, encoding: str = 'utf-8'):
        self.root_path = root_path
        self.encoding = encoding

    def _get_query_scm(self, lang):
        query_path = Path(__file__).parent / "queries" / f"tree-sitter-{lang}-tags.scm"
        if not query_path.exists():
            return None
        return query_path.read_text()

    def extract_tags(self, fname: str, content: str) -> List[Tag]:
        try:
            lang = filename_to_lang(fname)
            if not lang:
                LOGGER.warning(f"Unsupported language for file: {fname}")
                return []

            language = get_language(lang)
            parser = get_parser(lang)
            query_scm = self._get_query_scm(lang)
            if not query_scm:
                LOGGER.warning(f"No query scheme found for language: {lang}")
                return []

            tree = parser.parse(bytes(content, self.encoding))
            query = language.query(query_scm)
            captures = query.captures(tree.root_node)

            tags = []
            for node, tag in captures:
                kind = ""
                if tag.startswith("name.definition."):
                    kind = "def"
                elif tag.startswith("name.reference."):
                    kind = "ref"
                if not kind:
                    continue
                body = content[node.parent.start_byte:node.parent.end_byte]
                tags.append(Tag(
                    path=os.path.relpath(fname, self.root_path),
                    name=node.text.decode(self.encoding),
                    kind=kind,
                    line=node.start_point[0] + 1,
                    body=body
                ))
            LOGGER.info(f"Extracted {len(tags)} tags from {fname}")
            return tags

        except Exception as e:
            LOGGER.error(f"Error extracting tags from {fname}: {str(e)}")
            raise
