"""YAML Update Plugin V2.

Description:
    Plugin that supports to update yaml files. Thereby, it receives a dictionary as parameter and
    updates the configuration file with the new configuration entries.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import logging
import pathlib

import ruamel.yaml
from pydantic.v1.utils import deep_update

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.interfaces.modification_interface import ModificationInterface

logger = logging.getLogger(__name__)


class YamlUpdateV2Plugin(ModificationInterface):
    """Plugin that allows to update configuration files."""

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """Initializes the YamlUpdateV2Plugin."""
        self._release_entry = release_entry
        self._repository_dir = repository_dir

    def run(self, file_path_relative: str, configuration: dict):
        """The run method updates the yaml-file with the given entries in the configuration. It also
        supports to write new configuration files from scratch.

        Args:
            file_path_relative: path to the configuration file (relative to the repository).
            configuration: dictionary with all configuration parameters as key and configuration
                values as value.
        """
        logger.info(
            "Update Configuration file: %s, repository: %s",
            file_path_relative,
            self._release_entry.name,
        )

        file_path = self._repository_dir / file_path_relative
        self._prepare_yaml(file_path)
        self._update_yaml(file_path, configuration)

    def _prepare_yaml(self, file_path: pathlib.Path) -> pathlib.Path:
        """Ensures that the yaml file exists. If it does not, it is generated.

        Args:
            file_path: absolute path to the configuration file.
        Returns:
            a configuration path that is ensured to exist.
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch(exist_ok=True)
        return file_path

    def _update_yaml(self, config_path: pathlib.Path, configuration: dict):
        """Rewrites the yaml file at the given path.

        Args:
            config_path: absolute path to the configuration file.
            configuration: the dictionary, with which the existing dictionary is updated.
        """
        yaml = ruamel.yaml.YAML()
        with config_path.open("r") as yaml_file:
            yaml_string = yaml_file.read()
        existing_config = yaml.load(yaml_string)
        existing_config = existing_config if existing_config is not None else {}

        logger.debug("Existing Configuration: \n%s\n", existing_config)
        existing_config = deep_update(existing_config, configuration)

        with config_path.open("w") as yaml_file:
            yaml.dump(existing_config, yaml_file)
