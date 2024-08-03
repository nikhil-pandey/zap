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
                search_block, replace_block = await extract_search_replace_blocks(block)
                await self.create_or_update_file(filename, search_block, replace_block)
        return output

    async def create_or_update_file(self, filename, search_block, replace_block):
        await self.tool_manager.get_tool('replace_block').execute(
            filename=filename,
            search_block=search_block,
            replace_block=replace_block
        )
        LOGGER.info(f'Updated file {filename}')
