from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AgentConfig:
    name: str
    type: str
    system_prompt: str
    user_prompt: Optional[str] = None
    tools: List[str] = field(default_factory=list)
    model: str = "gpt-4"
    provider: str = "azure"
