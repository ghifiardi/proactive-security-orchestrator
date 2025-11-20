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
            extra = semgrep_result.get("extra", {})
            
            # Extract message - prefer Semgrep's message, fallback to metadata description
            message = semgrep_result.get("message", "")
            if not message and "metadata" in extra:
                message = extra["metadata"].get("description", "")
            if not message:
                # Create readable message from rule ID
                message = self._format_rule_name(check_id)
            
            severity = extra.get("severity", "medium")

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

            # Get code snippet (first 3 lines max)
            code_snippet = ""
            if "lines" in extra:
                lines = extra["lines"].split("\n")[:3]
                code_snippet = "\n".join(lines).strip()

            # Extract remediation guidance
            remediation = self._extract_remediation(extra, check_id)
            
            # Extract why_relevant from metadata
            why_relevant = ""
            if "metadata" in extra:
                why_relevant = extra["metadata"].get("cwe", "")
                if why_relevant:
                    why_relevant = f"CWE-{why_relevant}: {extra['metadata'].get('cwe_description', 'Security vulnerability detected')}"
                else:
                    why_relevant = extra["metadata"].get("description", f"Semgrep rule {check_id} detected this security issue")
            else:
                why_relevant = f"Semgrep security rule detected: {check_id}"

            finding = {
                "finding": message,
                "evidence": [
                    {
                        "path": path,
                        "lines": lines_str,
                        "why_relevant": why_relevant,
                        "code_snippet": code_snippet,
                    }
                ],
                "confidence": 0.8,  # Semgrep rules are generally reliable
                "tool": "semgrep",
                "severity": mapped_severity,
                "rule_id": check_id,
                "remediation": remediation,
            }

            return finding

        except (KeyError, AttributeError) as e:
            logger.warning(f"Failed to convert Semgrep result: {e}")
            return None

    def _format_rule_name(self, rule_id: str) -> str:
        """Convert technical rule ID to human-readable name.
        
        Args:
            rule_id: Semgrep rule ID like "python.lang.security.deserialization.pickle.avoid-pickle"
            
        Returns:
            Human-readable rule name
        """
        # Split by dots and capitalize
        parts = rule_id.split(".")
        if len(parts) >= 2:
            # Get the last meaningful parts
            category = parts[-2] if len(parts) >= 2 else ""
            rule_name = parts[-1].replace("-", " ").title()
            
            # Map common categories
            category_map = {
                "security": "Security",
                "secrets": "Secret Detection",
                "deserialization": "Deserialization",
                "xss": "XSS",
                "injection": "Injection",
            }
            category = category_map.get(category, category.title())
            
            return f"{category}: {rule_name}"
        return rule_id.replace(".", " ").replace("-", " ").title()

    def _extract_remediation(self, extra: Dict[str, Any], check_id: str) -> str:
        """Extract remediation guidance from Semgrep metadata.
        
        Args:
            extra: Semgrep extra metadata
            check_id: Rule ID
            
        Returns:
            Remediation guidance text
        """
        # Try to get remediation from metadata
        if "metadata" in extra:
            metadata = extra["metadata"]
            
            # Check for remediation field
            if "remediation" in metadata:
                return metadata["remediation"]
            
            # Check for owasp or cwe descriptions
            if "owasp" in metadata:
                return f"Follow OWASP guidelines: {metadata.get('owasp', '')}"
            
            # Generate based on rule type
            if "deserialization" in check_id.lower() or "pickle" in check_id.lower():
                return "Avoid using pickle for deserializing untrusted data. Use JSON or other safe serialization formats. If pickle is necessary, ensure data comes from trusted sources only."
            
            if "xss" in check_id.lower() or "jinja2" in check_id.lower():
                return "Use Flask's auto-escaping or manually escape user input before rendering in templates. Never render user input directly without escaping."
            
            if "secrets" in check_id.lower() or "private-key" in check_id.lower():
                return "Remove hardcoded secrets, API keys, or private keys from code. Use environment variables, secret management systems, or secure vaults. Rotate any exposed credentials immediately."
            
            if "injection" in check_id.lower():
                return "Use parameterized queries or prepared statements. Never concatenate user input directly into queries or commands."
        
        # Default generic remediation
        return f"Review and fix the security issue identified by rule: {check_id}. Refer to security best practices for your language and framework."

