# Contributing to ERA

[code-of-conduct]: CODE_OF_CONDUCT.md
[getting-started-developer]: doc/getting_started_developer

Hi there! We appreciate your interest in contributing to our project - your support helps us maintain its quality

Please note that this project is released with a [Contributor Code of Conduct][code-of-conduct].
By participating in this project you agree to abide by its terms.

If you want to implement a new feature, fix an existing bug, or help improve ERA in any
other way (such as adding or improving documentation), feel free to submit a pull request on GitHub.
It might be a good idea to open an issue beforehand and discuss your planned contributions.

Before you start working on your contribution, please make sure to follow the guidelines
described below.

## Setup

The [Git Forking Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow) is used:

1. Create a [fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) of the [repository](https://github.com/IngenicsDigital/easy-release-automation).

2. Clone the fork to your machine:

    ```bash
        git clone https://github.com/<your-username>/easy-release-automation
    ```

3. Make sure your [username](https://docs.github.com/en/get-started/getting-started-with-git/setting-your-username-in-git) and [email](https://docs.github.com/en/github/setting-up-and-managing-your-github-user-account/managing-email-preferences/setting-your-commit-email-address#setting-your-commit-email-address-in-git) are configured to match your account.

4. Add the original repository (also called _upstream_) as a remote to your local clone:

    ```bash
          git remote add upstream git@github.com:IngenicsDigital/easy-release-automation.git
    ```

5. Read [Getting Started for Developer][getting-started-developer]

### Add a feature or fix a bug

- Create and switch to a new branch (use a self-explanatory branch name).
  - Add identifiers from corresponding tickets, e.g. `issue-15`
  - Add a self-explanatory branch name after the identifier, e.g. `issue-15-my-new-feature`
- Make changes and commit them. Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- Push the changes to your remote fork.
- Add an entry to `CHANGELOG.md` (section "Unreleased") where you link to the corresponding PR and (if you desire) your account.
- Create a [pull request (PR)](https://github.com/IngenicsDigital/easy-release-automation/pulls).

## Coding Style

We use the following tools for code style and quality:

- [flake8](https://flake8.pycqa.org/en/latest/) for linting
- [mypy](https://mypy.readthedocs.io/en/stable/) for static type checking

## Recommended Visual Studio Code Extensions

To help maintain the quality of our code and ease the development process, we recommend the
following Visual Studio Code extensions for contributors.
These tools will assist you in adhering to our coding standards, checking syntax, and ensuring
commit message consistency.

For installing these extensions, please read the [Official Documentation](https://code.visualstudio.com/docs/editor/extension-marketplace)

### Extensions List

- **Conventional Commits**: Helps in enforcing our commit message style guide, ensuring that all
commit messages meet the required conventional commit format.
  - [Conventional Commits VS Code Extension](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits)

- **Markdownlint**: Lints Markdown files to ensure style consistency and correctness.
  - [Markdownlint VS Code Extension](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)

- **Flake8**: A linter that checks the Python code against coding style (PEP 8), programming errors, and complexity.
  - [Flake8 Linter](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8)

- **Python**: Provides comprehensive support for Python including features such as IntelliSense,
linting, debugging, code navigation, code formatting, Jupyter notebook support, refactoring, and snippets.
  - [Python for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

- **ShellCheck**: A powerful tool for analyzing and linting your shell scripts to avoid errors and
improve the scripts' robustness.
  - [ShellCheck](https://marketplace.visualstudio.com/items?itemName=timonwong.shellcheck)
