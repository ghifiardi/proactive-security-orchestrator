"""Tests for Gitleaks scanner."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.tools.gitleaks_scanner import GitleaksScanner


def test_scan_success(config_dir):
    """Test successful Gitleaks scan."""
    scanner = GitleaksScanner(config_dir / "gitleaks")

    # Mock gitleaks output (one JSON object per line)
    gitleaks_output = json.dumps(
        {
            "Description": "Generic API Key",
            "StartLine": 10,
            "EndLine": 10,
            "StartColumn": 11,
            "EndColumn": 40,
            # Use obviously fake/non-sensitive values to avoid triggering scanners
            "Match": "NOT_A_REAL_SECRET_KEY_FOR_TESTS",
            "Secret": "NOT_A_REAL_SECRET_KEY_FOR_TESTS",
            "File": "config.py",
            "SymlinkFile": "",
            "Commit": "",
            "Entropy": 4.5,
            "Author": "",
            "Email": "",
            "Date": "",
            "Message": "",
            "Tags": [],
            "RuleID": "generic-api-key",
        }
    )

    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1  # Gitleaks returns 1 when findings found
        mock_result.stdout = gitleaks_output
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        findings = scanner.scan("/tmp/repo")

        assert len(findings) == 1
        assert findings[0]["tool"] == "gitleaks"
        assert findings[0]["severity"] == "critical"  # Secrets are always critical
        assert findings[0]["rule_id"] == "generic-api-key"


def test_redact_secrets(config_dir):
    """Test secret redaction in findings."""
    scanner = GitleaksScanner(config_dir / "gitleaks")

    # Test redaction method
    secret = "NOT_A_REAL_SECRET_KEY"
    redacted = scanner._redact_secret(secret)

    assert redacted.startswith("NOT")
    assert redacted.endswith("KEY")
    assert "..." in redacted
    assert secret not in redacted  # Full secret not in redacted version


def test_scan_tool_not_found(config_dir):
    """Test scanner handles missing gitleaks command."""
    scanner = GitleaksScanner(config_dir / "gitleaks")

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("gitleaks: command not found")

        findings = scanner.scan("/tmp/repo")

        assert findings == []  # Empty list on error


def test_scan_no_findings(config_dir):
    """Test scanner handles no findings (exit code 0)."""
    scanner = GitleaksScanner(config_dir / "gitleaks")

    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0  # No findings
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        findings = scanner.scan("/tmp/repo")

        assert findings == []  # Empty list when no findings

