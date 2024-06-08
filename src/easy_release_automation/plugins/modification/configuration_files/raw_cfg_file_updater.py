"""Configuration Updater Plugin.

Description:
    Plugin that supports to update configuration files. Thereby, it receives a dictionary as
    parameter and updates the configuration file with the new configuration entries. Additionally,
    it preserves comments.

    NOTE: This Plugin is designed for a special use-case and has major constraints:
        - This plugin is written raw configuration files without sections.
        - Configuration files are not allowed to have comments within configuration
            lines and comments must be unique.
        For a more flexible approach consider using the RegexReplacerPlugin.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import configparser
import logging
import pathlib

from easy_release_automation.core.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.interfaces.modification_interface import ModificationInterface

logger = logging.getLogger(__name__)


class RAWCfgUpdaterPlugin(ModificationInterface):
    """Plugin that allows to update configuration files."""

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """Initializes the RAWCfgUpdaterPlugin"""
        self._release_entry = release_entry
        self._repository_dir = repository_dir

    def run(
        self, config_path_relative: str, configuration: dict[str, str], quoted_strings: bool = True
    ):
        """The run method updates the configuration file with the given entries in the
        configuration. It also supports to write new configuration files from scratch.

        Args:
            config_path_relative: path to the configuration file (relative to the repository).
            configuration: dictionary with all configuration parameters as key and configuration
                values as value.
            quoted_strings: if set True, updated string-values are quoted in the configuration file
                if set False, updated value strings do not have quotes.
        """
        logger.info(
            "Update Configuration file: %s, repository: %s",
            config_path_relative,
            self._release_entry.name,
        )

        config_path = self._prepare_configuration(config_path_relative)
        self._update_configuration(config_path, configuration, quoted_strings)

    def _prepare_configuration(self, config_path_relative: str) -> pathlib.Path:
        """Ensures that the configuration file exists. If it does not, it is generated.

        Args:
            config_path_relative: absolute path to the configuration file.
        Returns:
            a configuration path that is ensured to exist.
        """
        config_path = self._repository_dir / config_path_relative
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.touch(exist_ok=True)
        return config_path

    @classmethod
    def _update_configuration(
        cls, config_path: pathlib.Path, configuration: dict[str, str], quoted_strings: bool
    ):
        """Rewrites the new configuration file for the given path.

        Args:
            config_path: absolute path to the configuration file.
            configuration: dictionary with all configuration parameters as key and configuration
                values as value.
            quoted_strings: if set True, updated string-values are quoted in the configuration file
                if set False, updated value strings do not have quotes.
        """

        dummy_section = "dummy_section"

        config_handler = cls._get_configuration(config_path, dummy_section)

        for key, value in configuration.items():
            if quoted_strings and isinstance(value, str):
                value = f'"{value}"'
            if key in config_handler[dummy_section]:
                prev_value = config_handler[dummy_section][key].replace("\n", "")
                logger.info(
                    "Updating config parameter: %s from: %s to value: %s.", key, prev_value, value
                )
            else:
                logger.info("Introducing new parameter: %s with value: %s.", key, value)
            config_handler[dummy_section][key] = str(value)

        with config_path.open("w") as config_file:
            config_handler.write(config_file)

        cls._cleanup_section(config_path, dummy_section)

    @classmethod
    def _get_configuration(
        cls, config_path: pathlib.Path, dummy_section: str
    ) -> configparser.ConfigParser:
        """Parses the existing config file including existing comments.

        Args:
            config_path: absolute path to the configuration file.
            dummy_section: name of the dummy section.
        Returns:
            a configuration object
        """
        logger.info("Reading-in configuration file: %s", config_path)

        # NOTE: This approach of reading in files is not recommended, but works for the restricted
        # use-case of the plugin. The approach preserves unique comments in the configuration file
        # see: https://stackoverflow.com/a/52306763
        config = configparser.ConfigParser(allow_no_value=True, strict=False, comment_prefixes="/")
        config.optionxform = str  # type: ignore [assignment]
        config.read_string(f"[{dummy_section}]\n" + config_path.read_text())
        return config

    @classmethod
    def _cleanup_section(cls, config_path: pathlib.Path, dummy_section: str):
        """Cleans up the dummy-section in the configuration file.

        Args:
            config_path: absolute path to the configuration file.
            dummy_section: name of the dummy section to delete.
        """
        logger.debug(
            "Cleaning up the section: %s from configuration file %s.", dummy_section, config_path
        )
        with config_path.open("r") as config_file:
            lines = config_file.readlines()
            lines = [line for line in lines if dummy_section not in line]

        with config_path.open("w") as config_file:
            config_file.writelines(lines)
