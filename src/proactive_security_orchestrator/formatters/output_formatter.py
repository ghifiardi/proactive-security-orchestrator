"""Output formatters for security findings."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from proactive_security_orchestrator import __version__

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
                            "version": __version__,
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
            
            # Get human-readable finding message
            finding_message = finding.get("finding", "")
            if not finding_message or finding_message == rule_id:
                # Fallback: create readable name from rule_id
                finding_message = rule_id.split(".")[-1].replace("-", " ").title()

            # Create rule entry if not exists
            if rule_id not in rules_dict:
                remediation = finding.get("remediation", "")
                if not remediation:
                    remediation = f"Review and fix the security issue: {finding_message}"
                
                # Create better rule name from rule_id
                rule_name = finding_message
                if rule_name == rule_id or not rule_name:
                    # Parse rule_id to create readable name
                    parts = rule_id.split(".")
                    if len(parts) >= 2:
                        rule_name = parts[-1].replace("-", " ").title()
                    else:
                        rule_name = rule_id
                
                rules_dict[rule_id] = {
                    "id": rule_id,
                    "name": rule_name,
                    "shortDescription": {
                        "text": finding_message
                    },
                    "fullDescription": {
                        "text": finding_message
                    },
                    "help": {
                        "text": remediation,
                        "markdown": remediation
                    },
                    "properties": {
                        "tags": [finding.get("tool", "unknown"), severity],
                        "precision": "high" if finding.get("confidence", 0.5) > 0.7 else "medium",
                    },
                }

            # Create result entry for each evidence
            evidence_list = finding.get("evidence", [])
            for evidence in evidence_list:
                path = evidence.get("path", "")
                lines_str = evidence.get("lines", "")
                why_relevant = evidence.get("why_relevant", "")
                code_snippet = evidence.get("code_snippet", "")

                # Parse line numbers
                line_num = 0
                end_line_num = None
                if lines_str:
                    try:
                        # Handle "L100" or "L100-L145" format
                        line_parts = lines_str.replace("L", "").split("-")
                        line_num = int(line_parts[0])
                        if len(line_parts) > 1:
                            end_line_num = int(line_parts[1].replace("L", ""))
                    except (ValueError, AttributeError):
                        pass

                # Build message with context
                message_text = finding_message
                if why_relevant and why_relevant != finding_message:
                    message_text = f"{finding_message}. {why_relevant}"

                # Build region with code snippet if available
                region = {
                    "startLine": line_num,
                }
                if end_line_num and end_line_num != line_num:
                    region["endLine"] = end_line_num
                
                if code_snippet:
                    region["snippet"] = {
                        "text": code_snippet
                    }

                result = {
                    "ruleId": rule_id,
                    "level": sarif_severity,
                    "message": {
                        "text": message_text,
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": path,
                                },
                                "region": region,
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
    def to_pdf(findings: List[Dict[str, Any]]) -> bytes:
        """Convert findings to PDF format with bullet points and structured layout.

        Args:
            findings: List of finding dictionaries

        Returns:
            PDF file as bytes

        Raises:
            ImportError: If reportlab is not installed
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF output. Install with: pip install reportlab"
            )

        from io import BytesIO

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1,  # Center
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
        )

        severity_colors = {
            "critical": colors.HexColor('#d32f2f'),
            "high": colors.HexColor('#f57c00'),
            "medium": colors.HexColor('#fbc02d'),
            "low": colors.HexColor('#1976d2'),
            "info": colors.HexColor('#616161'),
        }

        # Title
        story.append(Paragraph("Security Scan Report", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Summary section
        total = len(findings)
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in findings:
            severity = finding.get("severity", "info").lower()
            counts[severity] = counts.get(severity, 0) + 1

        summary_data = [
            ["Total Findings", str(total)],
            ["Critical", str(counts["critical"])],
            ["High", str(counts["high"])],
            ["Medium", str(counts["medium"])],
            ["Low", str(counts["low"])],
            ["Info", str(counts["info"])],
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))

        # Findings section
        story.append(Paragraph("Security Findings", heading_style))
        story.append(Spacer(1, 0.1*inch))

        if not findings:
            story.append(Paragraph("✓ No security findings detected.", styles['Normal']))
        else:
            for idx, finding in enumerate(findings, 1):
                severity = finding.get("severity", "info").lower()
                finding_text = finding.get("finding", "Unknown issue")
                rule_id = finding.get("rule_id", "unknown")
                tool = finding.get("tool", "unknown")
                remediation = finding.get("remediation", "")

                # Finding header with severity color
                severity_color = severity_colors.get(severity, colors.grey)
                finding_title = f"<b>{idx}. {finding_text}</b>"
                story.append(Paragraph(finding_title, heading_style))
                story.append(Spacer(1, 0.05*inch))

                # Metadata bullet points
                metadata_items = [
                    f"<b>Severity:</b> {severity.upper()}",
                    f"<b>Tool:</b> {tool}",
                    f"<b>Rule ID:</b> {rule_id}",
                ]

                for item in metadata_items:
                    story.append(Paragraph(f"• {item}", styles['Normal']))
                    story.append(Spacer(1, 0.02*inch))

                story.append(Spacer(1, 0.1*inch))

                # Evidence section
                evidence_list = finding.get("evidence", [])
                if evidence_list:
                    story.append(Paragraph("<b>Locations:</b>", styles['Normal']))
                    story.append(Spacer(1, 0.05*inch))

                    for evidence in evidence_list:
                        path = evidence.get("path", "")
                        lines = evidence.get("lines", "")
                        why = evidence.get("why_relevant", "")
                        code = evidence.get("code_snippet", "")

                        location_text = f"• <b>File:</b> {path} <b>({lines})</b>"
                        story.append(Paragraph(location_text, styles['Normal']))
                        story.append(Spacer(1, 0.02*inch))

                        if why:
                            story.append(Paragraph(f"  <i>Reason:</i> {why}", styles['Normal']))
                            story.append(Spacer(1, 0.02*inch))

                        if code:
                            # Code snippet in monospace
                            code_style = ParagraphStyle(
                                'Code',
                                parent=styles['Normal'],
                                fontName='Courier',
                                fontSize=8,
                                leftIndent=20,
                                backColor=colors.HexColor('#f5f5f5'),
                                borderPadding=5,
                            )
                            # Escape HTML and format code
                            code_escaped = code.replace('<', '&lt;').replace('>', '&gt;')
                            story.append(Paragraph(f"<font face='Courier'>{code_escaped}</font>", code_style))
                            story.append(Spacer(1, 0.05*inch))

                # Remediation section
                if remediation:
                    story.append(Spacer(1, 0.1*inch))
                    remediation_style = ParagraphStyle(
                        'Remediation',
                        parent=styles['Normal'],
                        leftIndent=20,
                        backColor=colors.HexColor('#e8f5e9'),
                        borderPadding=8,
                        borderColor=colors.HexColor('#4caf50'),
                        borderWidth=1,
                    )
                    story.append(Paragraph(f"<b>Remediation:</b> {remediation}", remediation_style))

                story.append(Spacer(1, 0.2*inch))

                # Add page break if not last finding
                if idx < len(findings):
                    story.append(PageBreak())

        # Footer with timestamp
        story.append(Spacer(1, 0.3*inch))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1,  # Center
        )
        story.append(Paragraph(
            f"Generated by Proactive Security Orchestrator v{__version__} on {timestamp}",
            footer_style
        ))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def save_to_file(
        findings: List[Dict[str, Any]], format: str, output_path: Path | str
    ) -> None:
        """Save findings to file in specified format.

        Args:
            findings: List of finding dictionaries
            format: Output format ('json', 'sarif', 'html', 'pdf')
            output_path: Path to output file
        """
        output_path = Path(output_path)

        formatter = OutputFormatter()
        if format == "json":
            content = formatter.to_json(findings)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
        elif format == "sarif":
            content = formatter.to_sarif(findings)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
        elif format == "html":
            content = formatter.to_html(findings)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
        elif format == "pdf":
            pdf_content = formatter.to_pdf(findings)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(pdf_content)
        else:
            raise ValueError(f"Unsupported format: {format}. Supported: json, sarif, html, pdf")

