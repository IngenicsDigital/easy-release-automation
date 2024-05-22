"""Tests for ChangelogVersionUpdaterPlugin

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pathlib

import pytest

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.plugins.modification.changelog import changelog_version_updater
from easy_release_automation.utils import plugin_executor
from tests.plugins.fixtures.default_config import default_global_config, default_release_entry
from tests.plugins.utils import plugin_loader

CHANGELOG_HEADER = """
# Changelog

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

"""

CHANGELOG_RELEASE_ENTRY = """

[1.2.3] - 2024-04-29

### Added

"""


CHANGELOG_UNRELEASED_ENTRY = """

## [Unreleased]

### Added

"""

ENTRY_POINT_NAME = "changelog_version_updater"


@pytest.fixture
def changelog_version_updater_plugin(
    tmp_path: pathlib.Path, default_global_config: GlobalConfig, default_release_entry: ReleaseEntry
) -> changelog_version_updater.ChangelogVersionUpdaterPlugin:
    """Loads the plugin from the entrypoints. Ensures, that the entrypoint is configured
    correctly."""
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(plugin, changelog_version_updater.ChangelogVersionUpdaterPlugin)
    return plugin


def test_changelog_version_updater__changelog_is_unreleased(
    tmp_path: pathlib.Path,
    changelog_version_updater_plugin: changelog_version_updater.ChangelogVersionUpdaterPlugin,
):
    """Tests, if the [Unreleased] section is replaced with the release entry."""

    test_file = tmp_path / "test.yml"

    changelog_content = CHANGELOG_HEADER + CHANGELOG_UNRELEASED_ENTRY + CHANGELOG_RELEASE_ENTRY

    test_file.write_text(changelog_content)
    repository_dir = test_file.parent
    changelog_version_updater_plugin.run(
        str(test_file.relative_to(repository_dir)), version="1.2.3"
    )
    result = test_file.read_text(encoding="utf-8")

    assert CHANGELOG_UNRELEASED_ENTRY not in result
    assert "## [1.2.3] - " in result
