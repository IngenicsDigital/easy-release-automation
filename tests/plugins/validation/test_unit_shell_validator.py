"""Tests for ShellValidationPlugin

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pathlib

import pytest
from pytest_mock import MockFixture

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.interfaces.validation_interface import ValidationException
from easy_release_automation.plugins.validation import shell_validator
from easy_release_automation.utils import plugin_executor
from tests.plugins.utils import plugin_loader

from ..fixtures.default_config import default_global_config, default_release_entry

ENTRY_POINT_NAME = "validate_via_shell"


@pytest.fixture
def validate_via_shell_plugin(
    tmp_path: pathlib.Path, default_global_config: GlobalConfig, default_release_entry: ReleaseEntry
) -> shell_validator.ShellValidationPlugin:
    """Loads the plugin from the entrypoints. Ensures, that the entrypoint is configured
    correctly."""
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.VALIDATION_ENTRYPOINT_GROUP
    )
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(plugin, shell_validator.ShellValidationPlugin)
    return plugin


@pytest.fixture
def subprocess_mock(mocker: MockFixture):
    return mocker.patch("easy_release_automation.plugins.validation.shell_validator.subprocess")


@pytest.mark.parametrize("return_code", [0, -1])
def test_successful_and_failed_subprocess(
    mocker: MockFixture,
    tmp_path: pathlib.Path,
    validate_via_shell_plugin: shell_validator.ShellValidationPlugin,
    return_code: int,
    subprocess_mock,
):
    """Tests,
    - if the subprocess raises an ValidationException, when subprocess has !=0 returncode
    - if the subprocess runs through, when subprocess returns 0
    """

    process_return_mock = mocker.MagicMock()
    subprocess_mock.Popen.return_value = process_return_mock
    process_return_mock.poll.return_value = 1  # skip prints
    process_return_mock.returncode = return_code
    command = ["ls", "-la"]

    if return_code == 0:
        validate_via_shell_plugin.run(command)
    else:
        with pytest.raises(ValidationException):
            validate_via_shell_plugin.run(command)
    subprocess_mock.Popen.assert_called_once_with(
        command, stdout=subprocess_mock.PIPE, cwd=tmp_path
    )
