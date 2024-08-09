#!/usr/bin/env bash
#
# Copyright (c) 2024 Ingenics Digital GmbH
# 
# SPDX-License-Identifier: MIT
# 
# Authors:
#    - David Kauschke <david.kauschke@ingenics-digital.com>

set -e
[ "$DEBUG" = 1 ] && set -x


echo "Setup venv for ERA"

python3 -m venv .venv
. .venv/bin/activate
pip install . -e
pip install -r requirements-test.txt
tox -e lint
echo "Setup venv for ERA completed"

echo "Run ERA in test mode natively"

GIT_USER=$(git config user.name)
GIT_MAIL=$(git config user.email)
# Print the values to verify
echo "Git User Name: $GIT_USER"
echo "Git User Email: $GIT_MAIL"

ERA_LOG_LEVEL="DEBUG" easy-release-automation --author "${GIT_USER}" --email "${GIT_MAIL}" --test true --conf "era/release-config.yml"
