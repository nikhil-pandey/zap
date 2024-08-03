import logging

from rich.logging import RichHandler


def setup_logger():
    logger = logging.getLogger("zap")
    logger.setLevel(logging.INFO)
    handler = RichHandler(rich_tracebacks=True, show_time=False)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


LOGGER = setup_logger()
