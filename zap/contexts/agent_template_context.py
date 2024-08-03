import dataclasses
import os
import platform
from datetime import datetime
from typing import Dict, Any

from zap.agents import Agent
from zap.app_state import AppState
from zap.commands.advanced_input import UserInput
from zap.config import AppConfig
from zap.contexts.context import Context
from zap.git_analyzer.repo_map.repo_map import RepoMap
from zap.utils import get_files_content, get_shell, get_files_content_from_tags


async def build_agent_template_context(
    input: UserInput,
    context: Context,
    agent: Agent,
    state: AppState,
    config: AppConfig,
    contexts: dict[str, Context],
    repo_map: RepoMap
) -> Dict[str, Any]:
    """
    Builds the agent template context as a dictionary.
    """
    list_of_files = state.get_files()
    list_of_files.update(input.file_paths)
    files = await get_files_content(state.git_repo.root, list_of_files)
    ranked_tags = repo_map.get_ranked_tags_map(
        focus_files=list(list_of_files),
        mentioned_idents=input.symbols,
        max_files=100,
        max_tags_per_file=1000,
    )
    repo_map = await get_files_content_from_tags(state.git_repo.root, ranked_tags, prepend_line_numbers=True,
                                                 exclude_files=list_of_files, limit=20000)

    output = {
        "os": platform.system(),
        "shell": await get_shell(),
        "cpus": os.cpu_count(),
        "datetime": datetime.now().isoformat(),
        "message": input.message,
        "list_of_files": list(list_of_files),
        "files": files,
        "root": state.git_repo.root,
        "repo_metadata": dataclasses.asdict(state.repo_metadata),
        "repo_map": repo_map,
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
