"""Tests for RAWCfgUpdatePlugin

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import importlib.metadata
import pathlib

import pytest

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.plugins.modification.configuration_files import raw_cfg_file_updater
from easy_release_automation.utils import plugin_executor
from tests.plugins.fixtures.default_config import default_global_config, default_release_entry
from tests.plugins.utils import plugin_loader

ENTRY_POINT_NAME = "cfg_file_updater"


@pytest.fixture
def cfg_file_updater_plugin(
    tmp_path: pathlib.Path, default_global_config: GlobalConfig, default_release_entry: ReleaseEntry
) -> raw_cfg_file_updater.RAWCfgUpdaterPlugin:
    """Loads the plugin from the entrypoints. Ensures, that the entrypoint is configured
    correctly."""
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(plugin, raw_cfg_file_updater.RAWCfgUpdaterPlugin)
    return plugin


def test_cfg_file_updater__file_exists(
    tmp_path: pathlib.Path, cfg_file_updater_plugin: raw_cfg_file_updater.RAWCfgUpdaterPlugin
):
    """Tests, if the cfg-file is updated as expected."""

    test_file = tmp_path / "test.yml"

    config_content = """
    # Here is a comment A
    CONFIG_PARAM_A = "123"
    # Here is a comment B
    CONFIG_PARAM_B = "Hallo"
    ; Here is a comment C
    """

    configuration = {"CONFIG_PARAM_A": "test", "CONFIG_PARAM_B": 21}
    expected_output = """
    # Here is a comment A
    CONFIG_PARAM_A = "test"
    # Here is a comment B
    CONFIG_PARAM_B = 21
    ; Here is a comment C
    """
    test_file.write_text(config_content)
    repository_dir = test_file.parent

    cfg_file_updater_plugin.run(str(test_file.relative_to(repository_dir)), configuration, True)
    result = test_file.read_text(encoding="utf-8")
    # Ignore spaces
    assert result.replace(" ", "").strip() == expected_output.replace(" ", "").strip()
