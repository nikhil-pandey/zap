import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import toml
import yaml


@dataclass
class GitAnalyzerConfig:
    commit_limit: Optional[int] = 10
    most_changed_files_limit: Optional[int] = 10
    least_changed_files_limit: Optional[int] = 10
    log_level: Optional[str] = "INFO"
    explore: Optional[bool] = True
    allowlisted_paths: Optional[list[str]] = None

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "GitAnalyzerConfig":
        return cls(
            commit_limit=config_dict.get("commit_limit", 10),
            most_changed_files_limit=config_dict.get("most_changed_files_limit", 10),
            least_changed_files_limit=config_dict.get("least_changed_files_limit", 10),
            log_level=config_dict.get("log_level", "INFO"),
            explore=config_dict.get("explore", True),
            allowlisted_paths=config_dict.get("allowlisted_paths", None),
        )

    @classmethod
    def from_file(cls, file_path: str) -> "GitAnalyzerConfig":
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
