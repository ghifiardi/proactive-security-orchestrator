"""Semgrep analyzer child agent."""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SemgrepAnalyzer:
    """Child agent for Semgrep static analysis."""

    def __init__(self, config_dir: Path | str, timeout: int = 60) -> None:
        """Initialize Semgrep analyzer.

        Args:
            config_dir: Directory containing Semgrep config (rules.yaml)
            timeout: Timeout in seconds for Semgrep execution
        """
        self.config_dir = Path(config_dir)
        self.rules_path = self.config_dir / "rules.yaml"
        self.timeout = timeout

    def analyze(self, repo_path: str | Path) -> List[Dict[str, Any]]:
        """Run Semgrep analysis on repository.

        Args:
            repo_path: Path to repository to scan

        Returns:
            List of findings in standard format
        """
        repo_path = Path(repo_path)

        try:
            # Run semgrep with JSON output
            # Use custom rules if available, otherwise use Semgrep's default security rules
            if self.rules_path.exists():
                cmd = [
                    "semgrep",
                    "--config",
                    str(self.rules_path),
                    "--json",
                    str(repo_path),
                ]
            else:
                logger.info(f"Semgrep rules not found at {self.rules_path}. Using default security rules.")
                cmd = [
                    "semgrep",
                    "--config", "auto",  # Use Semgrep's auto-config (security-focused rules)
                    "--json",
                    str(repo_path),
                ]

            logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )

            if result.returncode != 0:
                logger.warning(
                    f"Semgrep exited with code {result.returncode}. "
                    f"stderr: {result.stderr[:200]}"
                )
                # Semgrep may return non-zero for findings, try to parse anyway
                if not result.stdout.strip():
                    return []

            # Parse JSON output
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Semgrep JSON output: {e}")
                return []

            # Convert Semgrep results to standard finding format
            findings = []
            results = data.get("results", [])

            for result in results:
                finding = self._to_finding(result)
                if finding:
                    findings.append(finding)

            logger.info(f"Semgrep found {len(findings)} issues")
            return findings

        except subprocess.TimeoutExpired:
            logger.error(f"Semgrep timed out after {self.timeout}s")
            return []
        except FileNotFoundError:
            logger.error("Semgrep command not found. Install with: pip install semgrep or brew install semgrep")
            return []
        except Exception as e:
            logger.error(f"Error running Semgrep: {e}", exc_info=True)
            return []

    def _to_finding(self, semgrep_result: Dict[str, Any]) -> Dict[str, Any] | None:
        """Convert Semgrep result to standard finding format.

        Args:
            semgrep_result: Semgrep JSON result object

        Returns:
            Standard finding dictionary or None if invalid
        """
        try:
            check_id = semgrep_result.get("check_id", "")
            path = semgrep_result.get("path", "")
            start = semgrep_result.get("start", {})
            end = semgrep_result.get("end", {})
            message = semgrep_result.get("message", "")
            severity = semgrep_result.get("extra", {}).get("severity", "medium")

            start_line = start.get("line", 0)
            end_line = end.get("line", start_line)

            # Format lines as "L100-L145" or "L50"
            if start_line == end_line:
                lines_str = f"L{start_line}"
            else:
                lines_str = f"L{start_line}-L{end_line}"

            # Map Semgrep severity to standard severity
            severity_map = {
                "ERROR": "critical",
                "WARNING": "high",
                "INFO": "medium",
            }
            mapped_severity = severity_map.get(severity.upper(), "medium")

            # Get code snippet (first 2 lines max)
            code_snippet = ""
            if "extra" in semgrep_result and "lines" in semgrep_result["extra"]:
                lines = semgrep_result["extra"]["lines"].split("\n")[:2]
                code_snippet = "\n".join(lines).strip()

            finding = {
                "finding": message or check_id,
                "evidence": [
                    {
                        "path": path,
                        "lines": lines_str,
                        "why_relevant": f"Semgrep rule {check_id} detected this issue",
                        "code_snippet": code_snippet,
                    }
                ],
                "confidence": 0.8,  # Semgrep rules are generally reliable
                "tool": "semgrep",
                "severity": mapped_severity,
                "rule_id": check_id,
                "remediation": f"Review and fix according to rule {check_id}",
            }

            return finding

        except (KeyError, AttributeError) as e:
            logger.warning(f"Failed to convert Semgrep result: {e}")
            return None

