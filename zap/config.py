import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml

from zap.cliux.config import Config as UIConfig
from zap.git_analyzer.config import GitAnalyzerConfig


@dataclass
class AppConfig:
    ui_config: UIConfig
    git_analyzer_config: GitAnalyzerConfig
    build_command: Optional[str] = None
    lint_command: Optional[str] = None
    test_command: Optional[str] = None
    dependency_manager: Optional[str] = None
    templates_dir: Optional[str] = None
    verbose: bool = False
    agent: str = "chat"
    auto_persist_contexts: bool = True
    auto_archive_contexts: bool = True
    auto_load_contexts: bool = True


def load_config(config_paths: List[Path], args) -> AppConfig:
    # Load config from files
    config = {}
    for path in config_paths:
        if path.exists():
            with open(path, "r") as f:
                config.update(yaml.safe_load(f))

    git_analyzer_config = GitAnalyzerConfig.from_dict(
        config.get("git_analyzer_config", dataclasses.asdict(GitAnalyzerConfig()))
    )

    ui_config = UIConfig.from_dict(config.get("ui_config", dataclasses.asdict(UIConfig())))

    config.pop("git_analyzer_config", None)
    config.pop("ui_config", None)
    config['verbose'] = args.verbose or config.get("verbose", False)
    ui_config.verbose = args.verbose or ui_config.verbose
    config['agent'] = args.agent or config.get("agent", "chat")
    config['templates_dir'] = args.templates_dir or config.get("templates_dir",
                                                               str(Path(__file__).parent / "templates"))
    return AppConfig(
        ui_config=ui_config,
        git_analyzer_config=git_analyzer_config,
        **config,
    )
