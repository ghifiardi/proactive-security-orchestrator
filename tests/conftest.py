"""Pytest configuration and fixtures."""

import json
import tempfile
from pathlib import Path
from typing import Dict, List

import pytest


@pytest.fixture
def sample_finding() -> Dict:
    """Sample valid finding dictionary."""
    return {
        "finding": "SQL injection vulnerability detected",
        "evidence": [
            {
                "path": "src/app.py",
                "lines": "L45-L47",
                "why_relevant": "User input directly concatenated into SQL query",
                "code_snippet": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
            }
        ],
        "confidence": 0.9,
        "tool": "semgrep",
        "severity": "critical",
        "rule_id": "python.sql-injection",
        "remediation": "Use parameterized queries or ORM methods",
    }


@pytest.fixture
def sample_findings(sample_finding: Dict) -> List[Dict]:
    """List of sample findings."""
    finding2 = {
        **sample_finding,
        "finding": "Hardcoded API key detected",
        "evidence": [
            {
                "path": "config.py",
                "lines": "L10",
                "why_relevant": "API key hardcoded in source code",
                "code_snippet": "API_KEY = 'NOT_A_REAL_SECRET'",
            }
        ],
        "severity": "high",
        "tool": "gitleaks",
        "rule_id": "generic-api-key",
    }
    return [sample_finding, finding2]


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Create a temporary repository for testing."""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    # Create a Python file with vulnerability
    (repo / "app.py").write_text(
        '''# Test file with vulnerability
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)
'''
    )

    # Create a file with hardcoded secret (for gitleaks testing)
    (repo / "config.py").write_text(
        '''# Configuration file
API_KEY = "NOT_A_REAL_SECRET"
SECRET = "password123"
'''
    )

    # Initialize git repo (optional, for gitleaks)
    return repo


@pytest.fixture
def schema_path() -> Path:
    """Path to JSON schema file bundled with the package."""
    project_root = Path(__file__).parent.parent / "src" / "proactive_security_orchestrator"
    return project_root / "contracts" / "child_agent_schema.json"


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    """Create temporary config directory."""
    config = tmp_path / "config"
    config.mkdir()

    # Create semgrep config
    semgrep_dir = config / "semgrep"
    semgrep_dir.mkdir()
    (semgrep_dir / "rules.yaml").write_text(
        """rules:
  - id: p/python-security
exclude:
  - .git
"""
    )

    # Create gitleaks config
    gitleaks_dir = config / "gitleaks"
    gitleaks_dir.mkdir()
    (gitleaks_dir / ".gitleaksignore").write_text("# Test ignore patterns\n")

    return config

