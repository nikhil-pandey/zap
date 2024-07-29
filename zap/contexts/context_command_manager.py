from rich.table import Table

from zap.agent_manager import AgentManager
from zap.constants import FILE_ICONS
from zap.contexts.context_manager import ContextManager
from zap.cliux import UIInterface


class ContextCommandManager:
    def __init__(self, context_manager: ContextManager, ui: UIInterface, agent_manager: AgentManager):
        self.context_manager: ContextManager = context_manager
        self.ui: UIInterface = ui
        self.agent_manager: AgentManager = agent_manager

    async def switch_context(self, name: str):
        if name not in self.context_manager.contexts:
            self.context_manager.create_context(name)
        self.context_manager.switch_context(name)
        self.ui.print(f"Switched to context: {name}")

    async def switch_agent(self, agent_name: str):
        if agent_name not in self.agent_manager.agents:
            self.ui.warning(f"Agent not found: {agent_name}")
            return
        context = self.context_manager.get_current_context()
        self.context_manager.switch_agent(context.name, agent_name)
        self.ui.print(f"Switched to agent: {agent_name}")

    async def list_contexts(self):
        contexts = self.context_manager.list_contexts()
        self.ui.table(
            "Contexts",
            ["Context", "Agent", "Messages Count", "Last message"],
            [
                [context.name, context.current_agent, str(len(context.messages)), context.messages[-1].content if context.messages else ""]
                for context in self.context_manager.contexts.values()
            ]
        )

    async def show_current_context(self):
        context = self.context_manager.get_current_context()
        self.ui.print(f"Current context: {context.name}")
        self.ui.print(f"Current agent: {context.current_agent}")
        self.ui.data_view([m.to_agent_output() for m in context.messages], methods=False, title="Messages")

    async def save_context(self):
        current_context = self.context_manager.get_current_context()
        self.context_manager.save_context(current_context.name)
        self.ui.print(f"Saved current context: {current_context.name}")

    async def load_all_contexts(self):
        self.context_manager.load_all_contexts()
        self.ui.print("Loaded all saved contexts.")
        item = next(iter(self.context_manager.contexts.keys()))
        self.context_manager.switch_context(item)

    async def load_context(self, context_name: str):
        loaded_context = self.context_manager.load_context(context_name)
        if loaded_context:
            self.context_manager.switch_context(context_name)
            self.ui.print(f"Loaded and switched to context: {context_name}")
        else:
            self.ui.print(f"No saved context found with name: {context_name}")

    async def list_saved_contexts(self):
        saved_contexts = self.context_manager.list_saved_contexts()
        if saved_contexts:
            self.ui.print("Saved contexts:")
            for context in saved_contexts:
                self.ui.print(f"- {context}")
        else:
            self.ui.print("No saved contexts found.")

    async def list_agents(self):
        agents = self.agent_manager.list_agents()
        self.ui.print("Available agents:")
        for agent in agents:
            self.ui.print(f"- {agent}")

    async def delete_context(self, name: str):
        if self.context_manager.delete_context(name):
            self.ui.print(f"Deleted context: {name}")
        else:
            self.ui.error(f"Context not found: {name}")

    async def rename_context(self, old_name: str, new_name: str):
        if self.context_manager.rename_context(old_name, new_name):
            self.ui.print(f"Renamed context '{old_name}' to '{new_name}'")
        else:
            self.ui.error(f"Failed to rename context. Make sure the old name exists and the new name is not taken.")

    async def clear_context(self, name: str = None):
        if name is None:
            name = self.context_manager.get_current_context().name
        if self.context_manager.clear_context(name):
            self.ui.print(f"Cleared messages in context: {name}")
        else:
            self.ui.error(f"Failed to clear context: {name}")

    async def archive_all_contexts(self, archive_name: str):
        if self.context_manager.archive_all_contexts(archive_name):
            self.ui.print("All contexts have been archived and cleared.")
        else:
            self.ui.error("Archive with the same name already exists. Please choose a different name.")
            await self.list_archived_contexts()

    async def list_archived_contexts(self):
        archived_contexts = self.context_manager.list_archived_contexts()
        if archived_contexts:
            self.ui.print("Archived contexts:")
            for context in archived_contexts:
                self.ui.print(f"- {context}")
        else:
            self.ui.info("No archived contexts found.")

    async def load_archived_context(self, archive_name: str):
        loaded_context = self.context_manager.load_archived_contexts(archive_name)
        if loaded_context:
            item = next(iter(self.context_manager.contexts.keys()))
            self.context_manager.switch_context(item)
            self.ui.print(f"Loaded archived context and switched to: {item}")
        else:
            self.ui.error(f"No archived context found with name: {archive_name}")
            await self.list_archived_contexts()
