import json
from dataclasses import dataclass
from typing import Any, Optional

import toml
import yaml


@dataclass
class Config:
    theme: Optional[str] = "default"
    """
    The theme for the UI. Default is "default".
    """
    history_file: Optional[str] = "command_history.log"
    """
    The file where command history will be logged. Default is "command_history.log".
    """
    panel_border_style: Optional[str] = "bold"
    """
    The border style for panels. Default is "bold".
    """
    table_header_style: Optional[str] = "bold magenta"
    """
    The header style for tables. Default is "bold magenta".
    """
    spinner_type: Optional[str] = "dots"
    """
    The type of spinner to use. Default is "dots".
    """
    live_refresh_per_second: Optional[int] = 4
    """
    The refresh rate for live output, in frames per second. Default is 4.
    """
    syntax_theme: Optional[str] = "monokai"
    """
    The theme for syntax highlighting. Default is "monokai".
    """
    verbose: bool = False
    """
    Whether to enable verbose logging. Default is False.
    """

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "Config":
        """
        Create a Config instance from a dictionary.

        :param config_dict: Dictionary containing configuration settings.
        :return: Config instance.
        """
        return cls(
            theme=config_dict.get("theme", "default"),
            history_file=config_dict.get("history_file", "command_history.log"),
            panel_border_style=config_dict.get("panel_border_style", "bold"),
            table_header_style=config_dict.get("table_header_style", "bold magenta"),
            spinner_type=config_dict.get("spinner_type", "dots"),
            live_refresh_per_second=config_dict.get("live_refresh_per_second", 4),
            syntax_theme=config_dict.get("syntax_theme", "monokai"),
            verbose=config_dict.get("verbose", False),
        )

    @classmethod
    def from_file(cls, file_path: str) -> "Config":
        """
        Create a Config instance from a file.

        :param file_path: Path to the configuration file (JSON, YAML, or TOML).
        :return: Config instance.
        """
        if file_path.endswith(".json"):
            with open(file_path, "r") as f:
                return cls.from_dict(json.load(f))
        elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
            with open(file_path, "r") as f:
                return cls.from_dict(yaml.safe_load(f))
        elif file_path.endswith(".toml"):
            with open(file_path, "r") as f:
                return cls.from_dict(toml.load(f))
        else:
            raise ValueError("Unsupported file format. Use JSON, YAML, or TOML.")
