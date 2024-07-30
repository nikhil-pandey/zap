import logging

import pytest

from zap.git_analyzer.analyzer import GitAnalyzer
from zap.git_analyzer.config import GitAnalyzerConfig
from zap.git_analyzer.exceptions import GitAnalyzerError, RepoError

LOGGER = logging.getLogger("git_analyzer")


@pytest.mark.asyncio
async def test_git_analyzer_repo_not_found():
    config = GitAnalyzerConfig()
    with pytest.raises(RepoError):
        GitAnalyzer("/path/to/nonexistent/repo", config)


@pytest.mark.asyncio
async def test_git_analyzer_general_error(temp_git_repo, monkeypatch):
    config = GitAnalyzerConfig()
    analyzer = GitAnalyzer(temp_git_repo.path, config)

    def mock_explore():
        raise Exception("Unexpected error")

    monkeypatch.setattr(analyzer.repo_explorer, "explore", mock_explore)

    with pytest.raises(GitAnalyzerError):
        await analyzer.analyze()
