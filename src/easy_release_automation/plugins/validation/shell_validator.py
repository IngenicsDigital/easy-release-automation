"""Shell-Validator Plugin

Description:
    Shell-Validator that executes shell-commands for validation.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import logging
import pathlib
import subprocess

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.interfaces.validation_interface import (
    ValidationException,
    ValidationInterface,
)

logger = logging.getLogger(__name__)


class ShellValidationPlugin(ValidationInterface):
    """Shell Validator that runs shell commands."""

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """Initializes the ShellValidationPlugin"""
        self._release_entry = release_entry
        self._repository_dir = repository_dir

    def run(self, command: list[str]):
        """The run method executes the given command in the repository directory. This allows to
        use relative paths in the commands.

        Args:
            command: command to execute in the given repository.
        """

        logger.info("Shell Executor, repository: %s", self._release_entry.name)

        self._execute_shell_command(command)

        logger.info("Successfully run %s for %s", command, self._release_entry.name)

    def _execute_shell_command(self, command: list[str]):
        """Executes the given command and validates if the command is run through successfully.

        Args:
            command: bash command to execute.
        Raises:
            ValidationException: if the bash command returns a non-zero value.
        """
        logger.info("Executing Shell Command: %s from directory: %s", command, self._repository_dir)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=self._repository_dir)
        logger.info("Output:")
        while process.poll() is None:
            line = process.stdout.readline()  # type: ignore [union-attr]
            if line:
                logger.info(line.decode("utf-8"))

        if process.returncode != 0:
            raise ValidationException(
                f"Executing bash command {command} failed. Error Code: {process.returncode}"
            )
