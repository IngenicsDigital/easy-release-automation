"""Logging-Wrapper

Description:
    Defines info-printouts that allow more structure in the terminal.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import logging
from dataclasses import asdict

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry

logger = logging.getLogger(__name__)

MAJOR_LOG_DELIMITER = "\n" + ("$" * 80) + "\n"
CHAPTER_DELIMITER = "\n" + ("*" * 80) + "\n"
SUB_CHAPTER_DELIMITER = CHAPTER_DELIMITER
PLUGIN_DELIMITER = "\n" + ("_" * 80)


class CustomLogRecord(logging.LogRecord):
    """Reduces the origin string to file-name, function-name and linenumber."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin = f"[{self.filename}.{self.funcName}:{self.lineno}]"


def configure_logging(level: str = "INFO"):
    """Setting up the logging-level and format."""

    logging.setLogRecordFactory(CustomLogRecord)
    log_format = "%(levelname)-7s %(origin)-50s %(message)s"
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%d/%b/%Y %H:%M:%S",
    )


def format_major(message: str):
    """Formats major checkpoints, such as starting or finishing the program."""
    return "".join(["\n", MAJOR_LOG_DELIMITER, "\n", message, "\n", MAJOR_LOG_DELIMITER])


def format_minor(message: str):
    """Formats a minor checkpoint during the execution."""
    return "".join(["\n\n---- ", message, PLUGIN_DELIMITER])


def format_chapter(chapter: str):
    """Formats release chapters during the execution."""
    return "".join(["\n", CHAPTER_DELIMITER, "**** Chapter: ", chapter, CHAPTER_DELIMITER])


def format_sub_chapter(sub_chapter: str):
    """Formats release sub-chapters during the execution."""
    return "".join(
        ["\n", SUB_CHAPTER_DELIMITER, "**** Sub-Chapter: ", sub_chapter, SUB_CHAPTER_DELIMITER]
    )


def log_release_information(release_entries: list[ReleaseEntry], global_config: GlobalConfig):
    """Logs release information for the upcoming release."""
    releasing = ""
    skipping = ""
    release_type = (
        "Executing Test Release" if global_config.test_run else "Executing Production Release"
    )

    for release_entry in release_entries:
        repo_string = ""
        repo_string += "\t - "
        repo_string += f"Repository: '{release_entry.public.name}'"
        repo_string += f", using version: '{release_entry.public.version}'"
        repo_string += f", main-branch: '{release_entry.public.main_branch}'"
        repo_string += f", stable-branch: '{release_entry.public.stable_branch}'."
        repo_string += "\n"

        if release_entry.private.should_skip:
            skipping += repo_string
        else:
            releasing += repo_string
    global_config_str = "\n".join(
        [f"\t - {key}: '{value}'" for key, value in asdict(global_config).items()]
    )

    logger.info(
        format_major(
            f"\033[1m{release_type}\033[0m"
            f"\n\nReleasing:\n{releasing}"
            f"\n\nSkipping:\n{skipping}"
            f"\n\nGlobal Configuration:\n{global_config_str}"
        )
    )
