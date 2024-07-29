import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Union, Any

import aiofiles
from rich import inspect
from rich.console import Console
from rich.live import Live
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.theme import Theme
from rich.tree import Tree

from .config import Config
from .ui_interface import UIInterface


class UI(UIInterface):
    KNOWN_THEMES = {
        "monokai": {
            "default": "cyan",
            "dim": "dim cyan",
            "emphasis": "bold cyan",
            "heading": "bold magenta",
            "link": "bright_blue",
            "prompt": "cyan",
            "error": "red",
        },
        # Add more predefined themes here
    }

    def __init__(self, config: Union[dict[str, Any], str, Config]):
        """
        Initialize the UI with the given configuration.

        :param config: Configuration dictionary, file path, or Config instance.
        """
        if isinstance(config, Config):
            self.config = config
        elif isinstance(config, dict):
            self.config = Config.from_dict(config)
        elif isinstance(config, str):
            self.config = Config.from_file(config)
        else:
            raise ValueError(
                "Config must be a dictionary, a file path, or a Config instance"
            )

        # Create a Theme object if a known theme name is provided, otherwise use None
        if self.config.theme in self.KNOWN_THEMES:
            theme = Theme(self.KNOWN_THEMES[self.config.theme])
        elif self.config.theme != "default":
            print(f"Warning: Unknown theme '{self.config.theme}'. Using default theme.")
            theme = None
        else:
            theme = None

        self.console = Console(
            record=True, theme=theme, color_system="truecolor", force_terminal=True
        )
        self.logger = self._setup_logger()
        self.history_file = self.config.history_file
        self._running = False

    def _setup_logger(self, name: str = __name__, level: int = logging.DEBUG):
        """
        Set up the logger with RichHandler.

        :param name: Logger name.
        :param level: Logging level.
        :return: Configured logger.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level if self.config.verbose else logging.INFO)
        handler = RichHandler(rich_tracebacks=True, show_time=False)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        return logger

    def input_async(self, prompt: str) -> str:
        """
        Get user input asynchronously.

        :param prompt: Prompt to display.
        :return: User input string.
        """
        return self.console.input(prompt)

    def raw(self, obj: any):
        """
        Print the raw object.

        :param obj: Object to print.
        """
        self.console.print(obj)

    def print(self, *args, **kwargs):
        """
        Print to the console.

        :param args: Arguments to print.
        :param kwargs: Keyword arguments for printing.
        """
        self.logger.info(*args, **kwargs)

    def debug(self, message: str):
        """
        Print a debug message to the console.

        :param message: Debug message.
        """
        if self.config.verbose:
            self.logger.debug(message)

    def info(self, message: str):
        """
        Print an info message to the console.

        :param message: Info message.
        """
        self.logger.info(message)

    def warning(self, message: str):
        """
        Print a warning message to the console.

        :param message: Warning message.
        """
        self.logger.warning(message)

    def error(self, message: str):
        """
        Print an error message to the console.

        :param message: Error message.
        """
        self.logger.error(message)

    def exception(self, e: Exception, message: str):
        """
        Print an exception message to the console.

        :param e: Exception instance.
        :param message: Exception message.
        """
        if self.config.verbose:
            self.console.print_exception(show_locals=True)
        self.logger.exception(f"{message}: {str(e)}")

    def panel(self, content: str, title: str = "") -> None:
        """
        Display a panel with the given content and title.

        :param content: Content to display in the panel.
        :param title: Title of the panel.
        """
        self.console.print(
            Panel(content, title=title, border_style=self.config.panel_border_style)
        )

    def table(self, title: str, columns: list, rows: list) -> None:
        """
        Display a table with the given title, columns, and rows.

        :param title: Title of the table.
        :param columns: List of column names.
        :param rows: List of rows, where each row is a list of values.
        """
        table = Table(
            title=title, show_header=True, header_style=self.config.table_header_style
        )
        for column in columns:
            table.add_column(column)
        for row in rows:
            table.add_row(*row)
        self.console.print(table)

    def display_table(self, title: str | None, data: list[dict[str, Any]]) -> None:
        """
        Display a table with the given title and data.

        :param title: Title of the table.
        :param data: List of dictionaries representing the table data.
        """
        if not data:
            return
        table = Table(
            title=title, show_header=True, header_style=self.config.table_header_style
        )
        columns = list(data[0].keys())
        for column in columns:
            table.add_column(column)
        for row in data:
            table.add_row(*[str(row[col]) for col in columns])
        self.console.print(table)

    @contextmanager
    def spinner(self, message: str):
        """
        Display a spinner with the given message.

        :param message: Message to display with the spinner.
        """
        with self.console.status(message, spinner=self.config.spinner_type) as status:
            yield status

    def progress(self, total: int) -> Progress:
        """
        Display a progress bar.

        :param total: Total number of steps.
        :return: Progress instance.
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        return progress

    def data_view(self, data: Any, methods: bool = True, title: str | None = None):
        """
        Display a detailed view of the given data.

        :param data: Data to inspect.
        :param methods: Whether to include methods in the inspection.
        :param title: Title of the data view.
        """
        inspect(data, methods=methods, title=title)

    def syntax_highlight(
            self, code: str, language: str = "python", line_numbers: bool = True
    ):
        """
        Display syntax-highlighted code.

        :param code: Code to highlight.
        :param language: Programming language of the code.
        :param line_numbers: Whether to display line numbers.
        """
        self.console.print(
            Syntax(
                code,
                language,
                theme=self.config.syntax_theme,
                line_numbers=line_numbers,
            )
        )

    def tree(self, paths: list[str]):
        """
        Display a tree view of the given paths.

        :param paths: List of paths to display.
        """
        tree = Tree("Files")
        for path in paths:
            tree.add(path)
        self.console.print(tree)

    def live_output(self, content: any):
        """
        Display live output.

        :param content: Content to display.
        :return: Live instance.
        """
        return Live(
            content, console=self.console, refresh_per_second=self.config.live_refresh_per_second
        )

    def markdown(self, md_string: str):
        """
        Display markdown content.

        :param md_string: Markdown string to display.
        """
        md = Markdown(md_string)
        self.console.print(md)

    async def log_input(self, input_str: str):
        """
        Log user input to the history file.

        :param input_str: User input string.
        """
        timestamp = datetime.now().isoformat()
        async with aiofiles.open(self.history_file, mode="a") as f:
            await f.write(f"{timestamp}: {input_str}\n")

    def export_html(self, filename: str):
        """
        Export console output to an HTML file.

        :param filename: Name of the HTML file.
        """
        self.console.save_html(filename)

    def export_svg(self, filename: str):
        """
        Export console output to an SVG file.

        :param filename: Name of the SVG file.
        """
        self.console.save_svg(filename)

    def export_text(self, filename: str):
        """
        Export console output to a text file.

        :param filename: Name of the text file.
        """
        text = self.console.export_text()
        with open(filename, "w") as f:
            f.write(text)

    async def export_async(self, filename: str, fmt: str = "text"):
        """
        Export console output asynchronously.

        :param filename: Name of the file.
        :param fmt: Format of the file (text, html, svg).
        """
        if fmt == "html":
            self.export_html(filename)
        elif fmt == "svg":
            self.export_svg(filename)
        else:
            self.export_text(filename)
