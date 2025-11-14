"""Tests for CLI interface."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from src.cli import app

runner = CliRunner()


def test_cli_help():
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Scan repository for security vulnerabilities" in result.stdout


def test_cli_version():
    """Test CLI version command."""
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "v1.0.0" in result.stdout


def test_cli_scan_invalid_format(tmp_path):
    """Test CLI with invalid format."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    (repo / "test.py").touch()

    result = runner.invoke(app, ["scan", str(repo), "--format", "invalid"])

    assert result.exit_code != 0
    assert "Invalid format" in result.stdout


def test_cli_scan_nonexistent_repo():
    """Test CLI with non-existent repository."""
    result = runner.invoke(app, ["scan", "/nonexistent/repo"])

    assert result.exit_code != 0
    assert "does not exist" in result.stdout


@patch("src.cli.SecurityScanner")
def test_cli_scan_success(mock_scanner_class, tmp_path):
    """Test successful CLI scan."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    (repo / "test.py").touch()

    # Mock scanner
    mock_scanner = MagicMock()
    mock_scanner.scan.return_value = []  # No findings
    mock_scanner_class.return_value = mock_scanner

    output_file = tmp_path / "findings.json"
    result = runner.invoke(app, ["scan", str(repo), "--format", "json", "--output", str(output_file)])

    assert result.exit_code == 0
    assert "No security findings" in result.stdout or "Found 0" in result.stdout
    assert output_file.exists()


@patch("src.cli.SecurityScanner")
def test_cli_scan_with_findings(mock_scanner_class, tmp_path, sample_finding):
    """Test CLI scan with findings."""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    # Mock scanner with findings
    mock_scanner = MagicMock()
    mock_scanner.scan.return_value = [sample_finding]
    mock_scanner_class.return_value = mock_scanner

    output_file = tmp_path / "findings.json"
    result = runner.invoke(app, ["scan", str(repo), "--format", "json", "--output", str(output_file)])

    # Should exit with non-zero if critical findings
    assert output_file.exists()
    assert "findings" in result.stdout.lower()

