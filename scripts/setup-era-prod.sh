#!/usr/bin/env bash
# Sets up an production python environment for ERA
#
# Copyright (c) 2024 Ingenics Digital GmbH
# 
# SPDX-License-Identifier: MIT
# 
# Authors:
#    - David Kauschke <david.kauschke@ingenics-digital.com>

set -e
[ "$DEBUG" = 1 ] && set -x

echo "[PROD] Setup venv (.venv-prod) for ERA"

python3 -m venv .venv-prod
. .venv-prod/bin/activate
pip install .
pip install -r requirements.txt
echo "[PROD] Setup venv (.venv-prod) for ERA completed"
