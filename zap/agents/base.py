import json
from abc import ABC
from typing import List, Dict, Any, Tuple

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
        self.config = config
        self.tool_manager = tool_manager
        self.ui = ui
        self.engine = engine
        self.tool_schemas = self._load_tool_schemas()
        self.supports_tool_calling = True
        self.supports_parallel_tool_calls = True

    def _load_tool_schemas(self) -> List[Dict[str, Any]]:
        tool_schemas = []
        if self.config.tools:
            for tool in self.config.tools:
                tool_schema = self.tool_manager.get_function_schema(tool)
                if tool_schema:
                    tool_schemas.append(tool_schema)
                else:
                    raise ValueError(
                        f"Tool {tool} not found in tool manager. Found: {self.tool_manager.tools.keys()}"
                    )
            self.ui.info(f"Loaded {len(tool_schemas)} tool schemas")
        return tool_schemas

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
        messages = await self._prepare_messages(message, context, template_context)
        original_message_count = len(messages)

        self.ui.debug(f"You: {escape(message) if message else ''}")

        round = 1
        while True:
            try:
                response = await self._get_model_response(messages)
                content, tool_calls = self._process_response(response)

                if not tool_calls:
                    return self._create_agent_output(content, messages, original_message_count)

                messages.append(self._create_assistant_message(content, tool_calls))
                tool_responses = await self.handle_tool_calls(round, tool_calls)
                messages.extend(tool_responses)
                round += 1

            except RateLimitError as e:
                self.ui.warning(f"Rate limit reached. Retrying in a moment...")
                raise
            except BadRequestError as e:
                self.ui.exception(
                    e, f"Bad request error while processing message: {message}"
                )
                raise

    async def _prepare_messages(self, message: str, context: Context, template_context: dict) -> List[Dict[str, Any]]:
        messages = [msg.to_agent_output() for msg in context.messages]

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

        return messages

    async def _get_model_response(self, messages: List[Dict[str, Any]]):
        with self.ui.spinner(f"Thinking..."):
            return await acompletion(
                model=self.config.model,
                messages=messages,
                tools=self.tool_schemas if self.supports_tool_calling and self.tool_schemas else None,
                tool_choice="auto" if self.supports_tool_calling and self.tool_schemas else None,
                parallel_tool_calls=self.supports_parallel_tool_calls if self.supports_tool_calling and self.tool_schemas else None,
                top_p=1.0,
                temperature=1.0,
            )

    def _process_response(self, response):
        response_message = response.choices[0].message
        content = response_message["content"]
        tool_calls = response_message.tool_calls

        self.ui.print(
            f"{self.config.type}[{self.config.name}]: {escape(content) if content else ''}"
        )

        return content, tool_calls

    def _create_agent_output(self, content: str, messages: List[Dict[str, Any]],
                             original_message_count: int) -> AgentOutput:
        messages.append({"role": "assistant", "content": content})
        return AgentOutput(
            content=content,
            message_history=messages[original_message_count:],
        )

    def _create_assistant_message(self, content: str, tool_calls: List[Any]) -> Dict[str, Any]:
        return {
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

    async def handle_tool_calls(
            self, round: int, tool_calls: List[Any]
    ) -> List[Dict[str, Any]]:
        tool_responses = []
        valid_tool_calls = self._validate_tool_calls(tool_calls, tool_responses)

        for tool, function_name, function_args, tool_call in valid_tool_calls:
            response = await self._execute_tool_call(round, tool, function_name, function_args)
            tool_responses.append(self._create_tool_response(tool_call, function_name, response))

        return tool_responses

    def _validate_tool_calls(self, tool_calls: List[Any], tool_responses: List[Dict[str, Any]]) -> List[
        Tuple[Any, str, Dict[str, Any], Any]]:
        valid_tool_calls = []
        edit_tool_calls = []

        for tool_call in tool_calls:
            try:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                tool = self.tool_manager.get_tool(function_name)

                if isinstance(tool, EditFileTool):
                    edit_tool_calls.append((tool, function_name, function_args, tool_call))
                else:
                    valid_tool_calls.append((tool, function_name, function_args, tool_call))
            except Exception as e:
                tool_responses.append(self._create_invalid_tool_response(tool_call, e))

        edit_tool_calls.sort(key=lambda x: x[2]["start_line"], reverse=True)
        valid_tool_calls.extend(edit_tool_calls)
        return valid_tool_calls

    async def _execute_tool_call(self, round: int, tool: Any, function_name: str, function_args: Dict[str, Any]) -> str:
        self.ui.debug(f"Round {round}: Calling tool {function_name} with args {json.dumps(function_args)}")
        response = await self.handle_tool_call(tool, function_args)
        self.ui.debug(f"Tool {function_name} response: {response}")
        return response

    def _create_tool_response(self, tool_call: Any, function_name: str, response: str) -> Dict[str, Any]:
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": response,
        }

    def _create_invalid_tool_response(self, tool_call: Any, error: Exception) -> Dict[str, Any]:
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_call.function.name,
            "content": f"Invalid tool call {tool_call.function.name}: {error}",
        }

    @tool_executor
    async def handle_tool_call(self, tool, function_args):
        return await tool.execute(**function_args)
