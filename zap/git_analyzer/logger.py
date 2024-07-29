import logging

from rich.logging import RichHandler


def setup_logger(log_level=None):
    logger = logging.getLogger("git_analyzer")
    logger.setLevel(log_level if log_level else logging.WARNING)
    handler = RichHandler(rich_tracebacks=True, show_time=False)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


# Initialize with default level
LOGGER = setup_logger()


def set_log_level(level):
    """
    Set the log level for the git_analyzer logger.

    Args:
        level (str or int): The log level to set. Can be a string (e.g., 'DEBUG', 'INFO')
                            or an integer (e.g., logging.DEBUG, logging.INFO).
    """
    LOGGER.setLevel(level)
