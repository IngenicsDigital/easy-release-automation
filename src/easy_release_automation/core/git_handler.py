"""GIT-Handler

Description:
    Handles the git actions related to the release-process. It builds up on the widely used python
    package GitPython https://pypi.org/project/GitPython/. The GitHandler wraps the steps shown
    in the flow chart (Overview.md) and is initialized for each repository.

Authors:
    - Claus Seibold <claus.seibold@ingenics-digital.com>

Copyright (c) 2024 Ingenics Digital GmbH

SPDX-License-Identifier: MIT
"""

import logging
import pathlib
import shutil
from dataclasses import dataclass

import git
import git.exc

from easy_release_automation.core.configuration import GlobalConfig, ReleaseEntry

logger = logging.getLogger(__name__)


class GitHandlerException(Exception):
    """Thrown if an exception within the GIT-Handler occurs."""


class GitHandler:
    """Handles all git-related actions for a given repository configuration."""

    @dataclass
    class BranchNames:
        main: str
        stable: str
        release: str = "era_release_branch"
        merge_back: str = "era_merge_back_branch"

    def __init__(
        self, release_entry: ReleaseEntry, global_config: GlobalConfig, repository_dir: pathlib.Path
    ):
        """Initializes the GitHandler by cloning and initializing the repository, setting up the
        branch names and writing the configuration parameters into class-variables.
        """

        self._release_entry = release_entry
        self._global_config = global_config
        self._repository_dir = repository_dir

        self._branches = self.BranchNames(
            release_entry.public.main_branch, release_entry.public.stable_branch
        )

        self._clone_repository()
        self._repository = git.Repo.init(str(self._repository_dir))
        self._repository.config_writer().set_value(
            "user", "name", self._global_config.git_user_name
        ).release()
        self._repository.config_writer().set_value(
            "user", "email", self._global_config.git_user_email
        ).release()

    def checkout_release_branch(self):
        """Checks-out the 'release' branch originating from the local the 'main'-branch."""
        self._repository.git.switch(self._branches.main)
        self._repository.git.checkout("-b", self._branches.release)

    def checkout_merge_back_branch(self):
        """Checks-out the 'merge-back' branch originating from the local 'stable'-branch."""
        self._repository.git.switch(self._branches.stable)
        self._repository.git.checkout("-b", self._branches.merge_back)

    def merge_release_into_stable(self):
        """Merges the local release-branch into the local stable-branch, or initializes the
        'stable'-branch, if not existing."""

        logger.info("Switch to stable branch: '%s'", self._branches.stable)

        try:
            self._repository.git.switch(self._branches.stable)
        except git.exc.GitCommandError as error:
            logger.warning(
                "Generating non-existing stable-branch: %s from release branch: %s. Error: %s",
                self._branches.stable,
                self._branches.release,
                str(error),
            )
            self._repository.git.checkout(self._branches.release)
            self._repository.git.checkout("-b", self._branches.stable)
            logger.info("Setting up upstream for branch: '%s'.", self._branches.stable)
            self._repository.git.push("--set-upstream", "origin", self._branches.stable)
            return  # Return after generating new stable branch

        self._repository.git.merge(self._branches.release)
        logger.info(
            "Merge release branch: '%s' into stable branch: '%s'",
            self._branches.release,
            self._branches.stable,
        )

    def merge_merge_back_into_main(self):
        """Merges the local merge-back-branch into the local main-branch."""
        logger.debug("Switch to main branch: '%s'", self._branches.main)
        self._repository.git.checkout(self._branches.main)

        logger.info(
            "Merge merge-back-branch: '%s' into main branch: '%s'",
            self._branches.merge_back,
            self._branches.main,
        )
        self._repository.git.merge(self._branches.merge_back)

    def commit_release(self):
        """Commits the release-branch."""
        self._repository.git.checkout(self._branches.release)
        logger.info("Commit release_branch: '%s'", self._branches.release)
        self._commit(
            "chore: :white_check_mark: ERA: Modification with the plugin(s): "
            f"{self._get_plugin_string(self._release_entry.plugins.release_modification)} "
            "and Validation with the plugin(s): "
            f"{self._get_plugin_string(self._release_entry.plugins.release_validation)}"
        )

    def commit_stable(self):
        """Commits the stable-branch."""
        self._repository.git.checkout(self._branches.stable)
        logger.info("Commit commit stable branch: '%s'", self._branches.stable)
        self._commit(
            "chore: :bookmark: ERA: Release-Commit for Version: "
            f"{self._release_entry.public.version}"
        )

    def commit_merge_back(self):
        """Commits the merge-back-branch."""
        self._repository.git.checkout(self._branches.merge_back)
        logger.info("Commit merge-back-branch: '%s'", self._branches.merge_back)
        self._commit(
            "chore: :wastebasket: ERA: Preparation for merging back into main with the plugin(s): "
            f"{self._get_plugin_string(self._release_entry.plugins.merge_back_finalization)}"
        )

    def _get_plugin_string(self, plugins: list[dict[str, dict]]):
        """Allows to generate a string for all"""
        return ", ".join(", ".join(plugin.keys()) for plugin in plugins)

    def _clone_repository(self):
        """Clones the repository specified in the configuration file."""

        self._setup_directory(self._repository_dir)

        logger.info("Cloning: %s", self._release_entry.name)
        git.Repo.clone_from(
            url=self._release_entry.public.url,
            to_path=str(self._repository_dir),
        )

    def _setup_directory(self, repository_dir: pathlib.Path):
        """Sets up an empty folder at the given directory."""
        logger.info("Resetting repository directory: %s", repository_dir)
        if repository_dir.is_dir():
            shutil.rmtree(str(repository_dir))
        repository_dir.mkdir(exist_ok=True, parents=True)

    def _commit(self, message: str):
        """Stages all changes and commits with the given commit-message."""

        self._repository.git.add(all=True)
        self._repository.commit()
        self._repository.index.commit(message)

    def tag_exists(self):
        """Validates if the tag is already existing in the"""

        if self._release_entry.public.version in self._repository.tags:
            logger.warning("Tag %s already existing.", self._release_entry.public.version)
            return True
        return False

    def _remove_tag(self, tag: str):
        """Removes the tag from the repository (locally and remote)."""

        logger.info("Removing Existing Tag: %s.", tag)

        self._repository.git.tag("-d", tag)  # Delete locally
        self._repository.remote(name="origin").push(refspec=f":{tag}")

    def _tag_stable(self):
        """tags the repository (locally and remote)."""
        if self._global_config.test_run:
            return

        tag = self._release_entry.public.version
        if self.tag_exists():
            self._remove_tag(tag)

        logger.info(
            "Creating tag: %s for branch: %s", tag, self._release_entry.public.stable_branch
        )
        self._repository.create_tag(
            tag,
            ref=self._release_entry.public.stable_branch,
            message=self._release_entry.private.tag_message,
        )

        origin = self._repository.remote(name="origin")
        origin.push(tag)
        logger.info(
            "Successfully pushed the tag: %s for branch: %s",
            tag,
            self._release_entry.public.stable_branch,
        )

    def _push_branch_to_remote(self, branch: str):
        """Pushes the given branch to the remote repository."""

        logger.info("Pushing branch '%s' of repository '%s'", branch, self._release_entry.name)
        self._repository.git.switch(branch)
        origin = self._repository.remote(name="origin")
        push_info_list = origin.push()
        for push_info in push_info_list:
            logger.info(push_info.summary)
        push_info_list.raise_if_error()  # type: ignore [operator]
        logger.info(
            "Successfully pushed branch '%s' of repository '%s'.", branch, self._release_entry.name
        )

    def push_changes_to_remote(self):
        """Pushes the changes of the main- and stable-branch to the remote repository. And Tags the
        stable branch.

        NOTE: Local changes must be already committed before calling this function.
        """
        if self._repository.is_dirty(untracked_files=True):
            logger.error("Found un-staged changes in the repository.")

        self._push_branch_to_remote(self._branches.main)

        self._push_branch_to_remote(self._branches.stable)

        self._tag_stable()
