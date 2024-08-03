import asyncio
from typing import Optional

from .config import GitAnalyzerConfig
from .exceptions import GitAnalyzerError, ParserError
from .logger import LOGGER, set_log_level
from .models.exploration_result import ExplorationResult
from zap.git_analyzer.git_repo import GitRepo
from zap.git_analyzer.repo_explorer import RepoExplorer


class GitAnalyzer:
    """
    Main class for analyzing Git repositories.
    """

    def __init__(self, path: Optional[str] = None, config: Optional[GitAnalyzerConfig] = None):
        self.config = config or GitAnalyzerConfig()
        set_log_level(self.config.log_level)
        self.git_repo = GitRepo(path)
        self.repo_explorer = RepoExplorer(self.git_repo, self.config)

    async def analyze(self) -> ExplorationResult:
        LOGGER.info(f"Starting analysis of repository: {self.git_repo.path}")
        try:
            exploration_result = await self.repo_explorer.explore()
            LOGGER.info(f"Analysis completed for repository: {self.git_repo.path}")
            # You can include repo_map_result in the ExplorationResult if needed
            return exploration_result
        except ParserError as e:
            LOGGER.error(f"Parser error during analysis: {str(e)}")
            raise
        except Exception as e:
            LOGGER.error(f"Error during analysis: {str(e)}")
            raise GitAnalyzerError(f"Error during analysis: {str(e)}") from e
