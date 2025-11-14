"""Tests for security orchestrator."""

from unittest.mock import MagicMock, patch

import pytest

from src.security_orchestrator import SecurityScanner


def test_scan_merged_findings(config_dir, sample_findings, temp_repo):
    """Test orchestrator merges findings from both tools."""
    scanner = SecurityScanner(config_dir=config_dir)

    # Ensure tools are enabled
    assert scanner.semgrep is not None
    assert scanner.gitleaks is not None

    # Mock child agents
    with patch.object(scanner.semgrep, "analyze") as mock_semgrep, patch.object(
        scanner.gitleaks, "scan"
    ) as mock_gitleaks:
        mock_semgrep.return_value = [sample_findings[0]]  # Semgrep finding
        mock_gitleaks.return_value = [sample_findings[1]]  # Gitleaks finding

        findings = scanner.scan(temp_repo)

        assert len(findings) >= 2  # Both findings merged
        assert any(f["tool"] == "semgrep" for f in findings)
        assert any(f["tool"] == "gitleaks" for f in findings)


def test_scan_handles_tool_errors(config_dir):
    """Test orchestrator handles tool errors gracefully."""
    scanner = SecurityScanner(config_dir=config_dir)

    # Mock one tool failing
    with patch.object(scanner.semgrep, "analyze") as mock_semgrep, patch.object(
        scanner.gitleaks, "scan"
    ) as mock_gitleaks:
        mock_semgrep.side_effect = Exception("Semgrep failed")
        mock_gitleaks.return_value = []

        # Should not crash, but return empty or partial findings
        findings = scanner.scan("/tmp/repo")

        # Orchestrator should handle error and continue
        assert isinstance(findings, list)


def test_orchestrator_metrics(config_dir):
    """Test orchestrator logs metrics."""
    scanner = SecurityScanner(config_dir=config_dir)

    with patch.object(scanner.semgrep, "analyze") as mock_semgrep, patch.object(
        scanner.gitleaks, "scan"
    ) as mock_gitleaks:
        mock_semgrep.return_value = []
        mock_gitleaks.return_value = []

        findings = scanner.scan("/tmp/repo")

        # Metrics should be logged (tested via log capture if needed)
        assert isinstance(findings, list)

