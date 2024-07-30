import logging

from zap.git_analyzer.logger import setup_logger, set_log_level
from rich.logging import RichHandler


def test_setup_logger():
    logger = setup_logger()
    assert logger.name == "git_analyzer"
    assert logger.level == logging.WARNING
    assert len(logger.handlers) >= 1
    assert any(isinstance(handler, RichHandler) for handler in logger.handlers)


def test_set_log_level():
    logger = setup_logger()
    set_log_level(logging.DEBUG)
    assert logger.level == logging.DEBUG

    set_log_level("WARNING")
    assert logger.level == logging.WARNING
