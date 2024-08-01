import asyncio
from typing import Optional

from .config import GitAnalyzerConfig
from .exceptions import GitAnalyzerError, ParserError
from .logger import LOGGER, set_log_level
from .models.exploration_result import ExplorationResult
from .repo.git_repo import GitRepo
from .repo.repo_explorer import RepoExplorer
from .repomap import RepoMap

class GitAnalyzer:
    """
    Main class for analyzing Git repositories.
    """
    def __init__(self, path: Optional[str] = None, config: Optional[GitAnalyzerConfig] = None):
        self.config = config or GitAnalyzerConfig()
        set_log_level(self.config.log_level)
        self.git_repo = GitRepo(path)
        self.repo_explorer = RepoExplorer(self.git_repo, self.config)
        self.repo_map = RepoMap(root=path)

    async def analyze(self) -> ExplorationResult:
        LOGGER.info(f"Starting analysis of repository: {self.git_repo.path}")
        try:
            exploration_result = await self.repo_explorer.explore()
            repo_map_result = self.repo_map.get_repo_map(
                chat_files=[], other_files=list(await self.git_repo.get_tracked_files())
            )
            LOGGER.info(f"Analysis completed for repository: {self.git_repo.path}")
            # You can include repo_map_result in the ExplorationResult if needed
            return exploration_result
        except ParserError as e:
            LOGGER.error(f"Parser error during analysis: {str(e)}")
            raise
        except Exception as e:
            LOGGER.error(f"Error during analysis: {str(e)}")
            raise GitAnalyzerError(f"Error during analysis: {str(e)}") from e

async def analyze_repo(path: Optional[str] = None, config: Optional[GitAnalyzerConfig] = None) -> ExplorationResult:
    LOGGER.info(f"Analyzing repository at path: {path or 'current directory'}")
    analyzer = GitAnalyzer(path, config)
    return await analyzer.analyze()

if __name__ == "__main__":
    import sys

    repo_path = sys.argv[1] if len(sys.argv) > 1 else None
    result = asyncio.run(analyze_repo(repo_path))
    print(result)
