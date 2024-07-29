import json
from abc import ABC

from litellm import acompletion

from zap.agents.agent_output import AgentOutput
from zap.cliux import UIInterface
from zap.contexts.context import Context
from zap.agents.model_capabilities import ModelCapabilities
from zap.agents.agent_config import AgentConfig
from zap.exceptions import ToolExecutionError
from zap.templating import ZapTemplateEngine
from zap.tools.tool_manager import ToolManager


class Agent(ABC):
    def __init__(self, config: AgentConfig, tool_manager: ToolManager, ui: UIInterface, engine: ZapTemplateEngine):
        self.tool_manager = tool_manager
        self.ui = ui
        self.config = config
        self.engine = engine
        self.supports_tool_calling = ModelCapabilities.supports_function_calling(
            config.provider, config.model) and config.tools
        self.supports_parallel_tool_calls = ModelCapabilities.supports_parallel_function_calling(
            config.provider, config.model) and config.tools

    async def process(self, message: str, context: Context) -> AgentOutput:
        messages = []
        for msg in context.messages:
            messages.append(msg.to_agent_output())
        original_message_count = len(messages)

        if not messages:
            # TODO: Figure out a way to get context
            system_prompt = await self.engine.render_file(self.config.system_prompt, {})
            messages.append({"role": "system", "content": system_prompt})

            if self.config.user_prompt:
                user_prompt = await self.engine.render_file(self.config.user_prompt, {
                    'message': message
                })
                messages.append({"role": "user", "content": user_prompt})
            else:
                messages.append({"role": "user", "content": message})
        else:
            messages.append({"role": "user", "content": message})

        running = True
        round = 1
        while running:
            response = await acompletion(
                model=self.config.model,
                messages=messages,
                tools=self.config.tools if self.supports_tool_calling else None,
                tool_choice="auto" if self.supports_tool_calling else None,
                parallel_tool_calls=self.supports_parallel_tool_calls if self.supports_tool_calling else None,
            )

            response_message = response.choices[0].message
            content = response_message["content"]
            tool_calls = response_message.tool_calls

            if tool_calls is None or len(tool_calls) == 0:
                messages.append({"role": "assistant", "content": content})
                return AgentOutput(content=content, message_history=messages[original_message_count:])

            tool_responses = await self.handle_tool_calls(round, tool_calls)
            round += 1
            messages.extend(tool_responses)

    async def handle_tool_calls(self, round: int, tool_calls: any) -> list[dict[str, any]]:
        tool_responses = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args_str = tool_call.function.arguments
            try:
                tool = self.tool_manager.get_tool(function_name)
                function_args = json.loads(function_args_str)
                response = await tool.execute(round=round, **function_args)
            except json.JSONDecodeError as e:
                self.ui.exception(
                    e,
                    f"Failed to decode JSON arguments for tool call: {function_args_str}"
                )
                response = json.dumps({"error": "Failed to decode JSON arguments"})
            except ToolExecutionError as e:
                self.ui.exception(
                    e,
                    f"Failed to execute tool {function_name} with args {function_args_str}"
                )
                response = json.dumps({"error": "Failed to execute tool"})

            tool_responses.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": response,
                }
            )

        return tool_responses


class ChatAgent(Agent):
    pass


class CodeAgent(Agent):
    pass
