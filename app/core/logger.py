"""
Application logging configuration.

This module configures a single application logger that should be
used throughout the project instead of print().
"""

from __future__ import annotations

import logging
import sys


LOGGER_NAME = "carwash"


def configure_logging(debug: bool = True) -> logging.Logger:
    """
    Configure and return the application logger.

    Calling this function multiple times will not add duplicate
    handlers.
    """

    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    logger.propagate = False

    return logger


logger = configure_logging()