import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from zap.agent_manager import AgentManager
from zap.contexts.context import Context


class ContextManager:
    def __init__(self, agent_manager: AgentManager, default_agent: str):
        self.default_agent = default_agent
        self.contexts: Dict[str, Context] = {
            "default": Context(name="default", current_agent=default_agent)
        }
        self.current_context: str = "default"
        self.agent_manager = agent_manager
        self.contexts_dir = Path.home() / ".zap" / "contexts"
        self.archived_contexts_dir = Path.home() / ".zap" / "archived_contexts"
        self.contexts_dir.mkdir(parents=True, exist_ok=True)
        self.archived_contexts_dir.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"context_{timestamp}.json"

    def save_context(self, context_name: str):
        context = self.contexts.get(context_name)
        if context and len(context.messages) > 0:
            if not context.filename:
                context.filename = self._generate_filename()
            file_path = self.contexts_dir / context.filename
            with open(file_path, "w") as f:
                json.dump(context.to_dict(), f)

    def load_all_contexts(self):
        count = 0
        for file in self.contexts_dir.glob("context_*.json"):
            count += 1
            with open(file, "r") as f:
                data = json.load(f)
                context = Context.from_dict(data)
                self.contexts[context.name] = context
        return count > 0

    def load_context(self, file_name: str) -> Optional[Context]:
        file_path = self.contexts_dir / file_name
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)
                context = Context.from_dict(data)
                self.contexts[context.name] = context
                return context
        return None

    def create_context(self, name: str) -> Context:
        if name not in self.contexts:
            self.contexts[name] = Context(name)
        return self.contexts[name]

    def switch_context(self, name: str):
        if name in self.contexts:
            self.current_context = name
            self.contexts[name].last_accessed = datetime.now()

    def get_current_context(self) -> Context:
        return self.contexts[self.current_context]

    def switch_agent(self, context_name: str, agent_name: str):
        if context_name in self.contexts and agent_name in self.agent_manager.agents:
            self.contexts[context_name].current_agent = agent_name

    def list_contexts(self) -> List[str]:
        return list(self.contexts.keys())

    def list_saved_contexts(self) -> List[tuple]:
        context_files = list(self.contexts_dir.glob("context_*.json"))
        context_info = []
        for file in context_files:
            with open(file, "r") as f:
                data = json.load(f)
                context_name = data.get("name", "Unknown")
                timestamp = datetime.strptime(file.stem[8:], "%Y%m%d_%H%M%S")
                context_info.append((context_name, timestamp, file.name))
        return sorted(context_info, key=lambda x: x[1], reverse=True)

    def delete_context(self, name: str) -> bool:
        if name in self.contexts:
            del self.contexts[name]
            if self.current_context == name:
                self.current_context = "default"
            return True
        return False

    def rename_context(self, old_name: str, new_name: str) -> bool:
        if old_name in self.contexts and new_name not in self.contexts:
            self.contexts[new_name] = self.contexts.pop(old_name)
            self.contexts[new_name].name = new_name
            if self.current_context == old_name:
                self.current_context = new_name
            return True
        return False

    def clear_context(self, name: str) -> bool:
        if name in self.contexts:
            self.contexts[name].messages.clear()
            return True
        return False

    def archive_all_contexts(self, archive_name: str):
        for context_name in self.contexts:
            context = self.contexts[context_name]
            if len(context.messages) > 0:
                self.save_context(context_name)

        archive_path = self.archived_contexts_dir / archive_name
        if archive_path.exists():
            return False

        files = list(self.contexts_dir.glob("context_*.json"))
        if len(files) == 0:
            return False

        archive_path.mkdir()
        for file in files:
            shutil.move(str(file), str(archive_path))

        self.contexts.clear()
        self.contexts["default"] = Context(
            name="default", current_agent=self.default_agent
        )
        self.current_context = "default"
        return True

    def list_archived_contexts(self) -> List[str]:
        flat_file_list = list(self.archived_contexts_dir.glob("*"))
        return [f.name for f in flat_file_list if f.is_dir()]

    def load_archived_contexts(self, archive_name: str) -> bool:
        folder = self.archived_contexts_dir / archive_name
        if folder.exists():
            for file in folder.glob("context_*.json"):
                if file.exists():
                    with open(file.resolve(), "r") as f:
                        data = json.load(f)
                        context = Context.from_dict(data)
                        self.contexts[context.name] = context
            return True
        return False
