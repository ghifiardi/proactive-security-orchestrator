"""Tests for Semgrep analyzer."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.tools.semgrep_analyzer import SemgrepAnalyzer


def test_analyze_success(config_dir):
    """Test successful Semgrep analysis."""
    analyzer = SemgrepAnalyzer(config_dir / "semgrep")

    # Mock semgrep output
    semgrep_output = {
        "results": [
            {
                "check_id": "python.sql-injection",
                "path": "app.py",
                "start": {"line": 45},
                "end": {"line": 47},
                "message": "SQL injection vulnerability",
                "extra": {"severity": "ERROR", "lines": "query = f\"SELECT * FROM users WHERE id = {user_id}\""},
            }
        ]
    }

    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(semgrep_output)
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        findings = analyzer.analyze("/tmp/repo")

        assert len(findings) == 1
        assert findings[0]["tool"] == "semgrep"
        assert findings[0]["rule_id"] == "python.sql-injection"
        assert findings[0]["severity"] == "critical"  # ERROR -> critical


def test_analyze_tool_not_found(config_dir):
    """Test analyzer handles missing semgrep command."""
    analyzer = SemgrepAnalyzer(config_dir / "semgrep")

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("semgrep: command not found")

        findings = analyzer.analyze("/tmp/repo")

        assert findings == []  # Empty list on error


def test_analyze_timeout(config_dir):
    """Test analyzer handles timeout."""
    analyzer = SemgrepAnalyzer(config_dir / "semgrep", timeout=5)

    with patch("subprocess.run") as mock_run:
        from subprocess import TimeoutExpired

        mock_run.side_effect = TimeoutExpired("semgrep", 5)

        findings = analyzer.analyze("/tmp/repo")

        assert findings == []  # Empty list on timeout


def test_analyze_invalid_json(config_dir):
    """Test analyzer handles invalid JSON output."""
    analyzer = SemgrepAnalyzer(config_dir / "semgrep")

    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json{"
        mock_run.return_value = mock_result

        findings = analyzer.analyze("/tmp/repo")

        assert findings == []  # Empty list on parse error

