"""Regex Replace Plugin.

Description:
    Plugin that allows replacing text in arbitrary files via regex. Thereby, it receives a
    match-string and a replacement string as parameter and updates the file accordingly.
    When specific modes/flags are required, they have to be set via inline flags, e.g.,
    (?i) for case insensitivity.
    See https://docs.python.org/3/library/re.html for more information.
Authors:
    - Martin Lautenbacher <martin.lautenbacher@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import logging
import pathlib
import re
from typing import Union

from easy_release_automation.core.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.interfaces.modification_interface import (
    ModificationException,
    ModificationInterface,
)

logger = logging.getLogger(__name__)


class RegexReplacerPlugin(ModificationInterface):
    """Plugin that allows to update configuration files."""

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """Initializes the RegexReplacerPlugin"""
        self._release_entry = release_entry
        self._repository_dir = repository_dir

    def run(
        self,
        file_path_relative: str,
        regex: str,
        replacement: Union[str, list[str]] = "",
        replacement_count: int = 0,
    ):
        """The run method replaces anything matching the regex with replacement in the file.

        Raises:
            ReleaseModificationException: Thrown, if the regex is not valid or has no matches in
                                          the file.

        Args:
            file_path_relative: path to the configuration file (relative to the repository).
            regex: a regex string to match all text snippets, that need to be replaced.
            replacement: string, or a list of strings, that will be joined to build a replacement
                         string.
            replacement_count: the number of occurrences to replace. If set to 0,
                               all occurrences will be replaced.
        """
        logger.info("Update file: %s, repository: %s", file_path_relative, self._release_entry.name)

        replacement_str = self._build_replacement_str(replacement)
        file_path = self._repository_dir / file_path_relative
        pattern = self.compile_regex(regex)
        self._update_file(file_path, pattern, replacement_str, replacement_count=replacement_count)

    @classmethod
    def _build_replacement_str(cls, replacement: Union[str, list[str]] = "") -> str:
        """Builds the replacement string from a list of strings by joining it, if it is a list.
        Otherwise the string will simply be returned.

        Args:
            replacement: string, or a list of strings, that will be joined to build a replacement
                         string.

        Returns:
            str: the compiled replacement string
        """
        return "".join(replacement) if isinstance(replacement, list) else replacement

    @classmethod
    def compile_regex(cls, regex: str) -> re.Pattern:
        """Compiles the regex and throws an appropriate exception, when it fails.

        Args:
            regex (str): The regex definition as string.

        Raises:
            ReleaseModificationException: Thrown, if the regex is not valid.

        Returns:
            re.Pattern: The compiled regex pattern.
        """
        try:
            pattern = re.compile(regex)
        except re.error as regex_error:
            raise ModificationException(
                f"compiling '{regex}' as regex failed with {regex_error}"
            ) from regex_error

        logger.debug("Compiled pattern: %s", pattern)

        return pattern

    def _update_file(
        self,
        file_path: pathlib.Path,
        pattern: re.Pattern,
        replacement_str: str,
        replacement_count: int,
    ):
        """Rewrites the file at the given path.

        Raises:
            ReleaseModificationException: Thrown, if the search pattern is not found.

        Args:
            file_path: absolute path to the file.
            pattern: a compiled regex pattern to match all text snippets, that need to bee replaced.
            replacement_str: the replacement text.
            replacement_count: the number of occurrences to replace. If set to 0,
                               all occurrences will be replaced.
        """
        try:
            with file_path.open("r", newline="") as in_file:
                content = in_file.read()
        except FileNotFoundError as file_not_found_error:
            raise ModificationException(f"{file_path} not found.") from file_not_found_error

        logger.debug("existing file contents: \n%s", content)

        match = re.search(pattern, content)
        if match is None:
            raise ModificationException(f"{file_path} does not contain a match for {pattern}.")

        new_content = re.sub(pattern, replacement_str, content, count=replacement_count)

        logger.debug("new file contents: \n%s", new_content)

        with file_path.open("w", newline="") as out_file:
            out_file.write(new_content)
