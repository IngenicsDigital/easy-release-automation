"""Easy-Release-Automation (ERA) - Process

Description:
    This file declares the Entry-Point of ERA and defines the flow control of the automated
    release-process. It reads in the configuration file, triggers the git commands and executes the
    plugins.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import argparse
import json
import logging
import os
import pathlib
from dataclasses import dataclass
from typing import Optional

from easy_release_automation.configuration import GlobalConfig, ReleaseEntry, get_configuration
from easy_release_automation.utils import logging_wrapper
from easy_release_automation.utils.git_handler import GitHandler
from easy_release_automation.utils.logging_wrapper import format_chapter, format_major
from easy_release_automation.utils.plugin_executor import PluginExecutor

logger = logging.getLogger(__name__)


# Path relative to the working directory specifying the directory where repositories are cloned to.
REPOSITORIES_DIR = ".era-repositories"


def perform_local_release_steps(git_handler: GitHandler, plugin_executer: PluginExecutor):
    """Performs the local release steps on the given repository. Additionally, it validates if the
    tag already exists, and returns if the policy

    Args:
        git_handler: handler that allows to merge or switch between repositories, etc...
        plugin_executer: executor for the specified plugins.
    """

    # Release Branch
    git_handler.checkout_release_branch()
    plugin_executer.modify_release_branch()
    plugin_executer.validate_release_branch()
    git_handler.commit_release()

    # Stable Branch
    git_handler.merge_release_into_stable()
    git_handler.commit_stable()

    # Merge-Back Branch
    git_handler.checkout_merge_back_branch()
    plugin_executer.finalize_merge_back_branch()
    git_handler.commit_merge_back()

    # Main Branch
    git_handler.merge_merge_back_into_main()


def skip_repository(
    git_handler: GitHandler, global_tag_policy: str, local_tag_policy: Optional[str]
) -> bool:
    """Validates if a repository should be skipped and can erase the tag if it should be
    overwritten."""

    logger.debug(
        "Validate Skipping. global-tag-policy: %s, local-tag-policy %s",
        global_tag_policy,
        local_tag_policy,
    )

    tag_policy = global_tag_policy if local_tag_policy is None else local_tag_policy

    if git_handler.tag_exists():
        logger.info("The tag is already existing. Active tag_policy: %s.", tag_policy)
        if tag_policy == "skip":
            return True
    return False


def perform_release_for_single_entry(
    global_config: GlobalConfig, release_entry: ReleaseEntry, repository_dir: pathlib.Path
):
    """Performs the release process for a single release entry. It triggers the local release steps.
    If the release process is not a test run, the changes are pushed to the remote repository.

    Args:
        global_config: global configuration available for all release entries.
        release_entry: configuration that solely accounts for this single entry.
        repository_dir: directory where the repository is cloned to.
    """
    plugin_executor = PluginExecutor(release_entry, global_config, repository_dir)
    git_handler = GitHandler(release_entry, global_config, repository_dir)

    if skip_repository(git_handler, global_config.tag_policy, release_entry.private.tag_policy):
        logger.info("Skipping Repository.")
        return

    perform_local_release_steps(git_handler, plugin_executor)

    if global_config.test_run:
        logger.info(
            format_chapter("Successfully Finished Test-Run - No Pushes to Remote (repository: %s)"),
            release_entry.name,
        )
    else:
        logger.info(format_chapter("Successfully Built Release for: %s"), release_entry.name)
        git_handler.push_changes_to_remote()
        logger.info(
            format_chapter("Finish: Successfully Pushed all Changes for the repository: %s."),
            release_entry.name,
        )


def perform_release_process(
    work_directory: pathlib.Path, global_config: GlobalConfig, release_entries: list[ReleaseEntry]
):
    """Performs the full release process for the given release entries within the
    configuration_path.

    Args:
        work_directory: directory where the release repositories are cloned to, modified and
            evaluated.
        global_config: global release configuration
        release_entries: list of repositories to release
    """

    for release_entry in release_entries:
        if release_entry.private.should_skip:
            logger.info(format_chapter("Skipping Release for Repository: '%s'"), release_entry.name)
            continue
        logger.info(format_chapter("Beginning Release For: '%s'"), release_entry.name)

        repository_dir = work_directory / release_entry.name
        perform_release_for_single_entry(global_config, release_entry, repository_dir)

    logger.info(format_major("Successfully Built Release for all Repositories."))


@dataclass
class CLIArguments:
    """Dataclass for the cli-arguments."""

    configuration_path: pathlib.Path
    test_run: Optional[bool]
    author: Optional[str]
    email: Optional[str]
    global_tag_policy: Optional[str]


def parse_cli_args() -> CLIArguments:
    """Parses the cli-arguments and returns them as a dataclass."""
    parser = argparse.ArgumentParser(description="Release Automation Script.")
    parser.add_argument("--conf", type=str, help="Path to the release configuration file.")
    parser.add_argument(
        "--test",
        type=str,
        help="determines if Test-Run is active. true/false. "
        "Overrides test_run of the global configuration.",
    )
    parser.add_argument(
        "--author",
        type=str,
        help="author of the release. Overrides git_user_name of the global configuration.",
    )
    parser.add_argument(
        "--email",
        type=str,
        help="the author's email. Overrides git_user_email of the global configuration.",
    )
    parser.add_argument(
        "--global-tag-policy",
        type=str,
        help="'skip': skip repository if tag exists, 'ovr': override existing tag. "
        "Overrides tag_policy of the global configuration.",
    )

    arguments = parser.parse_args()

    try:
        test_run = None if arguments.test is None else json.loads(arguments.test.lower())
    except json.decoder.JSONDecodeError:
        logger.error("Expected True/False for parameter --test")

    return CLIArguments(
        configuration_path=pathlib.Path(arguments.conf),
        test_run=test_run,
        author=arguments.author,
        email=arguments.email,
        global_tag_policy=arguments.global_tag_policy,
    )


def main():
    """Configures and Starts ERA"""

    logging_wrapper.configure_logging(os.getenv("ERA_LOG_LEVEL", "INFO"))

    cli_args = parse_cli_args()
    current_directory = pathlib.Path().cwd()
    work_directory = current_directory / REPOSITORIES_DIR

    logger.info(format_chapter("Read_Configuration"))
    global_config, release_entries = get_configuration(
        cli_args.configuration_path,
        cli_args.test_run,
        cli_args.author,
        cli_args.email,
        cli_args.global_tag_policy,
    )
    logging_wrapper.log_release_information(release_entries, global_config)

    perform_release_process(work_directory, global_config, release_entries)


if __name__ == "__main__":
    # If this script is run directly, execute main()
    main()
