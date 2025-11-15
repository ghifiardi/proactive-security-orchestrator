"""Finding validator for security findings."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Set

import jsonschema

logger = logging.getLogger(__name__)


class FindingValidator:
    """Validates security findings against JSON schema and de-duplicates."""

    def __init__(self, schema_path: Path | None = None) -> None:
        """Initialize validator with schema.

        Args:
            schema_path: Path to JSON schema file. Defaults to contracts/child_agent_schema.json
        """
        if schema_path is None:
            # Default to contracts directory bundled within the package
            package_root = Path(__file__).resolve().parent.parent
            schema_path = package_root / "contracts" / "child_agent_schema.json"

        self.schema_path = schema_path
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

        self.validator = jsonschema.Draft7Validator(self.schema)

    def validate_all(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and de-duplicate findings.

        Args:
            findings: List of finding dictionaries to validate

        Returns:
            Validated, de-duplicated, sorted findings list
        """
        valid_findings: List[Dict[str, Any]] = []

        for finding in findings:
            try:
                self.validator.validate(finding)
                valid_findings.append(finding)
            except jsonschema.ValidationError as e:
                logger.warning(
                    f"Skipped invalid finding: {e.message}. "
                    f"Finding: {finding.get('rule_id', 'unknown')}"
                )

        # De-duplicate by (path, line, rule_id)
        deduplicated = self._deduplicate(valid_findings)

        # Sort by severity (critical → info) then by line number
        sorted_findings = self._sort_by_severity(deduplicated)

        return sorted_findings

    def _deduplicate(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate findings based on path, line, and rule_id.

        Args:
            findings: List of findings to de-duplicate

        Returns:
            De-duplicated list
        """
        seen: Set[tuple[str, str, str]] = set()
        unique_findings: List[Dict[str, Any]] = []

        for finding in findings:
            # Extract evidence for path/line matching
            evidence = finding.get("evidence", [])
            if not evidence:
                # If no evidence, use finding-level path if available
                path = finding.get("path", "")
                lines = finding.get("lines", "")
            else:
                # Use first evidence entry
                path = evidence[0].get("path", "")
                lines = evidence[0].get("lines", "")

            rule_id = finding.get("rule_id", "")

            key = (path, lines, rule_id)
            if key not in seen:
                seen.add(key)
                unique_findings.append(finding)

        return unique_findings

    def _sort_by_severity(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort findings by severity, then by line number.

        Args:
            findings: List of findings to sort

        Returns:
            Sorted list
        """
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

        def sort_key(finding: Dict[str, Any]) -> tuple[int, int]:
            severity = finding.get("severity", "info").lower()
            severity_score = severity_order.get(severity, 4)

            # Extract line number from evidence or finding
            line_num = 0
            evidence = finding.get("evidence", [])
            if evidence:
                lines_str = evidence[0].get("lines", "")
                # Extract first number from "L100-L145" or "L50"
                if lines_str:
                    try:
                        line_num = int(lines_str.replace("L", "").split("-")[0])
                    except (ValueError, AttributeError):
                        pass

            return (severity_score, line_num)

        return sorted(findings, key=sort_key)

