"""Modification Interface

Description:
    Defines an interface for plugins, that modify a repository. During the release process these
    plugins can be used for:
    - the 'Repository-Modification'-step, which allows to modify the repository before the
      'Repository-Validation'-step.
    - the 'Merge-Back-Finalization'-step, which allows to modify the 'Merge-Back'-branch, that
      is merged back into the 'Main'-branch and does not affect the 'Stable-Branch'

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pathlib
from abc import ABCMeta, abstractmethod

from easy_release_automation.core.configuration import GlobalConfig, ReleaseEntry


class ModificationException(Exception):
    """Exception raised when errors during the modification-process occur."""


class ModificationInterface(metaclass=ABCMeta):
    @abstractmethod
    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """This method initializes the modification plugin. All common parameters for the repository
        are processed here.

        Args:
            release_entry: release entry of the repository to process.
            global_config: global configuration, that defines the configuration for all
                release-entries.
            repository_dir: directory of all cloned repositories.
        Raises:
            ModificationException: Raised on any error during repository-modification process.
        """
        raise NotImplementedError("The '__init__'-function must be implemented in Child-Class.")

    @abstractmethod
    def run(self, **kwargs):
        """This method is called by ERA to modify the repository.

        Args:
            kwargs: keyword-arguments, that are individual to the implemented method.
                NOTE: We will ignore the violation the Liskov Substitution Principle (LSP) in the
                child-implementations, as it allows for more flexibility and simplicity in the code.
        Raises:
            ModificationException: Raised on any error during repository-modification process.
        """
        raise NotImplementedError("The 'run'-function must be implemented by the Child-Class.")
