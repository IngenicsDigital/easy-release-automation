"""Requirement Updater Plugin

Description:
    Plugin, that updates python-dependencies in requirements.* and pyproject.toml files with the
    new dependencies of other repositories. Thereby, it searches for the corresponding lines within
    the requirements file and updates their tag or branch. Requirement entries must have one of the
    the following formats:

    - requirement_id @ <git repo url>
    - requirement_id @ <git repo url>@tag/branch
    - git+https://<https git repo url>@tag/branch
        (e.g. "git+https://gitlab.example.com/path/awesome_project1.git@0.8.1")
    - git+ssh://<SSH git repo url>@tag/branch
        (e.g. "git+ssh://git@gitlab.example.local/path/awesome_project1.git@main"
        Note: the ':' in the ssh link after the host part is replaced with a '/')
            Example: git@gitlab.example.local: -> git@gitlab.example.local/

    Other formats, i.e. without reference to a repository are currently not supported. This Plugin
    is written to support test runs. This means, that in case of a test-run, the requirements are
    not updated to the newest tag of other repositories, but their latest version of the main
    branch.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>
    - Martin Lautenbacher <martin.lautenbacher@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import logging
import pathlib
import re

import tomlkit

from easy_release_automation.configuration import GlobalConfig, PublicReleaseEntry, ReleaseEntry
from easy_release_automation.interfaces.modification_interface import (
    ModificationException,
    ModificationInterface,
)
from easy_release_automation.plugins.modification.regex_replacer import RegexReplacerPlugin

logger = logging.getLogger(__name__)


class RequirementsUpdaterPlugin(ModificationInterface):
    """Plugin that supports an update to requirement files.

    The plugin will search in the requirement file for dependencies defined in the ERA release
    config and update those with the corresponding reference/version defined
    """

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """Initializes the RequirementsUpdaterPlugin."""
        self._release_entry = release_entry
        self._global_config = global_config
        self._repository_dir = repository_dir
        self._regex_replacer = RegexReplacerPlugin(release_entry, global_config, repository_dir)

    def run(self, file_paths: list[str] = ["requirements.txt"]) -> None:
        """Updates all requirement files for the given requirements file paths.

        Args:
            file_paths: Paths to the requirement files that should be updated.
        """
        logger.info("Update_Requirements: %s, repository: %s", file_paths, self._release_entry.name)

        for file_path in file_paths:
            self._update_file(file_path)

    def _update_file(self, file_path: str) -> None:
        """Updates a file with the new dependencies.

        Args:
            file_path: path to the requirement file.
        """
        full_path = self._repository_dir / file_path

        for dependency in self._release_entry.private.dependencies.values():
            logger.info(
                "Update dependency '%s' in %s/%s",
                dependency.name,
                self._repository_dir.name,
                file_path,
            )

            reference = self._determine_reference(dependency)
            plain_url = self._strip_dependency_url(dependency.url)
            pattern, replacement = self._build_dependency_replacer_strings(plain_url, reference)

            if full_path.suffix == ".toml":
                # pyproject.toml
                self._update_pyproject_toml_file(full_path, pattern, replacement)
            else:
                # requirements.txt, requirements.in
                self._update_requirement_file(pathlib.Path(file_path), pattern, replacement)

        with open(full_path, "r", encoding="utf-8") as file:
            logger.debug("Updated Requirement-File %s to: \n%s", full_path, file.read())

    def _determine_reference(self, dependency: PublicReleaseEntry) -> str:
        """Determines to reference to update to. Uses 'main' if no version is specified or ERA is
        run in testing mode. Uses the version specified in the ERA config otherwise.

        Args:
            dependency: the dependency from the ERA release config

        Returns:
            str: the reference/version to update to
        """
        if dependency.version == "" or dependency.version is None:
            reference = dependency.main_branch
            logger.info(
                "Using main-branch as reference for %s, as no version given", dependency.name
            )
        elif self._global_config.test_run:
            reference = dependency.main_branch
            logger.info(
                "Using main-branch as reference for %s, as running test-run.", dependency.name
            )
        else:
            reference = dependency.version
            logger.info("Using '%s' as reference for repository: %s", reference, dependency.name)

        return reference

    @classmethod
    def _strip_dependency_url(cls, url: str) -> str:
        """Removes url-prefixes (git@, https://) and suffixes (.git) from dependency git urls.

        Args:
            url: dependency (git-)url

        Returns:
            str: the stripped url
        """
        url_plain = re.sub(r"\.git.*$", "", url, flags=re.IGNORECASE)
        url_plain = re.sub(r"^(?:git@|https://)", "", url_plain, flags=re.IGNORECASE)
        return url_plain

    @classmethod
    def _build_dependency_replacer_strings(cls, url: str, reference: str) -> tuple[str, str]:
        """Builds regexes for matching/replacing the reference in requirements-files.

        Args:
            url (str): the stripped dependency url
            reference (str): the new dependency reference

        Returns:
            tuple[str, str]: regex (pattern, replacement) to be used with re.sub(...) to update the
                             reference.
        """
        pattern = rf"(?mi)(.*{url}(?:\.git){{0,1}})(@.*){{0,1}}$"
        replacement = rf"\1@{reference}"
        return (pattern, replacement)

    def _update_requirement_file(
        self, requirements_path: pathlib.Path, pattern: str, replacement: str
    ) -> None:
        """Rewrites the requirements file with the updated dependencies.

        Args:
            requirements_path: relative path to the requirements file that should be updated.
            pattern: a regex to match the dependency
            replacement: the corresponding replacement string
        """
        try:
            self._regex_replacer.run(requirements_path, pattern, replacement, replacement_count=0)
        except ModificationException:
            logger.debug("No matching dependency found in: %s.", requirements_path)

    @classmethod
    def _update_pyproject_toml_file(
        cls, pyproject_path: pathlib.Path, pattern: str, replacement: str
    ) -> None:
        """Rewrites the pyproject.toml file with updated dependencies.

        Args:
            pyproject_path: path to the requirements file that should be updated.
            pattern: a regex to match the dependency
            replacement: the corresponding replacement string with the new reference
        """
        toml = cls.read_pyproject_toml(pyproject_path)

        cls._update_toml_dependencies(toml, pattern, replacement)
        cls._rewrite_toml_file(pyproject_path, toml)

    @staticmethod
    def read_pyproject_toml(file_path: pathlib.Path) -> tomlkit.TOMLDocument:
        """Parses the pyproject.toml file.

        Args:
            file_path (pathlib.Path): the path to the pyproject.toml file.

        Raises:
            ReleaseModificationException: raised, if file not found, toml cannot be parsed or
                                          toml does not contain a 'project' section.

        Returns:
            tomlkit.TOMLDocument: the parsed toml.
        """
        try:
            with open(file_path, mode="rb") as f:
                content = f.read()
                toml = tomlkit.parse(content)
        except FileNotFoundError as err:
            raise ModificationException(f"File {file_path} not found.") from err
        except tomlkit.exceptions.ParseError as err:
            raise ModificationException(f"File {file_path} is not valid TOML: {err}") from err

        return toml

    @classmethod
    def _update_toml_dependencies(
        cls, toml: tomlkit.TOMLDocument, pattern: str, replacement: str
    ) -> None:
        """Updates dependencies in a pyproject.toml file.

        Args:
            toml: the parsed pyproject.toml file.
            pattern: a regex to match the dependency
            replacement: the corresponding replacement string with the new reference
        """
        try:
            toml_project = toml["project"]
            assert isinstance(toml_project, tomlkit.items.Table)
        except (AssertionError, KeyError) as err:
            raise ModificationException("This is not a valid pyproject.toml") from err

        cls._update_toml_dependency(
            toml_project.get("dependencies", tomlkit.array()), pattern, replacement
        )
        for _, entries in toml_project.get("optional-dependencies", tomlkit.table()).items():
            cls._update_toml_dependency(
                entries,
                pattern,
                replacement,
            )

    @classmethod
    def _rewrite_toml_file(cls, pyproject_path: pathlib.Path, toml: tomlkit.TOMLDocument) -> None:
        """Overwrites the pyproject.toml file.

        Args:
            pyproject_path: path to the pyproject.toml file.
            toml: Toml object to be written to file.
        """
        with open(pyproject_path, mode="w", encoding="utf-8") as toml_file:
            tomlkit.dump(toml, toml_file)

    @classmethod
    def _update_toml_dependency(
        cls, toml_section: tomlkit.items.Array, pattern: str, replacement: str
    ) -> None:
        """Updates the dependencies in the specified toml_section.

        Args:
            toml_section: The toml section containing the dependencies, e.g. project.dependencies or
                          project.optional-dependencies.test.
            pattern: a regex to match the dependency
            replacement: the corresponding replacement string with the new reference
        """
        for idx, item in enumerate(toml_section):
            toml_section[idx] = re.sub(pattern, replacement, item, count=1)
