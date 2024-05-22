"""Requirement Updater Plugin with Compiled Requirements

Description:
    This Plugin uses the standard RequirementsUpdaterPlugin to update the requirement files.
    In addition, it pip-compiles the pyproject.toml / requirements file to pin all python packages
    + their transitive dependencies. If a pyproject.toml file is to be updated/compiled, all
    optional dependencies will be compiled into requirements-<extra>.txt files.
    For further information please refer to:
    https://github.com/jazzband/pip-tools

    NOTE: the path to the pyproject.toml can be in a subdirectory of the repository, but must be
    called "pyproject.toml"

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>
    - Martin Lautenbacher <martin.lautenbacher@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import logging
import pathlib
import subprocess

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.interfaces.modification_interface import (
    ModificationException,
    ModificationInterface,
)
from easy_release_automation.plugins.modification.python_requirements.requirements_updater import (
    RequirementsUpdaterPlugin,
)

logger = logging.getLogger(__name__)


class RequirementsUpdaterAndCompilerPlugin(ModificationInterface):
    """Plugin that supports an update and and compilation of requirement/pyproject.toml files"""

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """Initializes the RequirementsUpdaterAndCompilerPlugin"""
        self._release_entry = release_entry
        self._repository_dir = repository_dir
        self._requirement_updater = RequirementsUpdaterPlugin(
            release_entry, global_config, repository_dir
        )

    def run(self, file_paths: list[str] = ["requirements.in"]):
        """The run method updates and compiles the requirement files.

        Args:
            file_paths: List of file paths to the requirement files that should be updated.
        """
        logger.info(
            "Update&Compile Requirements: %s, repository: %s", file_paths, self._release_entry.name
        )
        # Update requirements
        self._requirement_updater.run(file_paths)

        # Compile Requirements
        for file_path in file_paths:
            full_path = self._repository_dir / file_path
            if full_path.suffix == ".toml":
                if full_path.name != "pyproject.toml":
                    raise ModificationException(
                        "Compilation not possible. File name must be 'pyproject.toml'"
                    )
                self._compile_pyproject_toml(full_path)
            else:
                self._compile_requirements(full_path)

    @classmethod
    def _compile_requirements(cls, file_path: pathlib.Path):
        """Compiles the requirements file at the given path.

        Args:
            file_path: path to the un-compiled requirements file.
        """

        logger.debug("Compiling %s", file_path)
        command = f"pip-compile {file_path.name}"
        cls._execute_compilation(command, file_path.parent)

    def _compile_pyproject_toml(self, file_path: pathlib.Path):
        """Compiles the dependencies from a pyproject.toml.

        The output files are requirements.txt, requirements-<extra>.txt.

        Args:
            file_path: path to the un-compiled requirements file.
        """
        logger.debug("Compiling %s", file_path)

        # NOTE: this is not ideal, perhaps move that function to util/ ?
        toml = self._requirement_updater.read_pyproject_toml(file_path)

        try:
            toml_project = toml["project"]
        except KeyError as err:
            raise ModificationException(
                f"{file_path} is not a valid pyproject.toml, no 'project' section found"
            ) from err

        if toml_project.get("dependencies", None):
            command = f"pip-compile -o requirements.txt {file_path.name}"
            self._execute_compilation(command, file_path.parent)

        for extra_dep_section in toml_project.get("optional-dependencies", []):
            command = (
                f"pip-compile "
                f"--extra={extra_dep_section} "
                f"-o requirements-{extra_dep_section}.txt "
                f"{file_path.name}"
            )
            self._execute_compilation(command, file_path.parent)

    @classmethod
    def _execute_compilation(cls, command: str, cwd: pathlib.Path):
        """Runs the specified command as subprocess.

        Args:
            command: the shell command, e.g. 'pip-compile requirements.in'
            cwd: the working directory to run this command from.

        Raises:
            ReleaseModificationException: raised, if the command execution fails.
        """
        try:
            process = subprocess.run(command, capture_output=True, shell=True, check=True, cwd=cwd)
        except subprocess.CalledProcessError as error:
            raise ModificationException(
                f"Executing git command {command} failed with: "
                f"\nstdout: {error.stdout.decode('utf-8')}\nstderr: {error.stderr.decode('utf-8')}"
            ) from error

        logger.debug(
            "stdout: %s\nstderr: %s",
            process.stdout.decode("utf-8"),
            process.stderr.decode("utf-8"),
        )
