#!/usr/bin/env bash
# Setup ERA development environment
#
# Copyright (c) 2024 Ingenics Digital GmbH
# 
# SPDX-License-Identifier: MIT
# 
# Authors:
#    - David Kauschke <david.kauschke@ingenics-digital.com>

set -e
[ "$DEBUG" = 1 ] && set -x

echo "[DEV] Setup venv (.venv) for ERA"

python3 -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-test.txt
tox -e lint
echo "[DEV] Setup venv (.venv) for ERA completed"