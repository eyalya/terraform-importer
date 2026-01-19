# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- None

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

## [2.0.1] - 2026-01-XX
### Fixed
- Kubernetes provider now validates `config_context` and `config_path` are strings, preventing crashes when Terraform references are unresolved
- Provider initialization failures are now non-fatal - tool continues execution with warnings instead of crashing
- Improved error messages for Kubernetes provider configuration issues

### Added
- Kubernetes provider README documentation explaining configuration requirements

## [2.0.0] - 2026-01-19
### Added
- AWS API Gateway WebSocket integration support
- AWS ECR (Elastic Container Registry) service support
- Bitbucket provider support
- Enhanced Kubernetes provider support
- Enhanced error handling with proper warning levels
- Project metadata and testing instructions
- Comprehensive test coverage for AWS services

### Changed
- Refactored AWS service implementations for better maintainability
- Improved error handling to use appropriate log levels (WARNING for provider-level issues, ERROR for system errors)
- Enhanced CLI argument handling and Terraform command execution

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

## [1.0.0] - 2025-06-26
### Added
- Initial project structure
- Basic AWS resource import functionality
- Command-line interface for resource importing
- Documentation setup
- Use providers authentication from terraform configuration

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

## [0.1.0] - YYYY-MM-DD
### Added
- Initial release
- Basic project structure
- Core importing functionality
- AWS provider support
- Basic CLI interface

[Unreleased]: https://github.com/eyalya/terraform-importer/compare/v2.0.1...HEAD
[2.0.1]: https://github.com/eyalya/terraform-importer/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/eyalya/terraform-importer/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/eyalya/terraform-importer/releases/tag/v1.0.0
[0.1.0]: https://github.com/eyalya/terraform-importer/releases/tag/v0.1.0
