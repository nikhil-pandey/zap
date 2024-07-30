from zap.agents.agent_output import AgentOutput
from zap.agents.base import ChatAgent
from zap.contexts.context import Context


class EchoAgent(ChatAgent):
    async def process(
        self, message: str, context: Context, template_context: dict
    ) -> AgentOutput:
        echo_message = f"I heard you say: {message}"
        message_history = [
            {"role": "user", "content": message},
            {"role": "assistant", "content": echo_message},
        ]
        return AgentOutput(content=echo_message, message_history=message_history)
