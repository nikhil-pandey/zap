import dataclasses
import re
from typing import List, Set, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import ThreadedCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import InMemoryHistory, FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import CompleteStyle

from zap.app_state import AppState
from zap.cliux import UIInterface
from zap.commands.advanced_completer import AdvancedCompleter
from zap.commands.command_registry import CommandRegistry


@dataclasses.dataclass
class UserInput:
    message: str
    file_paths: Optional[List[str]]
    symbols: Optional[Set[str]]


class AdvancedInput:
    def __init__(
        self,
        registry: CommandRegistry,
        state: AppState,
        ui: UIInterface,
        filename_to_path: dict,
        symbol_filter: set):
        if state.config.command_history_file:
            self.history = FileHistory(state.config.command_history_file)
        else:
            self.history = InMemoryHistory()
        self.completer = ThreadedCompleter(AdvancedCompleter(registry, state, ui))
        self.kb = KeyBindings()
        self.registry = registry
        self.filename_to_path = filename_to_path
        self.symbol_filter = symbol_filter

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

    def extract_file_paths_and_symbols(self, text: str) -> (List[str], Set[str]):
        file_paths = []
        symbols = set()
        words = re.findall(r'\b\w+\b', text)

        for word in words:
            word_lower = word.lower()
            if word_lower in self.filename_to_path:
                file_paths.extend(self.filename_to_path[word])
            if word_lower in self.symbol_filter:
                symbols.add(word)

        return file_paths, symbols

    async def input_async(self, prompt: str = "> ") -> UserInput:
        while True:
            user_input = await self.session.prompt_async(prompt, multiline=True)
            if not user_input:
                continue
            user_input = user_input.strip()
            if not user_input.startswith("/") and len(user_input.split()) == 1:
                maybe_command = "/" + user_input
                if self.registry.is_command(maybe_command):
                    return UserInput(maybe_command)

            file_paths, symbols = self.extract_file_paths_and_symbols(user_input)
            return UserInput(user_input, file_paths, symbols)
