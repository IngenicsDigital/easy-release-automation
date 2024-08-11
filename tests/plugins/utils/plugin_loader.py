"""Utility Functions for Loading Plugins

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import importlib.metadata


def load_plugin_class(entry_point_name: str, entry_point_group: str):
    """Returns the loaded entrypoint/plugin-class for the given group and name."""
    entry_points = importlib.metadata.entry_points()[entry_point_group]
    for entry_point in entry_points:
        if entry_point.name == entry_point_name:
            return entry_point.load()
    raise RuntimeError(f"Plugin not found. {entry_point_name=}, {entry_point_group=}")
