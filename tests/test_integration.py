"""Integration tests for end-to-end scanning."""

import pytest

from proactive_security_orchestrator.security_orchestrator import SecurityScanner


@pytest.mark.integration
def test_end_to_end_scan(temp_repo, config_dir):
    """Test end-to-end scan on test repository."""
    scanner = SecurityScanner(config_dir=config_dir, timeout=30)

    # Run scan (may not find anything if tools aren't installed, but should not crash)
    try:
        findings = scanner.scan(temp_repo)

        # Should return a list (even if empty)
        assert isinstance(findings, list)

        # If tools are available, may find issues
        # If not, should gracefully return empty list
    except Exception as e:
        # If tools not installed, skip test
        if "not found" in str(e).lower() or "command not found" in str(e).lower():
            pytest.skip(f"Tools not installed: {e}")
        else:
            raise


@pytest.mark.integration
def test_integration_with_mocked_tools(temp_repo, config_dir, sample_findings):
    """Test integration with mocked tools (simulates real scan)."""
    from unittest.mock import patch

    scanner = SecurityScanner(config_dir=config_dir)

    # Mock both tools to return sample findings
    with patch.object(scanner.semgrep, "analyze") as mock_semgrep, patch.object(
        scanner.gitleaks, "scan"
    ) as mock_gitleaks:
        mock_semgrep.return_value = [sample_findings[0]]
        mock_gitleaks.return_value = [sample_findings[1]]

        findings = scanner.scan(temp_repo)

        # Should have both findings
        assert len(findings) >= 2

        # Should be validated
        for finding in findings:
            assert "tool" in finding
            assert "severity" in finding
            assert "evidence" in finding

