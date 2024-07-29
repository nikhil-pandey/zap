from zap.agents.chat_message import ChatMessage

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Context:
    name: str
    current_agent: str = "chat"
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    filename: Optional[str] = None

    def add_message(self, message: ChatMessage):
        self.messages.append(message)
        self.last_accessed = datetime.now()

    def get_last_message(self) -> Optional[ChatMessage]:
        return self.messages[-1] if self.messages else None

    def to_dict(self):
        return {
            "name": self.name,
            "current_agent": self.current_agent,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "filename": self.filename
        }

    @classmethod
    def from_dict(cls, data):
        context = cls(
            name=data["name"],
            current_agent=data["current_agent"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            filename=data.get("filename")
        )
        context.messages = [ChatMessage.from_dict(msg) for msg in data["messages"]]
        return context
