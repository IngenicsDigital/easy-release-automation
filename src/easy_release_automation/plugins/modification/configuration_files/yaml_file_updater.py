"""YAML Update Plugin.

Description:
    Plugin that supports to update yaml files. Thereby, it receives a dictionary as parameter and
    updates the configuration file with the new configuration entries.

    NOTE: This plugin is constrained to YAML files, where the keys do not contain the '/'-character.
        We recommend using YamlUpdateV2Plugin, for a more generic approach.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import logging
import pathlib
from typing import Any

import ruamel.yaml

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.interfaces.modification_interface import ModificationInterface

logger = logging.getLogger(__name__)


class YamlUpdaterPlugin(ModificationInterface):
    """Plugin that allows to update configuration files."""

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """Initializes the YamlUpdaterPlugin."""
        self._release_entry = release_entry
        self._repository_dir = repository_dir

    def run(self, file_path_relative: str, configuration: dict[str, str]):
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

    def _update_yaml(self, config_path: pathlib.Path, configuration: dict[str, str]):
        """Rewrites the yaml file at the given path.

        Args:
            config_path: absolute path to the configuration file.
            configuration: dictionary with all configuration parameters as key and configuration
                values as value. e.g., {"key1/key2/key3": new_val_1, "key1/key3": new_val_2, ...}
        """
        yaml = ruamel.yaml.YAML()
        with config_path.open("r") as yaml_file:
            yaml_string = yaml_file.read()
        existing_config = yaml.load(yaml_string)
        existing_config = existing_config if existing_config is not None else {}

        logger.debug("Existing Configuration: \n%s\n", existing_config)
        for parameter_path, value in configuration.items():
            self._update_value(parameter_path, value, existing_config)

        with config_path.open("w") as yaml_file:
            yaml.dump(existing_config, yaml_file)

    @classmethod
    def _update_value(cls, parameter_path: str, value: Any, existing_configuration: dict):
        """Updates a single Value for the given parameter path

        Args:
            parameter_path: path to the yaml parameter
            value: the value to which the parameter should be updated
            existing_configuration: dictionary of the existing configuration.
        """
        logger.debug("Updating: %s to value %s", parameter_path, value)

        config_branch = existing_configuration
        path_elements = parameter_path.split("/")
        for parameter_key in path_elements[:-1]:
            if parameter_key not in config_branch:
                config_branch[parameter_key] = {}
            config_branch = config_branch[parameter_key]
        config_branch[path_elements[-1]] = value
