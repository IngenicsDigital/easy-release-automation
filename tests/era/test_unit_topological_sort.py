"""Tests for release-config.yml

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pathlib

import pytest

from easy_release_automation.core import configuration


def test_topological_sort():
    """Tests, if ERA's topological sort orders the release-entries according to their repository
    dependencies."""
    current_directory = pathlib.Path(__file__).parent.resolve()
    configuration_path = current_directory / "configurations/test_config_default.yaml"

    _, release_entries = configuration.get_file_configuration(configuration_path)

    predicted_order = [entry.name for entry in release_entries]
    assert predicted_order.index("package_1") > predicted_order.index("package_2")
    assert predicted_order.index("package_1") > predicted_order.index("package_4")
    assert predicted_order.index("package_2") > predicted_order.index("package_3")


def test_error_on_bidirectional_relation():
    """Tests, if the ERA's topological sort raises an exception, if it detects a bidirectional
    relation."""

    current_directory = pathlib.Path(__file__).parent.resolve()
    configuration_path = current_directory / "configurations/test_config_circle_relation.yaml"

    with pytest.raises(configuration.ConfigurationHandlerException) as exc_info:
        configuration.get_file_configuration(configuration_path)
    # these asserts are identical; you can use either one
    assert "NOTE: No circular relations allowed." in exc_info.value.args[0]
