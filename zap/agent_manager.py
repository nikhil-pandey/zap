import yaml
from pathlib import Path
from typing import Dict

from zap.agents import *
from zap.tools.tool_manager import ToolManager


class AgentManager:
    def __init__(
        self,
        config_dir: Path,
        tool_manager: ToolManager,
        ui: UIInterface,
        engine: ZapTemplateEngine,
    ):
        self.tool_manager = tool_manager
        self.ui = ui
        self.engine = engine
        self.agents: Dict[str, Agent] = {}
        self.load_agents(config_dir)

    def load_agents(self, config_dir: Path):
        for config_file in config_dir.glob("*.yaml"):
            with open(config_file, "r") as f:
                config_dict = yaml.safe_load(f)
                config = AgentConfig(**config_dict)
                agent_class = globals()[config.type]
                agent = agent_class(
                    config,
                    tool_manager=self.tool_manager,
                    ui=self.ui,
                    engine=self.engine,
                )
                self.agents[config.name] = agent

    def get_agent(self, name: str) -> Agent:
        return self.agents.get(name)

    def list_agents(self) -> list[str]:
        return list(self.agents.keys())
