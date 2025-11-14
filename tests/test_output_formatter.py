"""Tests for output formatters."""

import json

import pytest

from src.formatters.output_formatter import OutputFormatter


def test_to_json(sample_findings):
    """Test JSON formatter produces valid JSON."""
    formatter = OutputFormatter()
    output = formatter.to_json(sample_findings)

    # Should be valid JSON
    parsed = json.loads(output)
    assert isinstance(parsed, list)
    assert len(parsed) == len(sample_findings)


def test_to_sarif(sample_findings):
    """Test SARIF formatter produces valid SARIF."""
    formatter = OutputFormatter()
    output = formatter.to_sarif(sample_findings)

    # Should be valid JSON
    parsed = json.loads(output)

    # Should have SARIF structure
    assert parsed["version"] == "2.1.0"
    assert "runs" in parsed
    assert len(parsed["runs"]) > 0
    assert "tool" in parsed["runs"][0]
    assert "results" in parsed["runs"][0]


def test_to_html(sample_findings):
    """Test HTML formatter produces valid HTML."""
    formatter = OutputFormatter()
    output = formatter.to_html(sample_findings)

    # Should be HTML
    assert output.startswith("<!DOCTYPE html>")
    assert "<html" in output.lower()
    assert str(len(sample_findings)) in output  # Count should be in HTML


def test_save_to_file(sample_findings, tmp_path):
    """Test saving findings to file."""
    formatter = OutputFormatter()
    output_file = tmp_path / "findings.json"

    formatter.save_to_file(sample_findings, "json", output_file)

    assert output_file.exists()
    content = json.loads(output_file.read_text())
    assert len(content) == len(sample_findings)

