import pytest
from zap.git_analyzer.analyzer import GitAnalyzer, analyze_repo
from zap.git_analyzer.config import GitAnalyzerConfig
from zap.git_analyzer.exceptions import ParserError, GitAnalyzerError, RepoError


@pytest.mark.asyncio
async def test_git_analyzer(temp_git_repo):
    config = GitAnalyzerConfig()
    analyzer = GitAnalyzer(temp_git_repo.path, config)
    result = await analyzer.analyze()

    assert result.project_info is not None
    assert result.relevant_files is not None
    assert result.git_status is not None
    assert result.recent_commits is not None
    assert result.most_changed_files is not None
    assert result.least_changed_files is not None
    assert result.file_change_count is not None


@pytest.mark.asyncio
async def test_git_analyzer_parser_error(monkeypatch):
    config = GitAnalyzerConfig()
    with pytest.raises(
        RepoError, match="Path /path/to/nonexistent/repo does not exist"
    ):
        GitAnalyzer("/path/to/nonexistent/repo", config)


@pytest.mark.asyncio
async def test_analyze_repo(temp_git_repo):
    result = await analyze_repo(temp_git_repo.path)

    assert result.project_info is not None
    assert result.relevant_files is not None
    assert result.git_status is not None
    assert result.recent_commits is not None
    assert result.most_changed_files is not None
    assert result.least_changed_files is not None
    assert result.file_change_count is not None
