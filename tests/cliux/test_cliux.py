import asyncio
import logging
from unittest.mock import patch

import pytest
from rich.console import Console
from rich.live import Live
from rich.progress import Progress
from rich.syntax import Syntax
from rich.text import Text

from zap.cliux import Config, UI


# Config Tests

def test_config_default_values():
    config = Config()
    assert config.theme == "default"
    assert config.history_file == "command_history.log"
    assert config.panel_border_style == "bold"
    assert config.table_header_style == "bold magenta"
    assert config.spinner_type == "dots"
    assert config.live_refresh_per_second == 4
    assert config.syntax_theme == "monokai"


def test_config_from_dict():
    config_dict = {
        "theme": "dark",
        "history_file": "test_history.log",
        "panel_border_style": "double",
        "table_header_style": "bold cyan",
        "spinner_type": "line",
        "live_refresh_per_second": 5,
        "syntax_theme": "solarized"
    }
    config = Config.from_dict(config_dict)
    assert config.theme == "dark"
    assert config.history_file == "test_history.log"
    assert config.panel_border_style == "double"
    assert config.table_header_style == "bold cyan"
    assert config.spinner_type == "line"
    assert config.live_refresh_per_second == 5
    assert config.syntax_theme == "solarized"


@pytest.mark.parametrize("file_extension", [".json", ".yaml", ".yml", ".toml"])
def test_config_from_file(file_extension, tmp_path):
    config_data = {
        "theme": "light",
        "history_file": "test_history.log",
    }
    file_path = tmp_path / f"config{file_extension}"

    if file_extension == ".json":
        import json
        with open(file_path, 'w') as f:
            json.dump(config_data, f)
    elif file_extension in (".yaml", ".yml"):
        import yaml
        with open(file_path, 'w') as f:
            yaml.dump(config_data, f)
    elif file_extension == ".toml":
        import toml
        with open(file_path, 'w') as f:
            toml.dump(config_data, f)

    config = Config.from_file(str(file_path))
    assert config.theme == "light"
    assert config.history_file == "test_history.log"


def test_config_from_file_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported file format"):
        Config.from_file("config.txt")


# UI Tests

@pytest.fixture
def ui():
    return UI({"theme": "default"})  # Using "default" theme


def test_ui_initialization(ui):
    assert isinstance(ui.config, Config)
    assert ui.config.theme == "default"
    assert isinstance(ui.console, Console)
    assert isinstance(ui.logger, logging.Logger)


def test_ui_custom_theme():
    custom_ui = UI({"theme": "monokai"})
    assert custom_ui.config.theme == "monokai"


def test_ui_unknown_theme(capsys):
    UI({"theme": "unknown_theme"})
    captured = capsys.readouterr()
    assert "Warning: Unknown theme 'unknown_theme'. Using default theme." in captured.out


@pytest.mark.parametrize("log_level", ["debug", "info", "warn", "error"])
def test_ui_logging(ui, log_level):
    with patch.object(ui.logger, log_level) as mock_log:
        getattr(ui, log_level)("Test log message")
        mock_log.assert_called_once_with("Test log message")


def test_ui_syntax_highlight(ui):
    with patch.object(ui.console, 'print') as mock_print:
        ui.syntax_highlight("print('Hello')", "python")
        mock_print.assert_called_once()
        # Check if the first argument of the first call is a Panel
        assert isinstance(mock_print.call_args[0][0], Syntax)


@pytest.mark.asyncio
async def test_background_export():
    ui = UI({"theme": "default"})
    ui.start_background_export()
    assert ui._background_task is not None

    # Simulate adding an export task
    await ui.export_async("test.txt", "text")

    # Allow some time for the background task to process the export
    await asyncio.sleep(0.1)

    # Stop the background export task
    await ui.stop_background_export()
    assert ui._background_task is None
    assert not ui._running


@pytest.mark.asyncio
async def test_ui_ask_async(ui):
    with patch.object(Input, 'text_async', return_value="Test Input"):
        result = await ui.ask_async("text", "Enter text:")
        assert result == "Test Input"


def test_ui_print(ui):
    with patch.object(ui.console, 'print') as mock_print:
        ui.print("Test message")
        mock_print.assert_called_once_with("Test message")


@pytest.mark.parametrize("log_level", ["debug", "info", "warning", "error"])
@pytest.mark.parametrize("verbose", [True, False])
def test_ui_logging(ui, log_level, verbose):
    ui.config.verbose = verbose
    with patch.object(ui.logger, log_level) as mock_log:
        with patch.object(ui.console, 'print') as mock_print:
            getattr(ui, log_level)("Test log message")

            if log_level in ["warning", "error"] or (verbose and log_level in ["debug", "info"]):
                mock_log.assert_called_once_with("Test log message")
                mock_print.assert_called_once()
            elif log_level == "info":
                mock_log.assert_called_once_with("Test log message")
                if not verbose:
                    mock_print.assert_not_called()
            else:  # debug and not verbose
                mock_log.assert_not_called()
                mock_print.assert_not_called()


def test_ui_exception(ui):
    with patch.object(ui.logger, 'exception') as mock_exception:
        ui.exception(ValueError("Test error"), "An error occurred")
        mock_exception.assert_called_once_with("An error occurred: Test error")


def test_ui_panel(ui):
    with patch.object(ui.console, 'print') as mock_print:
        ui.panel("Test content", "Test title")
        mock_print.assert_called_once()


def test_ui_table(ui):
    with patch.object(ui.console, 'print') as mock_print:
        ui.table("Test Table", ["Column 1", "Column 2"], [["Row 1 Col 1", "Row 1 Col 2"]])
        mock_print.assert_called_once()


def test_ui_display_table(ui):
    with patch.object(ui.console, 'print') as mock_print:
        ui.display_table("Test Table", [{"Name": "Alice", "Age": 30}])
        mock_print.assert_called_once()


def test_ui_spinner(ui):
    with patch.object(ui.console, 'status') as mock_status:
        with ui.spinner("Loading..."):
            pass
        mock_status.assert_called_once_with("Loading...", spinner=ui.config.spinner_type)


def test_ui_progress(ui):
    progress = ui.progress(100)
    assert isinstance(progress, Progress)


def test_ui_data_view(ui):
    with patch.object(ui.console, 'print') as mock_print:
        ui.data_view({"key": "value"})
        mock_print.assert_called_once()


def test_ui_tree(ui):
    with patch.object(ui.console, 'print') as mock_print:
        ui.tree(["/path/to/file1", "/path/to/file2"])
        mock_print.assert_called_once()


def test_ui_live_output(ui):
    live = ui.live_output(Text("Test"))
    assert isinstance(live, Live)


def test_ui_markdown(ui):
    with patch.object(ui.console, 'print') as mock_print:
        ui.markdown("# Heading")
        mock_print.assert_called_once()


@pytest.mark.asyncio
async def test_ui_log_input(ui, tmp_path):
    ui.history_file = tmp_path / "test_history.log"
    await ui.log_input("Test input")
    with open(ui.history_file, 'r') as f:
        content = f.read()
    assert "Test input" in content


@pytest.mark.parametrize("export_format", ["html", "svg", "text"])
def test_ui_export(ui, export_format, tmp_path):
    export_file = tmp_path / f"export.{export_format}"
    getattr(ui, f"export_{export_format}")(str(export_file))
    assert export_file.exists()


@pytest.mark.asyncio
async def test_ui_export_async(ui):
    with patch.object(ui.export_queue, 'put') as mock_put:
        await ui.export_async("test.html", "html")
        mock_put.assert_called_once_with(("test.html", "html"))
