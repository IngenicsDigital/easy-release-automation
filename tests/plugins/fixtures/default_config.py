"""Pytest Fixtures for the default configuration

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pytest

from easy_release_automation.core.configuration import (
    GlobalConfig,
    PluginEntries,
    PrivateReleaseEntry,
    PublicReleaseEntry,
    ReleaseEntry,
)

DEFAULT_REPO_NAME = "my_repository"
DEFAULT_REPO_URL = "my_repo@github.com/my_repo"
DEFAULT_GIT_USER_NAME = "default_git_user"
DEFAULT_GIT_USER_NAME_EMAIL = "default_git_user@my_company.com"


@pytest.fixture
def default_release_entry() -> ReleaseEntry:
    """Fixture for the default release-entry configuration"""
    return ReleaseEntry(
        DEFAULT_REPO_NAME,
        PublicReleaseEntry(DEFAULT_REPO_NAME, DEFAULT_REPO_URL),
        PrivateReleaseEntry(),
        PluginEntries(),
    )


@pytest.fixture
def default_global_config() -> GlobalConfig:
    """Fixture for the default global configuration"""
    return GlobalConfig(DEFAULT_GIT_USER_NAME, DEFAULT_GIT_USER_NAME_EMAIL)
