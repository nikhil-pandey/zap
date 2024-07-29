class GitAnalyzerError(Exception):
    """Base exception for git_analyzer module."""


class ParserError(GitAnalyzerError):
    """Raised when there's an error parsing a dependency file."""


class RepoError(GitAnalyzerError):
    """Raised when there's an error interacting with the Git repository."""
