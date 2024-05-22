"""Tests for RequirementsUpdaterPlugin

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pathlib

import pytest

from easy_release_automation.configuration import GlobalConfig, PublicReleaseEntry, ReleaseEntry
from easy_release_automation.plugins.modification.python_requirements import requirements_updater
from easy_release_automation.utils import plugin_executor
from tests.plugins.fixtures.default_config import default_global_config, default_release_entry
from tests.plugins.utils import plugin_loader

ENTRY_POINT_NAME = "update_requirements"

DEP_REPO_1 = PublicReleaseEntry("my-dep-repo-1", "github.com/my-org/my-dep-repo-1", "v1.2.1")
DEP_REPO_2 = PublicReleaseEntry("my-dep-repo-2", "github.com/my-org/my-dep-repo-2", "12.1.2")

REQ_FILE = """# some comment
%s # some comment
# some comment
some-independent-repo==0.23.4 # some comment
"""
REQ_FILE_2_DEP = """# some comment
%s # some comment
# some comment
some-independent-repo==0.23.4 # some comment
%s # some comment
"""


@pytest.mark.parametrize(
    "input_content, output_content",
    [
        (  # Using HTTPS protocol identifier
            REQ_FILE.format(f"{DEP_REPO_1.name} @ git+https://{DEP_REPO_1.url}@v2.34.63"),
            REQ_FILE.format(
                f"{DEP_REPO_1.name} @ git+https://{DEP_REPO_1.url}@{DEP_REPO_1.version}"
            ),
        ),
        (  # Version pinning with repository @
            REQ_FILE.format(f"{DEP_REPO_1.name} @ git+ssh://{DEP_REPO_1.url}@v2.34.63"),
            REQ_FILE.format(f"{DEP_REPO_1.name} @ git+ssh://{DEP_REPO_1.url}@{DEP_REPO_1.version}"),
        ),
        (  # Branch reference with repository @
            REQ_FILE.format(f"{DEP_REPO_1.name} @ git+ssh://{DEP_REPO_1.url}@my_branch"),
            REQ_FILE.format(f"{DEP_REPO_1.name} @ git+ssh://{DEP_REPO_1.url}@{DEP_REPO_1.version}"),
        ),
        (  # No pinning with repository @
            REQ_FILE.format(f"{DEP_REPO_1.name} @ git+ssh://{DEP_REPO_1.url}"),
            REQ_FILE.format(f"{DEP_REPO_1.name} @ git+ssh://{DEP_REPO_1.url}@{DEP_REPO_1.version}"),
        ),
        (  # Version pinning without repository @
            REQ_FILE.format(f"git+ssh://{DEP_REPO_1.name}@2.1.3"),
            REQ_FILE.format(f"git+ssh://{DEP_REPO_1.name}@{DEP_REPO_1.version}"),
        ),
        (  # Branch reference without repository @
            REQ_FILE.format(f"git+ssh://{DEP_REPO_1.name}@my_branch"),
            REQ_FILE.format(f"git+ssh://{DEP_REPO_1.name}@{DEP_REPO_1.version}"),
        ),
        (  # No pinning without repository @
            REQ_FILE.format(f"git+ssh://{DEP_REPO_1.name}"),
            REQ_FILE.format(f"git+ssh://{DEP_REPO_1.name}@{DEP_REPO_1.version}"),
        ),
    ],
)
def test_requirements_updater__requirements_file_different_variations(
    tmp_path: pathlib.Path,
    output_content: str,
    input_content: str,
    default_release_entry: ReleaseEntry,
    default_global_config: GlobalConfig,
):
    """Tests different variations of requirement entries."""
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    requirements_file = tmp_path / "some_dir" / "my-requirements.in"
    requirements_file.parent.mkdir()
    requirements_file.write_text(input_content)

    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    # Add dependencies
    default_release_entry.private.dependencies[DEP_REPO_1.name] = DEP_REPO_1

    # Instantiate Class
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(plugin, requirements_updater.RequirementsUpdaterPlugin)

    # Run Plugin on requirements.txt
    plugin.run([str(requirements_file.relative_to(tmp_path))])
    assert output_content == requirements_file.read_text()


def test_requirements_updater__requirements_file_two_dependencies(
    tmp_path: pathlib.Path,
    default_release_entry: ReleaseEntry,
    default_global_config: GlobalConfig,
):
    """Tests the behavior on multiple requirement entries in a requirements.txt file."""
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    requirements_file = tmp_path / "some_dir" / "my-requirements.in"
    requirements_file.parent.mkdir()

    input_content = REQ_FILE_2_DEP.format(f"git+{DEP_REPO_1.name}@2.1.3", f"git+{DEP_REPO_1.name}")
    output_content = REQ_FILE_2_DEP.format(
        f"git+{DEP_REPO_1.name}@{DEP_REPO_1.version}", f"git+{DEP_REPO_2.name}@{DEP_REPO_2.version}"
    )
    requirements_file.write_text(input_content)

    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    # Add dependencies
    default_release_entry.private.dependencies[DEP_REPO_1.name] = DEP_REPO_1
    default_release_entry.private.dependencies[DEP_REPO_2.name] = DEP_REPO_2

    # Instantiate Class
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(plugin, requirements_updater.RequirementsUpdaterPlugin)

    # Run Plugin on requirements.txt
    plugin.run([str(requirements_file.relative_to(tmp_path))])
    assert output_content == requirements_file.read_text()


TOML_REQUIREMENT_1 = f"{DEP_REPO_1.name} @ git+{DEP_REPO_1.url}@{DEP_REPO_1.version}"


TOML_TEST_FILE = pathlib.Path(__file__).parent / "test_files/requirement_update_pyproject.toml"


@pytest.mark.parametrize(
    "main_dep_before, main_dep_after, opt_dep_before, opt_dep_after",
    [
        (  # Version reference beforehand
            f"{DEP_REPO_1.name} @ git+{DEP_REPO_1.url}@v2.34.63",
            f"{DEP_REPO_1.name} @ git+{DEP_REPO_1.url}@{DEP_REPO_1.version}",
            f"git+{DEP_REPO_2.url}@v2.34.63",
            f"git+{DEP_REPO_2.url}@{DEP_REPO_2.version}",
        ),
        (  # Branch reference beforehand
            f"{DEP_REPO_1.name} @ git+{DEP_REPO_1.url}@my_branch",
            f"{DEP_REPO_1.name} @ git+{DEP_REPO_1.url}@{DEP_REPO_1.version}",
            f"git+{DEP_REPO_2.url}@my_branch",
            f"git+{DEP_REPO_2.url}@{DEP_REPO_2.version}",
        ),
        (  # No pinning beforehand
            f"{DEP_REPO_1.name} @ git+{DEP_REPO_1.url}",
            f"{DEP_REPO_1.name} @ git+{DEP_REPO_1.url}@{DEP_REPO_1.version}",
            f"git+{DEP_REPO_2.url}",
            f"git+{DEP_REPO_2.url}@{DEP_REPO_2.version}",
        ),
    ],
)
def test_requirements_updater__toml_file_two_dependencies(
    tmp_path: pathlib.Path,
    default_release_entry: ReleaseEntry,
    default_global_config: GlobalConfig,
    main_dep_before: str,
    main_dep_after: str,
    opt_dep_before: str,
    opt_dep_after: str,
):
    """Tests the behavior on multiple requirement entries in a toml-file."""
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )

    # Define input toml
    toml_input = TOML_TEST_FILE.read_text()
    toml_input = toml_input.replace("{ OPTIONAL-TEST-DEPENDENCY }", opt_dep_before)
    toml_input = toml_input.replace("{ MAIN-DEPENDENCY }", main_dep_before)
    toml_file = tmp_path / "some_dir" / "my-requirements.toml"
    toml_file.parent.mkdir()
    toml_file.write_text(toml_input)
    # Define output toml
    toml_output = TOML_TEST_FILE.read_text()
    toml_output = toml_output.replace("{ OPTIONAL-TEST-DEPENDENCY }", opt_dep_after)
    toml_output = toml_output.replace("{ MAIN-DEPENDENCY }", main_dep_after)

    # Add dependencies
    default_release_entry.private.dependencies[DEP_REPO_1.name] = DEP_REPO_1
    default_release_entry.private.dependencies[DEP_REPO_2.name] = DEP_REPO_2
    # Instantiate Class
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(plugin, requirements_updater.RequirementsUpdaterPlugin)
    # Run Plugin on requirements.txt
    plugin.run([str(toml_file.relative_to(tmp_path))])

    # Validate
    assert toml_output == toml_file.read_text()
