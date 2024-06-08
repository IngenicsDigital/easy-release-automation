"""Tests for ChangelogVersionUpdaterPlugin

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pathlib

from easy_release_automation.core.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.plugins.modification.python_requirements import (
    requirements_updater_and_compiler,
)
from easy_release_automation.core import plugin_executor
from tests.plugins.fixtures.default_config import default_global_config, default_release_entry
from tests.plugins.utils import plugin_loader

ENTRY_POINT_NAME = "update_and_compile_requirements"

TOML_TEST_FILE = pathlib.Path(__file__).parent / "test_files/compile_pyproject.toml"


def test_requirements_updater_and_compiler__compile_toml_file(
    tmp_path: pathlib.Path,
    default_release_entry: ReleaseEntry,
    default_global_config: GlobalConfig,
):
    """Tests the generation of the requirement-files for a pyproject.toml.
    NOTE: it does not validate the output requirement-files. Only ensures their generation.
    NOTE: it does not test the requirements updates, as there are specific tests for the
    RequirementsUpdaterPlugin.
    """
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )

    # Define input toml
    toml_input = TOML_TEST_FILE.read_text()
    toml_file = tmp_path / "some_dir" / "pyproject.toml"
    toml_file.parent.mkdir()
    toml_file.write_text(toml_input)

    # Instantiate Class
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(
        plugin, requirements_updater_and_compiler.RequirementsUpdaterAndCompilerPlugin
    )
    # Run Plugin on requirements.txt
    plugin.run([str(toml_file.relative_to(tmp_path))])

    # Validate, if requirement-files were generated. Would raise an IterationStop exception, if not.
    next(toml_file.parent.glob("requirements.txt"))
    next(toml_file.parent.glob("requirements-test.txt"))


REQUIREMENTS_ENTRY = "pip==24.0"


def test_requirements_updater_and_compiler__compile_requirements_file(
    tmp_path: pathlib.Path,
    default_release_entry: ReleaseEntry,
    default_global_config: GlobalConfig,
):
    """Tests the generation of the requirement-files for a requirements.in.
    NOTE: it does not validate the output requirement-files. Only ensures their generation.
    NOTE: it does not test the requirements updates, as there are specific tests for the
    RequirementsUpdaterPlugin.
    """
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )

    # Define input requirements
    requirements_file = tmp_path / "some_dir" / "requirements.in"
    requirements_file.parent.mkdir()
    requirements_file.write_text(REQUIREMENTS_ENTRY)
    requirements_test_file = requirements_file.parent / "requirements-test.in"
    requirements_test_file.write_text(REQUIREMENTS_ENTRY)

    # Instantiate Class
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(
        plugin, requirements_updater_and_compiler.RequirementsUpdaterAndCompilerPlugin
    )
    # Run Plugin on requirements.txt
    plugin.run(
        [
            str(requirements_file.relative_to(tmp_path)),
            str(requirements_test_file.relative_to(tmp_path)),
        ]
    )

    # Validate, if requirement-files were generated. Would raise an IterationStop exception, if not.
    next(requirements_file.parent.glob("requirements.txt"))
    next(requirements_file.parent.glob("requirements-test.txt"))
