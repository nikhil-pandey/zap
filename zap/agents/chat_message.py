from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class ChatMessage:
    role: str
    content: str
    agent: str
    timestamp: datetime = datetime.now()
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "agent": self.agent,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data):
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

    def to_agent_output(self):
        output = {
            "role": self.role,
            "content": self.content,
        }

        if self.metadata and 'tool_calls' in self.metadata:
            output['tool_calls'] = self.metadata['tool_calls']
        if self.metadata and 'tool_responses' in self.metadata:
            output['tool_responses'] = self.metadata['tool_responses']
        return output

    @classmethod
    def from_agent_output(cls, data, agent_name):
        metadata = {}
        if 'tool_calls' in data:
            metadata['tool_calls'] = data['tool_calls']
        if 'tool_responses' in data:
            metadata['tool_responses'] = data['tool_responses']
        return cls(
            role=data['role'],
            content=data['content'],
            agent=agent_name,
            metadata=metadata,
        )
