"""changelog.md version updater Plugin.

Description:
    Plugin that updates the version from [Unreleased] to a set version in changelog.md files, that
    follow *keep a changelog* (https://keepachangelog.com/en/1.0.0/). Thereby, it receives an
    updated version as parameter and updates the file accordingly.

Authors:
    - Martin Lautenbacher <martin.lautenbacher@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import logging
import pathlib
from datetime import datetime

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.interfaces.modification_interface import ModificationInterface
from easy_release_automation.plugins.modification.regex_replacer import RegexReplacerPlugin

logger = logging.getLogger(__name__)

UNRELEASED_REGEX = r"(?m)^## \[Unreleased\]$"


class ChangelogVersionUpdaterPlugin(ModificationInterface):
    """Plugin that allows to update the version in changelog.md files."""

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """Initializes the ChangelogVersionUpdaterPlugin"""
        self._release_entry = release_entry
        self._repository_dir = repository_dir
        self._regex_replacer = RegexReplacerPlugin(release_entry, global_config, repository_dir)

    def run(self, file_path_relative: str, version: str):
        """The run method replaces the version in the file via regex substitution.

        Args:
            file_path_relative: path to the conf.py file (relative to the repository).
            version: the new version.
        """

        replacement = f"## [{version}] - {datetime.today().strftime('%Y-%m-%d')}"
        logger.info("replacing '## [Unreleased]' with '%s' in changelog", replacement)
        self._regex_replacer.run(file_path_relative, UNRELEASED_REGEX, replacement)
