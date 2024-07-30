import json
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable


def tool_executor(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return json.dumps({"result": result})
        except json.JSONDecodeError as e:
            return json.dumps({"error": "Failed to decode JSON arguments"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    return wrapper


class Tool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, *args, **kwargs):
        pass
