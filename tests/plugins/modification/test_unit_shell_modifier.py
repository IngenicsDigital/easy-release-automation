"""Tests for ShellModificationPlugin

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pathlib

import pytest
from pytest_mock import MockFixture

from easy_release_automation.core.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.interfaces.modification_interface import ModificationException
from easy_release_automation.plugins.modification import shell_modifier
from easy_release_automation.core import plugin_executor
from tests.plugins.utils import plugin_loader

from ..fixtures.default_config import default_global_config, default_release_entry

ENTRY_POINT_NAME = "modify_via_shell"


@pytest.fixture
def modify_via_shell_plugin(
    tmp_path: pathlib.Path, default_global_config: GlobalConfig, default_release_entry: ReleaseEntry
) -> shell_modifier.ShellModificationPlugin:
    """Loads the plugin from the entrypoints. Ensures, that the entrypoint is configured
    correctly."""
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(plugin, shell_modifier.ShellModificationPlugin)
    return plugin


@pytest.fixture
def subprocess_mock(mocker: MockFixture):
    return mocker.patch("easy_release_automation.plugins.modification.shell_modifier.subprocess")


@pytest.mark.parametrize("return_code", [0, -1])
def test_shell_modifier__successful_and_failed_subprocess(
    tmp_path: pathlib.Path,
    mocker: MockFixture,
    return_code: int,
    modify_via_shell_plugin: shell_modifier.ShellModificationPlugin,
    subprocess_mock,
):
    """Tests, if the subprocess
    - raises an ModificationException, when subprocess has !=0 returncode.
    - runs through, when subprocess has a ==0 returncode.
    - is called with the expected parameters.
    """

    process_return_mock = mocker.MagicMock()
    subprocess_mock.Popen.return_value = process_return_mock
    process_return_mock.poll.return_value = 1  # skip prints
    process_return_mock.returncode = return_code
    command = ["ls", "-la"]

    if return_code == 0:
        modify_via_shell_plugin.run(command)
    else:
        with pytest.raises(ModificationException):
            modify_via_shell_plugin.run(command)
    subprocess_mock.Popen.assert_called_once_with(
        command, stdout=subprocess_mock.PIPE, cwd=tmp_path
    )
