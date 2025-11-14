"""Gitleaks scanner child agent."""

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class GitleaksScanner:
    """Child agent for Gitleaks secrets detection."""

    def __init__(self, config_dir: Path | str, timeout: int = 60) -> None:
        """Initialize Gitleaks scanner.

        Args:
            config_dir: Directory containing Gitleaks config (.gitleaksignore)
            timeout: Timeout in seconds for Gitleaks execution
        """
        self.config_dir = Path(config_dir)
        self.ignore_path = self.config_dir / ".gitleaksignore"
        self.timeout = timeout

    def scan(self, repo_path: str | Path) -> List[Dict[str, Any]]:
        """Run Gitleaks scan on repository.

        Args:
            repo_path: Path to repository to scan

        Returns:
            List of findings in standard format (with secrets redacted)
        """
        repo_path = Path(repo_path)

        try:
            # Build gitleaks command
            cmd = [
                "gitleaks",
                "detect",
                "--source",
                str(repo_path),
                "--json",
                "--no-banner",
            ]

            # Add config if it exists
            if self.ignore_path.exists():
                # Note: Gitleaks uses --config-path or .gitleaksignore in repo root
                # For now, we'll let gitleaks use its default config
                pass

            logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )

            # Gitleaks returns non-zero exit code when findings are detected
            # Exit code 1 = findings found, 0 = no findings, 2 = error
            if result.returncode == 2:
                logger.error(f"Gitleaks error: {result.stderr[:200]}")
                return []

            # Parse JSON output
            output = result.stdout.strip()
            if not output:
                # No findings or empty output
                return []

            try:
                # Gitleaks outputs one JSON object per line
                findings = []
                for line in output.split("\n"):
                    if line.strip():
                        data = json.loads(line)
                        finding = self._to_finding(data)
                        if finding:
                            findings.append(finding)

                logger.info(f"Gitleaks found {len(findings)} secrets")
                return findings

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gitleaks JSON output: {e}")
                return []

        except subprocess.TimeoutExpired:
            logger.error(f"Gitleaks timed out after {self.timeout}s")
            return []
        except FileNotFoundError:
            logger.error(
                "Gitleaks command not found. Install with: brew install gitleaks or "
                "download from https://github.com/gitleaks/gitleaks"
            )
            return []
        except Exception as e:
            logger.error(f"Error running Gitleaks: {e}", exc_info=True)
            return []

    def _to_finding(self, gitleaks_match: Dict[str, Any]) -> Dict[str, Any] | None:
        """Convert Gitleaks match to standard finding format.

        Args:
            gitleaks_match: Gitleaks JSON match object

        Returns:
            Standard finding dictionary (with secrets redacted) or None if invalid
        """
        try:
            rule_id = gitleaks_match.get("RuleID", "")
            file_path = gitleaks_match.get("File", "")
            line_num = gitleaks_match.get("StartLine", 0)
            secret = gitleaks_match.get("Secret", "")
            match = gitleaks_match.get("Match", "")
            entropy = gitleaks_match.get("Entropy", 0.0)

            # Redact secret value (replace with placeholder)
            redacted_secret = self._redact_secret(secret or match)

            # Get code snippet (redacted)
            code_snippet = ""
            if "Line" in gitleaks_match:
                code_snippet = self._redact_secret(str(gitleaks_match["Line"]))

            finding = {
                "finding": f"Secret detected: {rule_id}",
                "evidence": [
                    {
                        "path": file_path,
                        "lines": f"L{line_num}",
                        "why_relevant": f"Gitleaks detected potential secret with entropy {entropy:.2f}",
                        "code_snippet": code_snippet or "[REDACTED]",
                    }
                ],
                "confidence": min(0.7 + (entropy / 10), 0.95),  # Higher entropy = higher confidence
                "tool": "gitleaks",
                "severity": "critical",  # Secrets are always critical
                "rule_id": rule_id,
                "remediation": f"Remove secret from code and rotate credentials. Match: {redacted_secret}",
            }

            return finding

        except (KeyError, AttributeError) as e:
            logger.warning(f"Failed to convert Gitleaks match: {e}")
            return None

    def _redact_secret(self, secret: str) -> str:
        """Redact secret value for safe logging.

        Args:
            secret: Secret string to redact

        Returns:
            Redacted string (first 4 chars + ... + last 4 chars, or [REDACTED])
        """
        if not secret:
            return "[REDACTED]"

        secret_str = str(secret)
        if len(secret_str) <= 8:
            return "[REDACTED]"

        # Show first 4 and last 4 characters, mask the rest
        return f"{secret_str[:4]}...{secret_str[-4:]}"

