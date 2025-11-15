"""Output formatters for security findings."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Template for HTML dashboard
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Scan Results</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }}
        .stat .number {{ font-size: 2em; font-weight: bold; color: #007acc; }}
        .stat .label {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
        .severity-critical {{ border-left: 4px solid #d32f2f; }}
        .severity-high {{ border-left: 4px solid #f57c00; }}
        .severity-medium {{ border-left: 4px solid #fbc02d; }}
        .severity-low {{ border-left: 4px solid #1976d2; }}
        .severity-info {{ border-left: 4px solid #616161; }}
        .finding {{ margin: 15px 0; padding: 15px; background: #fafafa; border-radius: 4px; }}
        .finding-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .finding-title {{ font-weight: bold; color: #333; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 3px; font-size: 0.85em; font-weight: 500; }}
        .badge-critical {{ background: #ffebee; color: #d32f2f; }}
        .badge-high {{ background: #fff3e0; color: #f57c00; }}
        .badge-medium {{ background: #fffde7; color: #fbc02d; }}
        .badge-low {{ background: #e3f2fd; color: #1976d2; }}
        .badge-info {{ background: #f5f5f5; color: #616161; }}
        .evidence {{ margin-top: 10px; padding: 10px; background: #fff; border: 1px solid #ddd; border-radius: 4px; }}
        .code {{ font-family: 'Courier New', monospace; font-size: 0.9em; background: #f5f5f5; padding: 8px; border-radius: 3px; margin-top: 5px; }}
        .meta {{ font-size: 0.85em; color: #666; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Security Scan Results</h1>
        <div class="meta">Generated: {timestamp}</div>
        
        <div class="summary">
            <div class="stat">
                <div class="number">{total}</div>
                <div class="label">Total Findings</div>
            </div>
            <div class="stat">
                <div class="number">{critical}</div>
                <div class="label">Critical</div>
            </div>
            <div class="stat">
                <div class="number">{high}</div>
                <div class="label">High</div>
            </div>
            <div class="stat">
                <div class="number">{medium}</div>
                <div class="label">Medium</div>
            </div>
            <div class="stat">
                <div class="number">{low}</div>
                <div class="label">Low</div>
            </div>
        </div>
        
        <h2>Findings</h2>
        {findings_html}
    </div>
</body>
</html>
"""


class OutputFormatter:
    """Formats security findings into multiple output formats."""

    @staticmethod
    def to_json(findings: List[Dict[str, Any]]) -> str:
        """Convert findings to JSON format.

        Args:
            findings: List of finding dictionaries

        Returns:
            Pretty-printed JSON string
        """
        return json.dumps(findings, indent=2, ensure_ascii=False)

    @staticmethod
    def to_sarif(findings: List[Dict[str, Any]]) -> str:
        """Convert findings to SARIF 2.1.0 format.

        Args:
            findings: List of finding dictionaries

        Returns:
            SARIF JSON string
        """
        # SARIF structure
        sarif = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Proactive Security Orchestrator",
                            "version": "1.0.0",
                            "informationUri": "https://github.com/ghifiardi/proactive-security-orchestrator",
                            "rules": [],
                        }
                    },
                    "results": [],
                }
            ],
        }

        # Map severity levels
        severity_map = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
            "info": "note",
        }

        # Collect unique rules
        rules_dict: Dict[str, Dict[str, Any]] = {}
        results = []

        for finding in findings:
            rule_id = finding.get("rule_id", "unknown")
            severity = finding.get("severity", "medium").lower()
            sarif_severity = severity_map.get(severity, "warning")

            # Create rule entry if not exists
            if rule_id not in rules_dict:
                rules_dict[rule_id] = {
                    "id": rule_id,
                    "name": finding.get("finding", rule_id),
                    "shortDescription": {"text": finding.get("finding", "")},
                    "help": {
                        "text": finding.get("remediation", ""),
                    },
                    "properties": {
                        "tags": [finding.get("tool", "unknown"), severity],
                    },
                }

            # Create result entry for each evidence
            evidence_list = finding.get("evidence", [])
            for evidence in evidence_list:
                path = evidence.get("path", "")
                lines_str = evidence.get("lines", "")

                # Parse line numbers
                line_num = 0
                if lines_str:
                    try:
                        line_num = int(lines_str.replace("L", "").split("-")[0])
                    except (ValueError, AttributeError):
                        pass

                result = {
                    "ruleId": rule_id,
                    "level": sarif_severity,
                    "message": {
                        "text": finding.get("finding", ""),
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": path,
                                },
                                "region": {
                                    "startLine": line_num,
                                },
                            },
                        }
                    ],
                    "properties": {
                        "tool": finding.get("tool", "unknown"),
                        "confidence": finding.get("confidence", 0.5),
                    },
                }

                results.append(result)

        sarif["runs"][0]["tool"]["driver"]["rules"] = list(rules_dict.values())
        sarif["runs"][0]["results"] = results

        return json.dumps(sarif, indent=2, ensure_ascii=False)

    @staticmethod
    def to_html(findings: List[Dict[str, Any]]) -> str:
        """Generate HTML dashboard for human review.

        Args:
            findings: List of finding dictionaries

        Returns:
            HTML string
        """
        # Count findings by severity
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in findings:
            severity = finding.get("severity", "info").lower()
            counts[severity] = counts.get(severity, 0) + 1

        total = len(findings)

        # Generate HTML for each finding
        findings_html = ""
        for finding in findings:
            severity = finding.get("severity", "info").lower()
            rule_id = finding.get("rule_id", "unknown")
            tool = finding.get("tool", "unknown")
            finding_text = finding.get("finding", "")

            # Evidence HTML
            evidence_html = ""
            evidence_list = finding.get("evidence", [])
            for evidence in evidence_list:
                path = evidence.get("path", "")
                lines = evidence.get("lines", "")
                why = evidence.get("why_relevant", "")
                code = evidence.get("code_snippet", "")

                evidence_html += f"""
                <div class="evidence">
                    <div><strong>{path}</strong> <span style="color: #666;">({lines})</span></div>
                    <div style="margin-top: 5px; color: #666;">{why}</div>
                    {f'<div class="code">{code}</div>' if code else ''}
                </div>
                """

            # Remediation
            remediation = finding.get("remediation", "")
            remediation_html = f'<div class="meta"><strong>Remediation:</strong> {remediation}</div>' if remediation else ""

            finding_html = f"""
            <div class="finding severity-{severity}">
                <div class="finding-header">
                    <div class="finding-title">{finding_text}</div>
                    <div>
                        <span class="badge badge-{severity}">{severity.upper()}</span>
                        <span class="badge">{tool}</span>
                    </div>
                </div>
                <div class="meta">Rule ID: {rule_id}</div>
                {evidence_html}
                {remediation_html}
            </div>
            """

            findings_html += finding_html

        # If no findings
        if not findings_html:
            findings_html = '<div class="finding"><div>No security findings detected.</div></div>'

        # Format timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Fill template
        html = HTML_TEMPLATE.format(
            timestamp=timestamp,
            total=total,
            critical=counts["critical"],
            high=counts["high"],
            medium=counts["medium"],
            low=counts["low"],
            findings_html=findings_html,
        )

        return html

    @staticmethod
    def save_to_file(
        findings: List[Dict[str, Any]], format: str, output_path: Path | str
    ) -> None:
        """Save findings to file in specified format.

        Args:
            findings: List of finding dictionaries
            format: Output format ('json', 'sarif', 'html')
            output_path: Path to output file
        """
        output_path = Path(output_path)

        formatter = OutputFormatter()
        if format == "json":
            content = formatter.to_json(findings)
        elif format == "sarif":
            content = formatter.to_sarif(findings)
        elif format == "html":
            content = formatter.to_html(findings)
        else:
            raise ValueError(f"Unsupported format: {format}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

