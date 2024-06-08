"""Plugin-Executor

Description:
    Initializes all plugins and executes their run method with the given key-word arguments. It
    contains 4 stages:
    - modify_release_branch: executes specified plugins for modifying the release branch.
    - validate_release_branch: executes specified plugins for validating the release branch.
    - finalize_merge_back_branch: executes specified plugins for finalizing the merge-back branch.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import importlib.metadata
import logging
import pathlib
from typing import Optional

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.utils.logging_wrapper import format_minor, format_sub_chapter

logger = logging.getLogger(__name__)

MODIFICATION_ENTRYPOINT_GROUP = "repository.modification"
VALIDATION_ENTRYPOINT_GROUP = "repository.validation"


class PluginExecutorError(Exception):
    """For exceptions during actions of the PluginExecutor."""


class PluginExecutor:
    """Executor for the Plugin-Mechanism in ERA."""

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        self._release_entry = release_entry
        self._global_config = global_config
        self._repository_dir = repository_dir

    def _execute_plugins(
        self, entry_group: str, requested_entry_points: list[dict[str, Optional[dict]]]
    ):
        """Initializes all the requested entry-point classes for the given entry group and executes
        their run method.

        Args:
            entry_group: entry group of the entry points.
            requested_entry_points: all requested entry-points (classes) that should be executed and
                an optional dictionary, that will be handed over as a keyword arguments for the
                entry-points run method.
        Raises:
            PluginExecutorError, if the specified plugin from the telematics-config.yml is not
                existing.
        """
        # Get a dictionary of all entry points for the given group (specified in the setup.cfg)
        entry_points = self._get_entry_point_dictionary(entry_group)

        for entry in requested_entry_points:
            # Get entry-point name and kwargs from release-configuration
            requested_entry_point, key_word_args = next(iter(entry.items()))
            # Validate, that entry-point exists
            if requested_entry_point not in entry_points:
                error_msg = (
                    f"Unknown entry-point specified in release-config.yml: {requested_entry_point}."
                    f" Available entry-points: {entry_points.keys()}"
                )
                logger.error(error_msg)
                raise PluginExecutorError(error_msg)
            # Load entry-point.
            entry_point_class = entry_points[requested_entry_point].load()
            # Instantiate and run entry-point.
            class_instance = entry_point_class(
                self._release_entry, self._global_config, self._repository_dir
            )

            logger.info(
                format_minor("Executing %s with the argument: %s"),
                requested_entry_point,
                key_word_args,
            )

            if key_word_args is not None:
                class_instance.run(**key_word_args)
            else:
                class_instance.run()

    def _get_entry_point_dictionary(self, group: str) -> dict[str, importlib.metadata.EntryPoint]:
        """Returns all entrypoints for the given string in a dictionary.

        Args:
            group: group of entry points.
        Returns:
            a dictionary of all installed entry-points.
        """
        entry_pts = importlib.metadata.entry_points()[group]
        return {entry_point.name: entry_point for entry_point in entry_pts}

    def modify_release_branch(self):
        """Triggers the execution of all modification-plugins for the release-branch."""
        logger.info(format_sub_chapter("Modify Release Branch of '%s'"), self._release_entry.name)
        self._execute_plugins(
            MODIFICATION_ENTRYPOINT_GROUP,
            self._release_entry.plugins.release_modification,
        )

    def validate_release_branch(self):
        """Triggers the execution of all validation plugins for the release-branch."""
        logger.info(format_sub_chapter("Validate Release Branch of '%s'"), self._release_entry.name)

        self._execute_plugins(
            VALIDATION_ENTRYPOINT_GROUP,
            self._release_entry.plugins.release_validation,
        )

    def finalize_merge_back_branch(self):
        """Triggers the execution of all modification-plugins for the merge-back-branch."""
        logger.info(
            format_sub_chapter("Finalize Merge-Back Branch of '%s'"), self._release_entry.name
        )

        self._execute_plugins(
            MODIFICATION_ENTRYPOINT_GROUP,
            self._release_entry.plugins.merge_back_finalization,
        )
