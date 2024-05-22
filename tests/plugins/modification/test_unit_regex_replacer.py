"""Tests for RegexReplacerPlugin

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import pathlib
from typing import Union

import pytest

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry
from easy_release_automation.plugins.modification import regex_replacer
from easy_release_automation.utils import plugin_executor
from tests.plugins.utils import plugin_loader

from ..fixtures.default_config import default_global_config, default_release_entry

ENTRY_POINT_NAME = "regex_replacer"


@pytest.fixture
def regex_replacer_plugin(
    tmp_path: pathlib.Path, default_global_config: GlobalConfig, default_release_entry: ReleaseEntry
) -> regex_replacer.RegexReplacerPlugin:
    """Loads the plugin from the entrypoints. Ensures, that the entrypoint is configured
    correctly."""
    plugin_class = plugin_loader.load_plugin_class(
        ENTRY_POINT_NAME, plugin_executor.MODIFICATION_ENTRYPOINT_GROUP
    )
    plugin = plugin_class(default_release_entry, default_global_config, tmp_path)
    assert isinstance(plugin, regex_replacer.RegexReplacerPlugin)
    return plugin


# Test, if the replacement counts are respected.
@pytest.mark.parametrize("replacement_count", [0, 1, 2, 3])
# Test, if replacements strings and lists are handled as expected
@pytest.mark.parametrize("replacement", ['"pyproject"=="iGotReplaced"', ["I", "GOT", "Repl"]])
def test_regex_replacer__various_replacement_configurations(
    tmp_path: pathlib.Path,
    replacement_count: int,
    replacement: Union[str, list[str]],
    regex_replacer_plugin: regex_replacer.RegexReplacerPlugin,
):
    """Tests, if
    - the string gets replaced N-times dependent on replacement_count
    - the the string is replaced correctly
    """

    str_1 = '"pyproject"=="1.2.43"'
    str_2 = '"pyproject"=="49.12.233"'
    str_3 = '"pyproject"=="123.12.233"'

    file_content = f"""
        Lorem ipsum dolor sit amet, consectetur adipisici elit, 
        sed eiusmod tempor incidunt ut labore et dolore magna aliqua

        {str_1} Lorem ipsum dolor sit amet

        {str_2}Lorem ipsum dolor sit amet

        {str_3}Lorem ipsum dolor sit amet  

        Lorem ipsum dolor sit amet\
    """

    test_file = tmp_path / "test.txt"
    test_file.write_text(file_content, encoding="utf-8")

    repository_dir = test_file.parent

    relative_path = test_file.relative_to(repository_dir)

    replacement_str = "".join(replacement) if isinstance(replacement, list) else replacement
    regex_replacer_plugin.run(
        str(relative_path), '"pyproject"=="\d+\.\d+\.\d+"', replacement, replacement_count
    )

    result = test_file.read_text(encoding="utf-8")
    assert result.count(replacement_str) == (replacement_count if replacement_count != 0 else 3)
    assert result.count(str_1) == 0
    assert result.count(str_2) == (0 if replacement_count in [0, 2, 3] else 1)
    assert result.count(str_3) == (0 if replacement_count in [0, 3] else 1)
