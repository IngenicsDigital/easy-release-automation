"""Tests for PluginExecutor

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pytest
import pathlib
from easy_release_automation.core.configuration import PluginEntries
from easy_release_automation.core.plugin_executor import PluginExecutor, PluginExecutorError
from ..fixtures.default_config import default_release_entry, default_global_config


def test_plugin_executor_non_existing_plugin(
    tmp_path: pathlib.Path, default_release_entry, default_global_config
):
    """Validates, that PluginExecutorError is risen on non existing plugin."""
    plugin_executor = PluginExecutor(default_release_entry, default_global_config, tmp_path)
    default_release_entry.plugins = PluginEntries(
        release_modification=[],
        release_validation=[{"non-existing-plugin": []}],
        merge_back_finalization=[],
    )
    with pytest.raises(PluginExecutorError):
        plugin_executor.validate_release_branch()


def test_plugin_executor_existing_plugin(
    mocker, tmp_path: pathlib.Path, default_release_entry, default_global_config
):
    """Validates, that an existing plugin is executed with the correct keyword-arguments.
    Thereby, it utilizes the ShellValidationPlugin, and validates, if the expected command
    is called.

    NOTE: This test has a dependency on the ShellValidationPlugin. In the future, it
    might be desireable to remove this dependency, and use dynamically generated plugins in the
    test. Related Issue: https://github.com/IngenicsDigital/easy-release-automation/issues/3
    """
    plugin_executor = PluginExecutor(default_release_entry, default_global_config, tmp_path)
    command = ["ls"]
    default_release_entry.plugins = PluginEntries(
        release_modification=[],
        release_validation=[{"validate_via_shell": {"command": command}}],
        merge_back_finalization=[],
    )
    subprocess_mock = mocker.patch(
        "easy_release_automation.plugins.validation.shell_validator.subprocess"
    )
    popen_instance = mocker.MagicMock()
    subprocess_mock.Popen.return_value = popen_instance
    # Avoid polling
    popen_instance.poll.return_value = 0
    # Imitate a successful call
    popen_instance.returncode = 0

    # Execute call
    plugin_executor.validate_release_branch()

    # Validate a correct call
    assert subprocess_mock.Popen.call_count == 1
    assert subprocess_mock.Popen.call_args[0] == (command,)
