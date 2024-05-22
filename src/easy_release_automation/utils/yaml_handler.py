"""Yaml-Reader

Description:
    Reads a yaml for a given path, or if an environment variable is set, the Yaml-Reader reads the
    path of the environment variable.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import yaml

COMP_NAME = "YamlHandler"

logger = logging.getLogger(__name__)


class InvalidConfPathError(Exception):
    """Exception Class for cases where the configuration-path is invalid"""


class YamlHandler:
    @classmethod
    def get_config(cls, default_path: str, env_variable_name: Optional[str] = None) -> dict:
        """Returns the yaml-content.

        Firstly, the function checks if the environment-variable is set for a custom file-path.
        If so, the file is read from the path given in the environment-variable.

        If environment variable is not set, the function reads the config from the standard
        location.

        Returns:
            yaml-content.
        """

        # Function os.getenv returns env-var if defined else the default value
        conf_path = (
            os.getenv(env_variable_name, default=default_path)
            if env_variable_name is not None
            else default_path
        )

        logger.info("Used File-Path: %s, default-path: %s", conf_path, default_path)

        return cls._read_config(conf_path)

    @classmethod
    def _read_config(cls, path: str) -> dict:
        """Reads the yaml-file for the given path. Includes error handling if file-path is invalid.

        Params:
            path: path to the yaml-file.
        Returns:
            Configuration dictionary.
        Raises:
            InvalidConfPathError if file-path is invalid
        """
        if not os.path.isfile(path):
            error_msg = f"YamlHandler: No yaml-file found. Path: {path}"
            raise InvalidConfPathError(error_msg)

        with open(path, "r", encoding="utf-8") as config_stream:
            try:
                config = yaml.safe_load(config_stream)
            except yaml.YAMLError as error:
                error_msg = (
                    f"YamlHandler: - Unable to read Yaml file {path}. Potentially corrupted Yaml."
                )
                raise InvalidConfPathError(error_msg) from error

        return config
