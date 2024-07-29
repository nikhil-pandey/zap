import asyncio
from typing import Optional

from .config import GitAnalyzerConfig
from .exceptions import GitAnalyzerError, ParserError
from .logger import LOGGER, set_log_level
from .models.exploration_result import ExplorationResult
from .repo.git_repo import GitRepo
from .repo.repo_explorer import RepoExplorer


class GitAnalyzer:
    """
    Main class for analyzing Git repositories.

    This class provides high-level functionality to analyze a Git repository,
    including its structure, dependencies, and commit history.
    """

    def __init__(
        self, path: Optional[str] = None, config: Optional[GitAnalyzerConfig] = None
    ):
        """
        Initialize a GitAnalyzer instance.

        Args:
            path (str, optional): Path to the Git repository. If None, the current directory is used.
            config (GitAnalyzerConfig, optional): Custom configuration. If None, default configuration is used.
        """
        self.config = config or GitAnalyzerConfig()
        set_log_level(self.config.log_level)
        self.git_repo = GitRepo(path)
        self.repo_explorer = RepoExplorer(self.git_repo, self.config)

    async def analyze(self) -> ExplorationResult:
        LOGGER.info(f"Starting analysis of repository: {self.git_repo.path}")
        try:
            exploration_result = await self.repo_explorer.explore()
            LOGGER.info(f"Analysis completed for repository: {self.git_repo.path}")
            return exploration_result
        except ParserError as e:
            LOGGER.error(f"Parser error during analysis: {str(e)}")
            raise
        except Exception as e:
            LOGGER.error(f"Error during analysis: {str(e)}")
            raise GitAnalyzerError(f"Error during analysis: {str(e)}") from e


async def analyze_repo(
    path: Optional[str] = None, config: Optional[GitAnalyzerConfig] = None
) -> ExplorationResult:
    """
    Convenience function to analyze a Git repository.

    Args:
        path (str, optional): Path to the Git repository. If None, the current directory is used.
        config (GitAnalyzerConfig, optional): Custom configuration. If None, default configuration is used.

    Returns:
        ExplorationResult: An object containing various analysis results.
    """
    LOGGER.info(f"Analyzing repository at path: {path or 'current directory'}")
    analyzer = GitAnalyzer(path, config)
    return await analyzer.analyze()


if __name__ == "__main__":
    import sys

    repo_path = sys.argv[1] if len(sys.argv) > 1 else None
    result = asyncio.run(analyze_repo(repo_path))
    print(result)
