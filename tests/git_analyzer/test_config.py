from zap.git_analyzer.config import GitAnalyzerConfig


def test_git_analyzer_config_default():
    config = GitAnalyzerConfig()
    assert config.commit_limit == 10
    assert config.most_changed_files_limit == 10
    assert config.least_changed_files_limit == 10
    assert config.log_level == "INFO"


def test_git_analyzer_config_custom():
    custom_config = GitAnalyzerConfig(
        commit_limit=20,
        most_changed_files_limit=15,
        least_changed_files_limit=5,
        log_level="DEBUG",
    )
    assert custom_config.commit_limit == 20
    assert custom_config.most_changed_files_limit == 15
    assert custom_config.least_changed_files_limit == 5
    assert custom_config.log_level == "DEBUG"
