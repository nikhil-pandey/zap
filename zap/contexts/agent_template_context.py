import dataclasses
import os
import platform
from datetime import datetime
from typing import Dict, Any

from zap.agents import Agent
from zap.app_state import AppState
from zap.config import AppConfig
from zap.contexts.context import Context
from zap.utils import get_files_content, get_shell


async def build_agent_template_context(
    message: str,
    context: Context,
    agent: Agent,
    state: AppState,
    config: AppConfig,
    contexts: dict[str, Context],
) -> Dict[str, Any]:
    """
    Builds the agent template context as a dictionary.
    """
    list_of_files = state.get_files()
    files = await get_files_content(state.git_repo.root, list_of_files)

    output = {
        "os": platform.system(),
        "shell": await get_shell(),
        "cpus": os.cpu_count(),
        "datetime": datetime.now().isoformat(),
        "message": message,
        "list_of_files": list(list_of_files),
        "files": files,
        "root": state.git_repo.root,
        "repo_metadata": dataclasses.asdict(state.repo_metadata),
    }

    for context_name, ctx in contexts.items():
        if context_name in output:
            # TODO: disallow creation of context with the same name as reserved keys
            raise ValueError(
                f"Context name {context_name} is already in the output dictionary"
            )

        if ctx.messages and len(ctx.messages) > 0:
            output[context_name] = {
                "message": ctx.messages[-1].content,
                "history": [msg.to_dict() for msg in ctx.messages],
            }
        else:
            output[context_name] = {"message": "", "history": []}

    return output
