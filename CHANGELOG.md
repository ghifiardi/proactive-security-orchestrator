# Changelog

All notable changes to the Proactive Security Orchestrator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.7] - 2025-01-XX

### Added
- `--no-fail-on-critical` flag to prevent workflow failure on critical findings
- CI/CD optimization for non-blocking security scans

### Changed
- Default behavior still exits with code 1 on critical findings (can be disabled with flag)

## [1.0.6] - 2025-01-XX

### Added
- PDF output format with professional layout
- Structured PDF reports with bullet points
- Summary tables in PDF format
- Code snippets in PDF reports
- Remediation guidance boxes in PDF

### Changed
- Added `reportlab>=4.0.0` dependency for PDF generation

## [1.0.5] - 2025-01-XX

### Added
- Human-readable rule names in SARIF output
- Contextual messages with CWE information
- Enhanced remediation guidance extraction
- Better rule name formatting from technical IDs
- Code snippets in SARIF region data
- Full description fields in SARIF rules

### Changed
- SARIF messages now use readable text instead of rule IDs
- Improved severity mapping and descriptions
- Better metadata extraction from Semgrep results

## [1.0.4] - 2025-01-XX

### Added
- Automatic fallback to Semgrep default security rules when config file missing
- Logging when using default rules

### Changed
- Semgrep analyzer no longer skips when rules file not found
- Uses `--config auto` for default Semgrep security rules

## [1.0.3] - 2025-01-XX

### Added
- `child_agent_schema.json` included in package distribution
- Proper package data configuration in setup.py

### Fixed
- Schema file now accessible in installed package
- FindingValidator can locate schema file correctly

## [1.0.2] - 2025-01-XX

### Changed
- Pinned `rich==13.5.2` for Semgrep compatibility
- Updated package namespace alignment

## [1.0.1] - 2025-01-XX

### Changed
- Initial version bump for GitHub Actions cache invalidation

## [1.0.0] - 2025-01-XX

### Added
- Initial release
- Semgrep integration
- Gitleaks integration
- SARIF output format
- JSON output format
- HTML output format
- GitHub Actions workflow support
- Basic finding validation

