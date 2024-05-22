"""Tests for YamlUpdateV2Plugin

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pathlib

import deepdiff
import pytest
import yaml

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.plugins.modification.configuration_files import yaml_file_updater_v2
from easy_release_automation.utils import plugin_executor
from tests.plugins.fixtures.default_config import default_global_config, default_release_entry
from tests.plugins.utils import plugin_loader

ENTRY_POINT_NAME = "yaml_file_updater_v2"


@pytest.fixture
def yaml_update_v2_plugin(
    tmp_path: pathlib.Path, default_global_config: GlobalConfig, default_release_entry: ReleaseEntry
) -> yaml_file_updater_v2.YamlUpdateV2Plugin:
    """Loads the plugin from the entrypoints. Ensures, that the entrypoint is configured
    correctly."""
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(plugin, yaml_file_updater_v2.YamlUpdateV2Plugin)
    return plugin


def test_yaml_file_updater__no_file_exists(
    tmp_path: pathlib.Path, yaml_update_v2_plugin: yaml_file_updater_v2.YamlUpdateV2Plugin
):
    """Tests, if the yaml-file is generated as expected."""

    assert isinstance(yaml_update_v2_plugin, yaml_file_updater_v2.YamlUpdateV2Plugin)

    test_file = tmp_path / "test.yml"
    expected_output = {"a": {"b": 21}, "c": 1, "d": {"e": {"f": "test"}}}

    repository_dir = test_file.parent
    yaml_update_v2_plugin.run(str(test_file.relative_to(repository_dir)), expected_output)
    result = yaml.load(test_file.read_text(encoding="utf-8"), Loader=yaml.CLoader)
    assert not deepdiff.DeepDiff(expected_output, result)


def test_yaml_file_updater__file_exists(
    tmp_path: pathlib.Path,
    default_global_config: GlobalConfig,
    default_release_entry: ReleaseEntry,
):
    """Tests, if the configuration is integrated correctly for a yaml file and comments persist."""

    test_file = tmp_path / "test.yml"
    configuration = {"a": {"b": 0}, "c": 1, "d": {"e": {"e": "test"}}}
    initial_configuration = {"a": {"b": 21}, "d": {"e": {"f": "test"}}}
    expected_output = {"a": {"b": 0}, "c": 1, "d": {"e": {"f": "test", "e": "test"}}}

    test_file.write_text(
        "# this is a comment\n" + yaml.dump(initial_configuration) + "# this is a comment\n"
    )

    repository_dir = test_file.parent.parent
    plugin = yaml_file_updater_v2.YamlUpdateV2Plugin(
        default_release_entry, default_global_config, repository_dir
    )

    plugin.run(str(test_file.relative_to(repository_dir)), configuration)
    raw_text = test_file.read_text(encoding="utf-8")
    assert raw_text.count("# this is a comment") == 2
    result = yaml.load(raw_text, Loader=yaml.CLoader)
    assert not deepdiff.DeepDiff(expected_output, result, ignore_order=True)
