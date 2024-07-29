import inspect
from typing import get_type_hints, Annotated

from zap.tools.tool import Tool


class ToolManager:
    def __init__(self):
        self.tools = {}

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        return self.tools.get(name)

    def get_function_schema(self, name: str) -> dict:
        tool = self.get_tool(name)
        if not tool:
            return {}

        schema = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }

        execute_method = tool.execute
        signature = inspect.signature(execute_method)
        type_hints = get_type_hints(execute_method, include_extras=True)

        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue

            param_schema = {"type": "string"}  # Default to string if no annotation

            if param_name in type_hints:
                annotation = type_hints[param_name]
                if isinstance(annotation, type(Annotated)):
                    param_schema["description"] = annotation.__metadata__[0]

            if param.default == inspect.Parameter.empty:
                schema["function"]["parameters"]["required"].append(param_name)

            schema["function"]["parameters"]["properties"][param_name] = param_schema

        # If there are no parameters, set it to an empty dict
        if not schema["function"]["parameters"]["properties"]:
            schema["function"]["parameters"] = {}

        return schema
