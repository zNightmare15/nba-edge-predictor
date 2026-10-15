"""Structured logging configuration using Rich."""

import logging
import sys

def setup_logger(name: str = "nba_ml", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        try:
            from rich.logging import RichHandler
            handler = RichHandler(rich_tracebacks=True, markup=True)
        except ImportError:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger()

