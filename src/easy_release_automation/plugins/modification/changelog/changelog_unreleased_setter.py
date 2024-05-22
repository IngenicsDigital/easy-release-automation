"""Changelog.md Preparation plugin.

Description:
    Plugin that adds an [Unreleased] section to a changelog.md files, that follow
    *keep a changelog* (https://keepachangelog.com/en/1.0.0/).

Authors:
    - Martin Lautenbacher <martin.lautenbacher@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import logging
import pathlib
import re

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.interfaces.modification_interface import (
    ModificationException,
    ModificationInterface,
)
from easy_release_automation.plugins.modification.regex_replacer import RegexReplacerPlugin

logger = logging.getLogger(__name__)

UNRELEASED_REGEX: str = r"(?m)^## \[Unreleased\]$"
RELEASE_SECTION_REGEX: str = r"(?m)(^## \[.+\] - \d\d\d\d-\d\d-\d\d$)"
UNRELEASED_SNIPPET: str = """## [Unreleased]

### Known Errors

### Added

### Changed

### Removed

### Fixed

"""


class ChangelogUnreleasedSetterPlugin(ModificationInterface):
    """Plugin that adds an [Unreleased] section to changelog.md files."""

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """Initializes the ChangelogUnreleasedSetterPlugin"""
        self._release_entry = release_entry
        self._repository_dir = repository_dir
        self._regex_replacer = RegexReplacerPlugin(release_entry, global_config, repository_dir)

    def run(self, file_path_relative: str):
        """The run method adds a [Unreleased] section to the changelog, if it does not exist
        already.

        Args:
            file_path_relative: path to the changelog.md file (relative to the repository).
        """
        logger.info("Update file: %s, repository: %s", file_path_relative, self._release_entry.name)

        self._update_file(file_path_relative)

    def _update_file(self, file_path_relative: str):
        """Rewrites the file at the given path.

        Args:
            file_path: absolute path to the changelog.md file.
        """

        file_path = self._repository_dir / file_path_relative
        unreleased_matcher = self._regex_replacer.compile_regex(UNRELEASED_REGEX)

        try:
            with file_path.open("r", newline="") as in_file:
                content = in_file.read()
        except FileNotFoundError as error:
            raise ModificationException(f"{file_path} not found.") from error

        unreleased_match = re.search(unreleased_matcher, content)
        if unreleased_match is not None:
            logger.info("%s already contains an [Unreleased] section, returning now.", file_path)
            return  # there's already a [Unreleased] section -> do nothing

        replacement = UNRELEASED_SNIPPET + r"\g<1>"
        try:
            self._regex_replacer.run(
                file_path_relative, RELEASE_SECTION_REGEX, replacement, replacement_count=1
            )
        except ModificationException:
            logger.info(
                "%s does not contain any release entry. Appending at end", file_path_relative
            )
            self._regex_replacer.run(
                file_path_relative, r"\Z", "\n\n" + UNRELEASED_SNIPPET, replacement_count=1
            )
