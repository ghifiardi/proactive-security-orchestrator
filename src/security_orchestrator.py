"""Parent security orchestrator coordinating child agents."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from src.tools.gitleaks_scanner import GitleaksScanner
from src.tools.semgrep_analyzer import SemgrepAnalyzer
from src.validators.finding_validator import FindingValidator

logger = logging.getLogger(__name__)


class SecurityScanner:
    """Parent orchestrator for security scanning."""

    def __init__(
        self,
        config_dir: Path | str = "config",
        timeout: int = 60,
        env: Dict[str, str] | None = None,
    ) -> None:
        """Initialize security scanner.

        Args:
            config_dir: Root directory containing tool configs
            timeout: Timeout in seconds for tool execution
            env: Environment variables (for feature flags)
        """
        self.config_dir = Path(config_dir)
        self.timeout = timeout
        self.env = env or {}

        # Feature flags from environment
        self.enable_semgrep = os.getenv("ENABLE_SEMGREP", "true").lower() == "true"
        self.enable_gitleaks = os.getenv("ENABLE_GITLEAKS", "true").lower() == "true"
        self.strict_validation = os.getenv("STRICT_VALIDATION", "false").lower() == "true"

        # Override with provided env dict
        if env:
            self.enable_semgrep = env.get("ENABLE_SEMGREP", str(self.enable_semgrep)).lower() == "true"
            self.enable_gitleaks = env.get("ENABLE_GITLEAKS", str(self.enable_gitleaks)).lower() == "true"
            self.strict_validation = env.get("STRICT_VALIDATION", str(self.strict_validation)).lower() == "true"

        # Check kill switch
        if os.getenv("ORCHESTRATOR_DISABLED", "false").lower() == "true":
            logger.warning("Orchestrator disabled via ORCHESTRATOR_DISABLED")
            self.enable_semgrep = False
            self.enable_gitleaks = False

        # Initialize child agents
        semgrep_config = self.config_dir / "semgrep"
        gitleaks_config = self.config_dir / "gitleaks"

        self.semgrep = SemgrepAnalyzer(semgrep_config, timeout=self.timeout) if self.enable_semgrep else None
        self.gitleaks = GitleaksScanner(gitleaks_config, timeout=self.timeout) if self.enable_gitleaks else None

        # Initialize validator
        self.validator = FindingValidator()

        logger.info(
            f"SecurityScanner initialized: Semgrep={self.enable_semgrep}, "
            f"Gitleaks={self.enable_gitleaks}, Strict={self.strict_validation}"
        )

    def scan(self, repo_path: str | Path, targets: List[str] | None = None) -> List[Dict[str, Any]]:
        """Run security scan on repository.

        Args:
            repo_path: Path to repository to scan
            targets: Optional list of specific targets (files/directories). Not used yet.

        Returns:
            List of validated, de-duplicated findings
        """
        repo_path = Path(repo_path)

        if not repo_path.exists():
            logger.error(f"Repository path does not exist: {repo_path}")
            return []

        logger.info(f"Starting security scan on: {repo_path}")

        all_findings: List[Dict[str, Any]] = []

        # Run Semgrep (child agent 1)
        if self.semgrep:
            try:
                logger.debug("Running Semgrep analyzer...")
                semgrep_findings = self.semgrep.analyze(repo_path)
                all_findings.extend(semgrep_findings)
                logger.info(f"Semgrep found {len(semgrep_findings)} findings")
            except Exception as e:
                logger.error(f"Semgrep failed: {e}", exc_info=True)
                if self.strict_validation:
                    raise

        # Run Gitleaks (child agent 2)
        if self.gitleaks:
            try:
                logger.debug("Running Gitleaks scanner...")
                gitleaks_findings = self.gitleaks.scan(repo_path)
                all_findings.extend(gitleaks_findings)
                logger.info(f"Gitleaks found {len(gitleaks_findings)} findings")
            except Exception as e:
                logger.error(f"Gitleaks failed: {e}", exc_info=True)
                if self.strict_validation:
                    raise

        # If no tools enabled, return empty
        if not self.enable_semgrep and not self.enable_gitleaks:
            logger.warning("No scanning tools enabled. Returning empty findings.")
            return []

        # Validate and de-duplicate all findings
        logger.debug(f"Validating {len(all_findings)} total findings...")
        validated_findings = self.validator.validate_all(all_findings)

        # Log metrics
        self._log_orchestration_metrics(all_findings, validated_findings)

        logger.info(f"Scan complete. {len(validated_findings)} validated findings (from {len(all_findings)} raw)")

        return validated_findings

    def _log_orchestration_metrics(
        self, raw_findings: List[Dict[str, Any]], validated_findings: List[Dict[str, Any]]
    ) -> None:
        """Log orchestration metrics for observability.

        Args:
            raw_findings: Findings before validation
            validated_findings: Findings after validation
        """
        # Count by tool
        tool_counts: Dict[str, int] = {}
        for finding in validated_findings:
            tool = finding.get("tool", "unknown")
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

        # Count by severity
        severity_counts: Dict[str, int] = {}
        for finding in validated_findings:
            severity = finding.get("severity", "info")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        logger.info(
            f"Orchestration metrics: "
            f"Raw={len(raw_findings)}, Validated={len(validated_findings)}, "
            f"Tools={tool_counts}, Severity={severity_counts}"
        )

