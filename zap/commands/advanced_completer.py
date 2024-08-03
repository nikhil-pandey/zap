import heapq
import os
from typing import Iterable

from fuzzywuzzy import fuzz
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.shortcuts import CompleteStyle


class AdvancedCompleter(Completer):
    def __init__(self, registry, state, ui=None):
        self.registry = registry
        self.state = state
        self.ui = ui
        self.session = None

    def set_session(self, session):
        self.session = session

    def get_completions(
        self, document: Document, complete_event
    ) -> Iterable[Completion]:
        text = document.text
        if text.startswith(("/add ", "/a ")):
            return self._get_file_completions(text)
        elif text.startswith(("/remove ", "/rm ")):
            return self._get_remove_completions(text)
        elif not text.endswith(" ") and len(text.split()) <= 1:
            return self._get_command_completions(text)
        return []

    def _get_file_completions(self, text) -> Iterable[Completion]:
        self._set_complete_style(CompleteStyle.MULTI_COLUMN)
        path_to_complete = self._get_last_word(text)
        return self.get_file_completions(path_to_complete)

    def _get_remove_completions(self, text):
        self._set_complete_style(CompleteStyle.MULTI_COLUMN)
        path_to_complete = self._get_last_word(text)
        files = self.state.get_files()
        if not files:
            return [
                Completion(
                    "No files to remove",
                    start_position=-len(path_to_complete),
                    display_meta="Error",
                )
            ]
        return [
            Completion(file, start_position=-len(path_to_complete))
            for file in files
            if file.startswith(path_to_complete)
        ]

    def _get_command_completions(self, text):
        self._set_complete_style(CompleteStyle.COLUMN)
        without_slash = text[1:] if text.startswith("/") else text
        heap = []
        for command in self.registry.get_all_commands(show_hidden=True):
            ratio = fuzz.partial_ratio(without_slash, command["Command"])
            if self._should_include_command(without_slash, command["Command"], ratio):
                heapq.heappush(heap, (-ratio, (command["Command"], command)))
        return [
            Completion(
                cmd["Command"],
                start_position=-len(text),
                display_meta=cmd["Description"],
            )
            for _, (_, cmd) in heap
        ]

    def _set_complete_style(self, style):
        if self.session:
            self.session.complete_style = style

    @staticmethod
    def _get_last_word(text):
        return (
            text.split()[-1] if len(text.split()) > 1 and not text.endswith(" ") else ""
        )

    @staticmethod
    def _should_include_command(without_slash, command, ratio):
        return (
            not without_slash
            or command.startswith(without_slash)
            or without_slash.strip() == ""
            or ratio > 80
        )

    def get_file_completions(self, prefix: str) -> list[Completion]:
        completions = []
        directory, partial_name = os.path.split(prefix)

        def traverse(path_conv, path, children, value=None):
            try:
                full_path = path_conv(path)
                if full_path.startswith(prefix):
                    relative_path = self._get_relative_path(
                        full_path, directory, value is not None
                    )
                    if relative_path.startswith(partial_name):
                        completions.append(
                            Completion(relative_path, start_position=-len(partial_name))
                        )
                    return list(children) if value is None else []
                elif os.path.commonprefix([full_path, prefix]) == full_path:
                    return list(children)
                return []
            except Exception as ex:
                self.ui.exception(ex, "An error occurred while trying to complete")
                return []

        try:
            if not directory:
                self.state.git_repo.file_trie.traverse(traverse)
            else:
                self.state.git_repo.file_trie.traverse(traverse, prefix=directory)
        except KeyError:
            pass
        except Exception as e:
            self.ui.exception(e, "An error occurred while trying to complete")

        return completions

    @staticmethod
    def _get_relative_path(full_path, directory, is_file):
        relative_path = full_path[len(directory) :].lstrip("/")
        return relative_path if is_file else relative_path + "/"
