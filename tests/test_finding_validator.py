"""Tests for finding validator."""

import pytest

from proactive_security_orchestrator.validators.finding_validator import FindingValidator


def test_validate_valid_finding(sample_finding, schema_path):
    """Test validator accepts valid finding."""
    validator = FindingValidator(schema_path=schema_path)
    findings = [sample_finding]

    result = validator.validate_all(findings)

    assert len(result) == 1
    assert result[0] == sample_finding


def test_validate_invalid_finding(schema_path):
    """Test validator rejects finding missing required fields."""
    validator = FindingValidator(schema_path=schema_path)

    # Missing required field
    invalid_finding = {
        "finding": "Test",
        # Missing evidence, confidence, tool, severity
    }

    findings = [invalid_finding]
    result = validator.validate_all(findings)

    assert len(result) == 0  # Invalid finding filtered out


def test_deduplicate_findings(sample_finding, schema_path):
    """Test validator de-duplicates findings by path/line/rule_id."""
    validator = FindingValidator(schema_path=schema_path)

    # Duplicate finding (same path, line, rule_id)
    duplicate = {**sample_finding}
    findings = [sample_finding, duplicate]

    result = validator.validate_all(findings)

    assert len(result) == 1  # Duplicate removed


def test_sort_by_severity(sample_finding, schema_path):
    """Test validator sorts findings by severity."""
    validator = FindingValidator(schema_path=schema_path)

    # Create findings with different severities
    critical = {**sample_finding, "severity": "critical"}
    high = {**sample_finding, "severity": "high", "rule_id": "rule2"}
    medium = {**sample_finding, "severity": "medium", "rule_id": "rule3"}

    findings = [medium, critical, high]  # Wrong order
    result = validator.validate_all(findings)

    # Should be sorted: critical, high, medium
    assert result[0]["severity"] == "critical"
    assert result[1]["severity"] == "high"
    assert result[2]["severity"] == "medium"

