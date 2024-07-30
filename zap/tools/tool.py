import json
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable


def tool_executor(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return json.dumps({"status": "success", "result": result})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    return wrapper


class Tool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    @tool_executor
    async def execute(self, *args, **kwargs):
        pass
