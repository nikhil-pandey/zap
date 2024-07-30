import json
from abc import ABC

from litellm import acompletion, BadRequestError, RateLimitError
from rich.markup import escape
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from zap.agents.agent_config import AgentConfig
from zap.agents.agent_output import AgentOutput
from zap.cliux import UIInterface
from zap.contexts.context import Context
from zap.templating import ZapTemplateEngine
from zap.tools.basic_tools import EditFileTool
from zap.tools.tool import tool_executor
from zap.tools.tool_manager import ToolManager


class Agent(ABC):
    def __init__(
            self,
            config: AgentConfig,
            tool_manager: ToolManager,
            ui: UIInterface,
            engine: ZapTemplateEngine,
    ):
        self.tool_manager = tool_manager
        self.tool_schemas = []
        self.ui = ui
        if config.tools:
            for tool in config.tools:
                tool_schema = self.tool_manager.get_function_schema(tool)
                if tool_schema:
                    self.tool_schemas.append(tool_schema)
                else:
                    raise ValueError(
                        f"Tool {tool} not found in tool manager. Found: {self.tool_manager.tools.keys()}"
                    )
            self.ui.info(f"Loaded {len(self.tool_schemas)} tool schemas")
        self.config = config
        self.engine = engine
        self.supports_tool_calling = True
        self.supports_parallel_tool_calls = True

    async def process(
            self, message: str, context: Context, template_context: dict
    ) -> AgentOutput:
        try:
            return await self._try_process(message, context, template_context)
        except BadRequestError as e:
            self.ui.exception(
                e, f"Bad request error while processing message: {message}"
            )
            raise
        except Exception as ex:
            self.ui.exception(ex, f"Failed to process message: {message}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    async def _try_process(
            self, message: str, context: Context, template_context: dict
    ) -> AgentOutput:
        messages = []
        for msg in context.messages:
            messages.append(msg.to_agent_output())
        original_message_count = len(messages)

        if not messages:
            system_prompt = await self.engine.render_file(
                self.config.system_prompt, template_context
            )
            messages.append({"role": "system", "content": system_prompt})

            if self.config.user_prompt:
                user_prompt = await self.engine.render_file(
                    self.config.user_prompt, template_context
                )
                messages.append({"role": "user", "content": user_prompt})
            else:
                messages.append({"role": "user", "content": message})
        else:
            messages.append({"role": "user", "content": message})

        self.ui.debug(f"You: {escape(message) if message else ''}")

        running = True
        round = 1
        while running:
            try:
                with self.ui.spinner(f"Thinking..."):
                    response = await acompletion(
                        model=self.config.model,
                        messages=messages,
                        tools=(
                            self.tool_schemas
                            if self.supports_tool_calling and self.tool_schemas
                            else None
                        ),
                        tool_choice=(
                            "auto"
                            if self.supports_tool_calling and self.tool_schemas
                            else None
                        ),
                        parallel_tool_calls=(
                            self.supports_parallel_tool_calls
                            if self.supports_tool_calling
                            else None
                        ),
                    )

                response_message = response.choices[0].message
                content = response_message["content"]
                tool_calls = response_message.tool_calls
                self.ui.print(
                    f"{self.config.type}: {escape(content) if content else ''}"
                )

                if tool_calls is None or len(tool_calls) == 0:
                    messages.append({"role": "assistant", "content": content})
                    return AgentOutput(
                        content=content,
                        message_history=messages[original_message_count:],
                    )

                messages.append(
                    {
                        "role": "assistant",
                        "content": content,
                        "tool_calls": [
                            {
                                "id": tool.id,
                                "type": tool.type,
                                "function": {
                                    "name": tool.function.name,
                                    "arguments": tool.function.arguments,
                                },
                            }
                            for tool in tool_calls
                        ],
                    }
                )
                tool_responses = await self.handle_tool_calls(round, tool_calls)
                round += 1
                messages.extend(tool_responses)

            except RateLimitError as e:
                self.ui.warning(f"Rate limit reached. Retrying in a moment...")
                raise  # This will trigger the retry decorator
            except BadRequestError as e:
                self.ui.exception(
                    e, f"Bad request error while processing message: {message}"
                )
                raise

    async def handle_tool_calls(
            self, round: int, tool_calls: any
    ) -> list[dict[str, any]]:
        tool_responses = []

        # Do one pass and make sure we have valid tool calls
        valid_tool_calls = []
        edit_tool_calls = []
        for tool_call in tool_calls:
            try:
                function_name = tool_call.function.name
                function_args_str = tool_call.function.arguments
                function_args = json.loads(function_args_str)
                tool = self.tool_manager.get_tool(function_name)
                if isinstance(tool, EditFileTool):
                    edit_tool_calls.append(
                        (tool, function_name, function_args, tool_call)
                    )
                else:
                    valid_tool_calls.append(
                        (tool, function_name, function_args, tool_call)
                    )
            except Exception as e:
                tool_responses.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": f"Invalid tool call {tool_call.function.name}: {e}",
                    }
                )

        # order the edit tool calls in descending order ot start line
        edit_tool_calls.sort(key=lambda x: x[2]["start_line"], reverse=True)
        valid_tool_calls.extend(edit_tool_calls)

        for tool, function_name, function_args, tool_call in valid_tool_calls:
            self.ui.debug(
                f"Round {round}: Calling tool {function_name} with args {tool_call.function.arguments}"
            )
            response = await self.handle_tool_call(tool, function_args)
            self.ui.debug(f"Tool {function_name} response: {response}")
            tool_responses.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": response,
                }
            )
        return tool_responses

    @tool_executor
    async def handle_tool_call(self, tool, function_args):
        return await tool.execute(**function_args)
