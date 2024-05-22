"""Validation Interface

Description:
    Defines an interface for plugins, that validate a repository. During the release process these
    plugins can be used for:
    - the 'Repository-Validation'-step, which allows to validate the repository, before merging the
      release-branch back to the stable-branch.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pathlib
from abc import ABCMeta, abstractmethod

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry


class ValidationException(Exception):
    """Exception raised when errors during the validation-process occur."""


class ValidationInterface(metaclass=ABCMeta):
    @abstractmethod
    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """This method initializes the validation plugin. All common parameters for the repository
        are processed here.

        Args:
            release_entry: release entry of the repository to process.
            global_config: global configuration, that defines the configuration for all
                release-entries.
            repository_dir: directory of all cloned repositories.
        Raises:
            ValidationException: Explains any error during repository-finalization process.
        """
        raise NotImplementedError("Deriving a subclass is required")

    @abstractmethod
    def run(self, **kwargs):
        """This method is called by ERA to validate the repository.

        Args:
            kwargs: keyword-arguments, that are individual to the implemented method.
                NOTE: We will ignore the violation the Liskov Substitution Principle (LSP) in the
                child-implementations, as it allows for more flexibility and simplicity in the code.
        Raises:
            ValidationException: Explains any error during release-validation process.
        """
        raise NotImplementedError("Deriving a subclass is required")
