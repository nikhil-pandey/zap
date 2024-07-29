from dataclasses import dataclass
from typing import List, Dict


@dataclass
class AgentOutput:
    content: str
    message_history: List[Dict[str, str]]
