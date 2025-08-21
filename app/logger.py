"""
This module is used to setup the logging configuration for the application.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_logger(logLevel: int = logging.INFO) -> None:
    """
    Creates log file.
    """

    # check if logs directory exists, if not create it
    if not Path(".logs").exists():
        Path(".logs").mkdir()

    # Set up logging
    logging.basicConfig(
        level=logLevel,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=".logs/job_finder.log",
    )
