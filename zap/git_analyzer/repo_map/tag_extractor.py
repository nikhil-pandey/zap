import os
from typing import List
from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_rust as tsrust
import tree_sitter_c_sharp as tscsharp
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Token
from pygments.util import ClassNotFound
from zap.git_analyzer.repo_map.models import Tag
import logging


class TagExtractor:
    def __init__(self):
        self.languages = {
            'python': Language(tspython.language()),
            'rust': Language(tsrust.language()),
            'csharp': Language(tscsharp.language()),
        }
        self.parsers = {}

    def _get_language(self, lang):
        return self.languages[lang]

    def _get_parser(self, lang):
        if lang not in self.parsers:
            language = self._get_language(lang)
            parser = Parser()
            parser.set_language(language)
            self.parsers[lang] = parser
        return self.parsers[lang]

    def _get_query_scm(self, lang):
        query_path = Path(__file__).parent / "queries" / f"tree-sitter-{lang}-tags.scm"
        if not query_path.exists():
            return None
        return query_path.read_text()

    def extract_tags(self, fname: str, content: str) -> List[Tag]:
        try:
            lang = self._filename_to_lang(fname)
            if not lang:
                logging.warning(f"Unsupported language for file: {fname}")
                return []

            parser = self._get_parser(lang)
            query_scm = self._get_query_scm(lang)
            if not query_scm:
                logging.warning(f"No query scheme found for language: {lang}")
                return []

            tree = parser.parse(bytes(content, "utf-8"))
            query = self._get_language(lang).query(query_scm)
            captures = query.captures(tree.root_node)

            tags = []
            for node, tag in captures:
                if tag.startswith("name.definition."):
                    kind = "def"
                elif tag.startswith("name.reference."):
                    kind = "ref"
                else:
                    continue

                tags.append(Tag(
                    rel_fname=os.path.relpath(fname),
                    fname=fname,
                    name=node.text.decode("utf-8"),
                    kind=kind,
                    line=node.start_point[0] + 1,
                ))

            # Add references from lexer if no references were found
            if not any(tag.kind == "ref" for tag in tags):
                try:
                    lexer = guess_lexer_for_filename(fname, content)
                    tokens = lexer.get_tokens(content)
                    for token_type, token_value in tokens:
                        if token_type in Token.Name:
                            tags.append(Tag(
                                rel_fname=os.path.relpath(fname),
                                fname=fname,
                                name=token_value,
                                kind="ref",
                                line=-1,
                            ))
                except ClassNotFound:
                    pass

            return tags

        except Exception as e:
            logging.error(f"Error extracting tags from {fname}: {str(e)}")
            return []

    def _filename_to_lang(self, filename):
        ext = Path(filename).suffix
        if ext == ".py":
            return "python"
        elif ext == ".rs":
            return "rust"
        elif ext == ".cs":
            return "csharp"
        return None
