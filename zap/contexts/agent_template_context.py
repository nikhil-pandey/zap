import dataclasses
import os
from dataclasses import dataclass

from zap.agents import Agent
from zap.app_state import AppState
from zap.config import AppConfig
from zap.contexts.context import Context
from zap.utils import get_files_content


@dataclass
class AgentTemplateContext:
    """
    This class represents the context of an agent template.
    """

    """
    The message to be displayed to the user.    
    """
    message: str

    """
    The list of files in the context.
    """
    list_of_files: list[str]

    """
    The content of all the files
    """
    files: str

    """
    The root directory of the git repository.
    """
    root: str

    """
    The operating system of the user.
    """
    os: str

    """
    The list of git exploration results.
    """
    repo_metadata: dict  # TODO: refine this further

    @classmethod
    async def build(cls, message: str, context: Context, agent: Agent, state: AppState,
                    config: AppConfig) -> "AgentTemplateContext":
        """
        Builds the AgentTemplateContext object.
        """
        list_of_files = state.get_files()
        files = await get_files_content(state.git_repo.root, list_of_files)
        return cls(
            message,
            list(list_of_files),
            files,
            root=state.git_repo.root,
            os=os.name,
            repo_metadata=dataclasses.asdict(state.repo_metadata),
        )
