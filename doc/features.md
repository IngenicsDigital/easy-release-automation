# ERA Features

Supported features: (+)

Unsupported features: (-)

Unclear supported features: (?)

Planned features: (*)

## Platform Support

- (+) Natively on local PC with Linux
- (+) In CI-pipeline with ERA exeucution natively
- (-) ERA in Docker because DinD problems occur when plugins start docker containers
- (*) Natively on local PC with Windows

## Execution Modes

- (+) Production-run.
- (+) Test-run. Note: Plugins need to support this feature - should not be reliant on remote-dependencies.

## Modification-Plugins

- (+) Update configuration files (.cfg).
- (+) Update YAML files (.yaml).
- (+) Update requirement files with dependencies from other git repositories
  - (+) requirements.txt, requirements.in
  - (+) pyproject.toml
- (+) Update requirement files with dependencies from other git repositories and pip-compile them.
  - (+) requirements.in
  - (+) pyproject.toml
- (+) Update the [Unreleased] entry to the correct version in changelog.md files.
- (+) Replace arbitrary text in plaintext files via regex substitution.

## Validation-Plugins

- (+) Shell Validation

## Merge-Back-Finalization-Plugins

- (+) Replace arbitrary text in plaintext files via regex substitution.
- (+) Add a new [Unreleased] section to changelog.md files.

## Expandability

- (+) Can be expanded by writing new Plugins via the Python Plugin mechanism.
- (+) The Shell-Validation-Plugin denotes an open door for a broad field of commands.

## Fail-Safe

- If a release of one repository fails, the release is aborted.
- (-) Releases that are executed prior to the failed release, are still released.
- (*) Ability to turn back changes on the remote.

## Authentication

- (+) Access token located unencrypted in `.git-credentials`
- (+) SSH Deploy Keys
- (-) Encrypted `.git-credentials`
