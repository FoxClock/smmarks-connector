# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-12

### Added
- `MarkbookApiClient` — facade for all SM Marks API actions.
- `InitialAuthStrategy` / `OngoingAuthStrategy` — pluggable auth strategies.
- Full model layer covering all known API response shapes.
- `configure()` — package-level entry point for redaction configuration.
- `ScrubFilter` — `logging.Filter` for defence-in-depth log redaction.
- GitHub Actions workflows for CI (test + lint) and PyPI release on tag.

[Unreleased]: https://github.com/FoxClock/smmarks-connector/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/FoxClock/smmarks-connector/releases/tag/v0.1.0
