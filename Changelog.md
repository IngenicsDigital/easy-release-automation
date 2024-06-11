# Changelog

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- First public preview release.
- #1: Added CI testing pipeline.

### Changed

- #4: add "./src/core" sub-folder for ERA-specific flow control to improve the overview of
  the ERA-module

### Fixed

- #2: add error handling for plugins, that are referenced in the release-config.yml, but are
  not installed (+ tests).
- #11: Don't push stable branch if missing when ERA test mode is active.
