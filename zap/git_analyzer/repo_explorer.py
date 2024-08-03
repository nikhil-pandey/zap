import asyncio
from typing import Dict, List, Tuple

from .git_repo import GitRepo
from zap.git_analyzer.config import GitAnalyzerConfig
from zap.git_analyzer.logger import LOGGER
from zap.git_analyzer.models.dependency import DependencyInfo, ProjectInfo, CommitInfo
from zap.git_analyzer.models.exploration_result import ExplorationResult
from zap.git_analyzer.parsers.factory import ParserFactory


class RepoExplorer:
    """
    Explores a Git repository to gather various information about its structure and history.
    """

    def __init__(self, git_repo: GitRepo, config: GitAnalyzerConfig):
        """
        Initialize a RepoExplorer instance.

        Args:
            git_repo (GitRepo): An instance of GitRepo representing the repository to explore.
            config (GitAnalyzerConfig): Configuration for the exploration.
        """
        self.git_repo = git_repo
        self.config = config
        self.dependency_cache = {}

    async def explore(self) -> ExplorationResult:
        """
        Perform a comprehensive exploration of the repository.

        This method gathers information about the project structure, Git status,
        recent commits, and file change statistics.

        Returns:
            ExplorationResult: An object containing various exploration results.
        """
        # This creates tries and caches the file content
        await self.git_repo.refresh()
        if not self.config.explore:
            LOGGER.info("Exploration is disabled. Skipping exploration.")
            return ExplorationResult(
                project_info=ProjectInfo(dependencies={}),
                relevant_files={},
                git_status={},
                recent_commits=[],
                most_changed_files=[],
                least_changed_files=[],
                file_change_count={}
            )

        LOGGER.info(f"Starting exploration of repository: {self.git_repo.path}")
        tasks = [
            self.analyze_project_structure(),
            self.get_git_status(),
            self.get_recent_commits(),
            self.git_repo.get_file_change_count(),
        ]
        results = await asyncio.gather(*tasks)

        dependencies, relevant_files = results[0]
        git_status = results[1]
        recent_commits = results[2]
        file_change_count = results[3]

        most_changed_files = sorted(
            file_change_count.items(), key=lambda x: x[1], reverse=True
        )[: self.config.most_changed_files_limit]
        least_changed_files = sorted(file_change_count.items(), key=lambda x: x[1])[
                              : self.config.least_changed_files_limit
                              ]

        project_info = ProjectInfo(dependencies=dependencies)

        LOGGER.info(f"Exploration completed for repository: {self.git_repo.path}")
        return ExplorationResult(
            project_info=project_info,
            relevant_files=relevant_files,
            git_status=git_status,
            recent_commits=recent_commits,
            most_changed_files=most_changed_files,
            least_changed_files=least_changed_files,
            file_change_count=file_change_count,
        )

    async def analyze_project_structure(
            self,
    ) -> Tuple[Dict[str, DependencyInfo], Dict[str, int]]:
        """
        Analyze the project structure and dependencies.

        This method identifies dependency files in the repository and parses them
        to extract dependency information.

        Returns:
            Tuple[Dict[str, DependencyInfo], Dict[str, int]]: A tuple containing
            dependency information and relevant file counts.
        """
        LOGGER.info("Analyzing project structure")
        tracked_files = await self.git_repo.get_tracked_files()
        dependency_files = [
            f for f in tracked_files if ParserFactory.is_dependency_file(f)
        ]
        LOGGER.debug(f"Found {len(dependency_files)} dependency files")

        parse_tasks = []
        for file_path in dependency_files:
            try:
                content = await self.git_repo.get_file_content(file_path)
                parser = ParserFactory.get_parser(file_path)
                parse_tasks.append(parser.parse(content, file_path))
            except Exception as e:
                LOGGER.error(f"Error parsing file {file_path}: {str(e)}")

        dependency_infos = []
        for task in asyncio.as_completed(parse_tasks):
            try:
                dependency_info = await task
                dependency_infos.append(dependency_info)
            except Exception as e:
                LOGGER.error(f"Error parsing file: {str(e)}")
                dependency_infos.append(None)

        dependencies = {
            file_path: info
            for file_path, info in zip(dependency_files, dependency_infos) if info
        }

        relevant_files = {}
        for dep_info in dependencies.values():
            for file in dep_info.config_files:
                relevant_files[file] = relevant_files.get(file, 0) + 1

        LOGGER.info(f"Project analysis created. Found {len(dependencies)} dependency files")
        LOGGER.debug(f"Dependency files: {dependency_files}")
        return dependencies, relevant_files

    async def get_git_status(self) -> Dict[str, List[str]]:
        """
        Get the current Git status of the repository.

        Returns:
            Dict[str, List[str]]: A dictionary containing lists of new, modified, and deleted files.
        """
        LOGGER.info("Fetching Git status")
        status = await self.git_repo.get_status()
        LOGGER.debug(f"Git status: {status}")
        return status

    async def get_recent_commits(self) -> List[CommitInfo]:
        """
        Get the most recent commits in the repository.

        The number of commits fetched is determined by the 'commit_limit' configuration setting.

        Returns:
            List[CommitInfo]: A list of CommitInfo objects representing the most recent commits.
        """
        LOGGER.info(f"Fetching {self.config.commit_limit} most recent commits")
        commits = await self.git_repo.get_recent_commits(self.config.commit_limit)
        LOGGER.debug(f"Found {len(commits)} recent commits")
        return commits
