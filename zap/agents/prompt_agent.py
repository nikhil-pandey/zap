import re

from litellm import acompletion

from zap.agents.chat_agent import ChatAgent
from zap.agents.agent_output import AgentOutput
from zap.contexts.context import Context
from zap.utils import get_lite_llm_model


class PromptAgent(ChatAgent):
    async def process(
        self, message: str, context: Context, template_context: dict
    ) -> AgentOutput:
        # TODO: This is probably going to be duplicate across agents, neet to refactor this
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

        response = await acompletion(
            model=await get_lite_llm_model(self.config.provider, self.config.model),
            messages=messages,
        )

        response_message = response.choices[0].message
        content = response_message["content"]
        content = re.search(r"<prompt>(.*?)</prompt>", content, re.DOTALL).group(1)
        messages.append({"role": "assistant", "content": content})

        return AgentOutput(
            content=content,
            message_history=messages[original_message_count:],
        )
