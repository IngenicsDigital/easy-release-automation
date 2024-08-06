"""Configuration Handling

Description:
    Reads a Yaml-Configuration for the given path, and converts the yaml-configuration into
    dataclasses. The configuration dataclasses are:
    - GlobalConfig: Global configuration that is available for all Release-Entries.
    - PublicReleaseEntry: public configuration of a single release entry that can be accessed by
        other release-entries.
    - PrivateReleaseEntry: private configuration of a single release entry that can be accessed
        solely by the release entry its self.
    - Plugins: plugins defined for a single release entry.
    - ReleaseEntry: containing the full configuration of a release entry:
        name, PublicReleaseEntry, PrivateReleaseEntry, Plugins
    Additionally, release-entries are sorted topologically with respect to their dependencies.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import inspect
import logging
import pathlib
from dataclasses import dataclass, field
from typing import Any, Optional

from easy_release_automation.core.utils.yaml_handler import YamlHandler
import graphlib

logger = logging.getLogger(__name__)


DEPENDENCY_KEY = "dependencies"
PLUGINS_KEY = "plugins"
REPOSITORY_NAME_KEY = "name"


class DictInitializedDataclass:
    """Allows to initialize a dataclass from a dictionary that contains more keys than the
    dataclass.
    """

    @classmethod
    def from_dict(cls, parameters: dict[str, Any]):
        filtered_dict = {
            k: v for k, v in parameters.items() if k in inspect.signature(cls).parameters
        }
        return cls(**filtered_dict)


@dataclass
class GlobalConfig(DictInitializedDataclass):
    """Declares the global Configuration of the app.

    Args:
        git_user_name: user-name that is used to, e.g., clone, or tag the git repository or
            commit and push changes.
        git_user_email: user-emails that is used to '''
        tag_policy: global tag policy (can be overwritten by local tag policy) if set to
            - 'skip': repositories that already contain the tag are skipped for the release process.
            - 'ovr': if the tag is already existing in the corresponding repository, the old tag is
                overwritten.
        test_run: if set to True, changes and commits are only executed locally and not pushed into
            the remote repository.
    """

    git_user_name: str
    git_user_email: str
    tag_policy: str = "skip"
    test_run: bool = False


@dataclass
class PublicReleaseEntry(DictInitializedDataclass):
    """Declares the Release-Entry properties that are publicly available to other Release-Entries if
    they are dependent on this entry.

    Args:
        version: Version/Tag of the Release-Entry
        main_branch: Defines the working branch.
        stable_branch: Defines the branch that is tagged.
        url: URL where to clone the repository. Note: Currently only HTTPS urls are
            supported for the docker version.
    """

    name: str
    url: str
    version: Optional[str] = None
    main_branch: str = "main"
    stable_branch: str = "stable"


@dataclass
class PrivateReleaseEntry(DictInitializedDataclass):
    """Declares the private Release-Entry properties that are solely available for this
    Release-Entry.

    Args:
        tag_message: message with for the tag.
        tag_policy: (overwrites the global tag policy) if set to
            - 'skip': if the tag already exists, the release process is skipped.
            - 'ovr': if the tag already exists, the old tag is overwritten.
        meta_data: any information that should be available for all plugins of this release-entry.
        dependencies: dict of public properties of other repositories, on which the plugin is
            dependent.
        skip_release: allows to define a release entry without executing the release-process for it.
    """

    tag_message: str = ""
    tag_policy: Optional[str] = None
    meta_data: Any = None
    dependencies: dict[str, PublicReleaseEntry] = field(default_factory=lambda: {})
    should_skip: bool = False


@dataclass
class PluginEntries(DictInitializedDataclass):
    """Declares the frame-structure containers for the plugins.

    NOTE: New framework containers for plugins are introduced, they are assumed to have a default
    plugin or an empty dictionary {}.

    Args:
        release_modification: container for plugins modifying the release-branch.
        release_validation: container for plugins modifying the release-branch.
        merge_back_finalization: container for plugins finalizing the merge-back-branch. This allows
            to prepare for merging back into the main branch, e.g., adapting the changelog.
    """

    release_modification: list[dict[str, Optional[dict]]] = field(default_factory=lambda: [])
    release_validation: list[dict[str, Optional[dict]]] = field(default_factory=lambda: [])
    merge_back_finalization: list[dict[str, Optional[dict]]] = field(default_factory=lambda: [])


@dataclass
class ReleaseEntry:
    name: str
    public: PublicReleaseEntry
    private: PrivateReleaseEntry
    plugins: PluginEntries


class ConfigurationHandlerException(Exception):
    """Exception that is raised during this release"""


def get_configuration(
    configuration_path: pathlib.Path,
    test_run: Optional[bool],
    author: Optional[str],
    email: Optional[str],
    global_tag_policy: Optional[str],
) -> tuple[GlobalConfig, list[ReleaseEntry]]:
    """Reads in the given configuration and conditionally overrides them with the given parameters.

    Args:
        configuration_path: path to the configuration
        test_run: if the release should be tested or not
        author: author of the release
        email: email of the release author
        global_tag_policy: global tag-policy
    """
    global_config, release_entries = get_file_configuration(configuration_path)

    if test_run is not None:
        global_config.test_run = test_run
    if global_tag_policy is not None:
        global_config.tag_policy = global_tag_policy
    if email is not None:
        global_config.git_user_email = email
    if author is not None:
        global_config.git_user_name = author

    return global_config, release_entries


def get_file_configuration(path: pathlib.Path) -> tuple[GlobalConfig, list[ReleaseEntry]]:
    """Returns the configuration that specifies.

    Returns:
        - Global configuration entry.
        - List of dependency-sorted release entries.
    """

    config = YamlHandler.get_config(str(path))
    global_config = GlobalConfig.from_dict(config["global_config"])
    release_entries = build_release_entries(config["repositories"])

    return global_config, topological_sort(release_entries)


def build_release_entries(release_entries_raw: dict) -> list[ReleaseEntry]:
    """Takes the raw release-entries and converts them into a list of the ReleaseEntry
    data-structures.

    Args:
        release_entries_raw: raw structure of release-entries given by the configuration file.
    Returns:
        a list of unsorted release-entries.
    """

    # add name_key
    for key in release_entries_raw:
        release_entries_raw[key][REPOSITORY_NAME_KEY] = key

    # Read-In Public Release Entries
    public_entries = {
        key: PublicReleaseEntry.from_dict(values) for key, values in release_entries_raw.items()
    }

    release_entries = []
    for key, entry in release_entries_raw.items():

        # Read-In Plugins
        plugin_entries = (
            release_entries_raw[key].pop(PLUGINS_KEY)
            if PLUGINS_KEY in entry and entry[PLUGINS_KEY] is not None
            else {}
        )
        plugins = PluginEntries.from_dict(plugin_entries)

        # Update dependencies to public-entries
        if DEPENDENCY_KEY in release_entries_raw[key]:
            try:
                entry[DEPENDENCY_KEY] = {dep: public_entries[dep] for dep in entry[DEPENDENCY_KEY]}
            except KeyError as error:
                raise ConfigurationHandlerException(
                    f"Missing dependency keys for repository: {public_entries[key].name}. Please "
                    "add all dependencies to the release-configuration YAML."
                ) from error

        # Read-In Private Release Entries
        private = PrivateReleaseEntry.from_dict(entry)

        release_entries.append(ReleaseEntry(key, public_entries[key], private, plugins))

    return release_entries


def topological_sort(release_entries: list[ReleaseEntry]) -> list[ReleaseEntry]:
    """Implementation similar to Khans-Algorithm.

    NOTE: Two repositories are not allowed to depend on each other.

    Args:
        release_entries: list of unsorted release-entries.
    Returns:
        list of dependency-sorted release-entries.
    """

    graph = {}
    release_entry_lut = {}
    for release_entry in release_entries:
        graph[release_entry.name] = set(
            [elem.name for elem in release_entry.private.dependencies.values()]
        )
        release_entry_lut[release_entry.name] = release_entry
    sorted_entry_names = graphlib.TopologicalSorter(graph).static_order()
    try:
        sorted_entries = [release_entry_lut[name] for name in sorted_entry_names]
    except graphlib.CycleError as error:
        raise ConfigurationHandlerException(
            f"Failed to perform topological sort due to error: {str(error)}"
            "NOTE: No circular relations allowed."
        ) from error
    logger.info("Successfully sorted release-entries: %s", sorted_entry_names)

    return sorted_entries
