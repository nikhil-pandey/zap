from abc import ABC, abstractmethod
from typing import Any


class UIInterface(ABC):
    @abstractmethod
    def print(self, *args, **kwargs):
        pass

    @abstractmethod
    def debug(self, message: str):
        pass

    @abstractmethod
    def info(self, message: str):
        pass

    @abstractmethod
    def warning(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str):
        pass

    @abstractmethod
    def exception(self, e: Exception, message: str):
        pass

    @abstractmethod
    def panel(self, content: str, title: str = "") -> None:
        pass

    @abstractmethod
    def table(self, title: str, columns: list, rows: list) -> None:
        pass

    @abstractmethod
    def display_table(self, title: str | None, data: list[dict[str, Any]]) -> None:
        pass

    @abstractmethod
    def spinner(self, message: str):
        pass

    @abstractmethod
    def progress(self, total: int) -> Any:
        pass

    @abstractmethod
    def data_view(self, data: Any, methods: bool = True, title: str | None = None):
        pass

    @abstractmethod
    def syntax_highlight(
        self, code: str, language: str = "python", line_numbers: bool = True
    ):
        pass

    @abstractmethod
    def tree(self, paths: list[str]):
        pass

    @abstractmethod
    def live_output(self, content: any):
        pass

    @abstractmethod
    def markdown(self, md_string: str):
        pass

    @abstractmethod
    async def log_input(self, input_str: str):
        pass

    @abstractmethod
    def export_html(self, filename: str):
        pass

    @abstractmethod
    def export_svg(self, filename: str):
        pass

    @abstractmethod
    def export_text(self, filename: str):
        pass

    @abstractmethod
    async def export_async(self, filename: str, fmt: str = "text"):
        pass
