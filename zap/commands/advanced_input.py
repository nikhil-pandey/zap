import heapq
import os
from typing import Iterable
from fuzzywuzzy import fuzz
from prompt_toolkit.completion import Completion, Completer
from prompt_toolkit.document import Document
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import ThreadedCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
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


class AdvancedInput:
    def __init__(self, registry, state, ui):
        self.history = InMemoryHistory()
        self.completer = ThreadedCompleter(AdvancedCompleter(registry, state, ui))
        self.kb = KeyBindings()
        self.registry = registry

        self.session = PromptSession(
            history=self.history,
            completer=self.completer,
            key_bindings=self.kb,
            complete_while_typing=True,
            complete_style=CompleteStyle.COLUMN,
            multiline=True,
        )
        # noinspection PyUnresolvedReferences
        self.completer.completer.set_session(self.session)

        self._setup_key_bindings()

    def _setup_key_bindings(self):
        @Condition
        def is_command():
            text = self.session.default_buffer.text.lstrip()
            items = text.split()
            return text.startswith("/") or (
                items
                and len(items) == 1
                and (len(text) < 10 or self.registry.is_command(items[0]))
            )

        @self.kb.add("enter", filter=is_command)
        def handle_command(event):
            event.current_buffer.validate_and_handle()

        @self.kb.add("enter", filter=~is_command)
        def insert_newline(event):
            event.current_buffer.newline()

        @self.kb.add("c-d")
        def exit_or_submit(event):
            if not event.current_buffer.text:
                event.app.exit()
            else:
                event.current_buffer.validate_and_handle()

    async def input_async(self, prompt: str = "> ") -> str:
        while True:
            user_input = await self.session.prompt_async(prompt, multiline=True)
            if not user_input:
                continue
            user_input = user_input.strip()
            if not user_input.startswith("/") and len(user_input.split()) == 1:
                maybe_command = "/" + user_input
                if self.registry.is_command(maybe_command):
                    return maybe_command
            return user_input
