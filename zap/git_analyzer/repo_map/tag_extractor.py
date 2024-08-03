import os
from typing import List, Dict
from pathlib import Path
from tree_sitter_languages import get_language, get_parser

from zap.git_analyzer.repo_map.constants import filename_to_lang
from zap.git_analyzer.repo_map.models import Tag
import logging


class TagExtractor:
    def __init__(self, root_path: str):
        self.root_path = root_path

    def _get_query_scm(self, lang):
        query_path = Path(__file__).parent / "queries" / f"tree-sitter-{lang}-tags.scm"
        if not query_path.exists():
            return None
        return query_path.read_text()

    def extract_tags(self, fname: str, content: str) -> List[Tag]:
        try:
            lang = filename_to_lang(fname)
            if not lang:
                logging.warning(f"Unsupported language for file: {fname}")
                return []

            language = get_language(lang)
            parser = get_parser(lang)
            query_scm = self._get_query_scm(lang)
            if not query_scm:
                logging.warning(f"No query scheme found for language: {lang}")
                return []

            tree = parser.parse(bytes(content, "utf-8"))
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
                # Since we're looking at the name node, the parent node is the one that contains the actual definition
                body = content[node.parent.start_byte:node.parent.end_byte]
                tags.append(Tag(
                    path=os.path.relpath(fname, self.root_path),
                    name=node.text.decode("utf-8"),
                    kind=kind,
                    line=node.start_point[0] + 1,
                    body=body
                ))
            return tags

        except Exception as e:
            logging.error(f"Error extracting tags from {fname}: {str(e)}")
            raise

    def query_by_symbol(self, file_infos: dict[str, list[Tag]], symbol: str) -> list[Tag]:
        results = []
        for tags in file_infos.values():
            for tag in tags:
                if tag.name == symbol:
                    results.append(tag)
        return results
