# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import sys

# Color palette constants
COLOR_PALETTE = {
    "yellow": "\x1b[33;20m",
    "green": "\033[92m",
    "red": "\x1b[31;20m",
    "bold_white": "\033[1m",
    "bold_red": "\x1b[31;1m",
    "reset": "\x1b[0m",
}


class ACTFormatter(logging.Formatter):
    """
    Log formatter definition for ACT.

    This class defines a custom log formatter for the ACT logger.
    It provides a colorized log output with different colors for each log level.
    """

    # Define the log formats for each level
    PREFIX = "[%(module)24s - "
    POSTFIX = " %(message)s"
    LEVEL_FORMATS = {
        logging.DEBUG: PREFIX
        + f"{COLOR_PALETTE['green']}%(levelname)s{COLOR_PALETTE['reset']}"
        + POSTFIX,
        logging.INFO: PREFIX
        + f"{COLOR_PALETTE['bold_white']}%(levelname)s{COLOR_PALETTE['reset']}"
        + POSTFIX,
        logging.WARNING: PREFIX
        + f"{COLOR_PALETTE['yellow']}%(levelname)s{COLOR_PALETTE['reset']}"
        + POSTFIX,
        logging.ERROR: PREFIX
        + f"{COLOR_PALETTE['red']}%(levelname)s{COLOR_PALETTE['reset']}"
        + POSTFIX,
        logging.CRITICAL: PREFIX
        + f"{COLOR_PALETTE['bold_red']}%(levelname)s{COLOR_PALETTE['reset']}"
        + POSTFIX,
    }

    def format(self, record):
        """
        Format a log record using the custom format.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record.
        """
        level_format = self.LEVEL_FORMATS.get(record.levelno)
        formatter = logging.Formatter(level_format)
        return formatter.format(record)


def clear_handlers():
    """
    Clear all handlers from the ACT logger except for the stream handler to stdout.

    This function removes all handlers from the ACT logger except for the stream handler to stdout.
    It is used to reset the logger to its default state.
    """
    logger = logging.getLogger("ACT")
    for handler in logger.handlers:
        if not isinstance(handler, logging.StreamHandler):
            logger.removeHandler(handler)
            handler.close()


def setup_logger(file_name=None, loglevel=None):
    """
    Set up the ACT logger with the specified file name and log level.

    Args:
        file_name (str, optional): The file name to log to. If None, no file handler is added.
        loglevel (int, optional): The log level to set. If None, the default log level is used.

    Returns:
        None
    """
    logger = logging.getLogger("ACT")
    logger.propagate = False  # prevent duplicate output
    if loglevel is not None:
        logger.setLevel(loglevel)
    formatter = ACTFormatter()
    new_handlers = []
    current_handlers = logger.handlers
    if not any(isinstance(h, logging.StreamHandler) for h in current_handlers):
        new_handlers.append(logging.StreamHandler(sys.stdout))
    if file_name is not None:
        new_handlers.append(logging.FileHandler(file_name, "w", "utf-8"))
    for handler in new_handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)


log = logging.getLogger("ACT")
