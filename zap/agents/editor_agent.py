import json
import os

from zap.agents.chat_agent import CodeAgent
from zap.agents.agent_output import AgentOutput
from zap.contexts.context import Context
from zap.utils import extract_xml_blocks, extract_search_replace_blocks
from zap.logger import LOGGER


class EditorAgent(CodeAgent):
    async def process(
        self, message: str, context: Context, template_context: dict
    ) -> AgentOutput:
        output: AgentOutput = await super().process(message, context, template_context)
        for message in output.message_history:
            if message['role'] != 'assistant':
                continue

            actions = await extract_xml_blocks('action', message['content'])
            for block, attributes in actions:
                filename = attributes.get('filename')
                if not filename:
                    LOGGER.warning('No filename attribute found in action block')
                    continue
                could_be_blocks = await extract_search_replace_blocks(block)
                for search_block, replace_block in could_be_blocks:
                    await self.create_or_update_file(filename, search_block, replace_block)
        return output

    async def create_or_update_file(self, filename, search_block, replace_block):
        await self.tool_manager.get_tool('replace_block').execute(
            filename=filename,
            search_block=search_block,
            replace_block=replace_block
        )
        LOGGER.info(f'Updated file {filename}')

    async def get_examples(self) -> list[dict]:
        examples_files = os.path.join(os.path.dirname(self.config.system_prompt), 'examples.json')
        examples_file_content = await self.engine.render_file(examples_files)
        examples = json.loads(examples_file_content)
        return list(item for sublist in examples for item in sublist)
