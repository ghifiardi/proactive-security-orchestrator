"""CLI entry point for security scanner."""

import logging
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler

from proactive_security_orchestrator.formatters.output_formatter import OutputFormatter
from proactive_security_orchestrator.security_orchestrator import SecurityScanner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)
console = Console()
app = typer.Typer(help="Proactive Security Orchestrator - Unified security scanning")


@app.command()
def scan(
    repo_path: str = typer.Argument(..., help="Path to repository to scan"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, sarif, html, pdf"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path (default: stdout for json, file for sarif/html)"),
    config_dir: Path = typer.Option("config", "--config", "-c", help="Configuration directory"),
    timeout: int = typer.Option(60, "--timeout", "-t", help="Timeout in seconds for each tool"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    fail_on_critical: bool = typer.Option(True, "--fail-on-critical/--no-fail-on-critical", help="Exit with code 1 if critical findings are detected (default: True)"),
):
    """Scan repository for security vulnerabilities and secrets.

    Example:
        $ security-scan /path/to/repo --format json --output findings.json
        $ security-scan /path/to/repo --format sarif --output findings.sarif
        $ security-scan /path/to/repo --format html --output dashboard.html
        $ security-scan /path/to/repo --format pdf --output report.pdf
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate format
    valid_formats = ["json", "sarif", "html", "pdf"]
    if format.lower() not in valid_formats:
        console.print(f"[red]Error: Invalid format '{format}'. Must be one of: {', '.join(valid_formats)}[/red]")
        sys.exit(1)

    # Validate repo path
    repo_path_obj = Path(repo_path)
    if not repo_path_obj.exists():
        console.print(f"[red]Error: Repository path does not exist: {repo_path}[/red]")
        sys.exit(1)

    try:
        # Initialize scanner
        console.print(f"[blue]Initializing security scanner...[/blue]")
        scanner = SecurityScanner(config_dir=config_dir, timeout=timeout)

        # Run scan
        console.print(f"[blue]Scanning repository: {repo_path}[/blue]")
        findings = scanner.scan(repo_path_obj)

        if not findings:
            console.print("[green]✓ No security findings detected![/green]")
        else:
            console.print(f"[yellow]Found {len(findings)} security findings[/yellow]")

            # Count by severity
            severity_counts = {}
            for finding in findings:
                severity = finding.get("severity", "info")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            console.print(f"  Critical: {severity_counts.get('critical', 0)}")
            console.print(f"  High: {severity_counts.get('high', 0)}")
            console.print(f"  Medium: {severity_counts.get('medium', 0)}")
            console.print(f"  Low: {severity_counts.get('low', 0)}")
            console.print(f"  Info: {severity_counts.get('info', 0)}")

        # Format and save output
        formatter = OutputFormatter()

        if output:
            # Save to file
            console.print(f"[blue]Saving {format.upper()} output to: {output}[/blue]")
            formatter.save_to_file(findings, format.lower(), output)
            console.print(f"[green]✓ Output saved to {output}[/green]")
        else:
            # Print to stdout (JSON only)
            if format.lower() == "json":
                json_output = formatter.to_json(findings)
                console.print(json_output)
            else:
                # For SARIF/HTML/PDF, default to file if output not specified
                default_output = f"findings.{format.lower()}"
                console.print(f"[yellow]No output file specified. Saving to: {default_output}[/yellow]")
                formatter.save_to_file(findings, format.lower(), default_output)
                console.print(f"[green]✓ Output saved to {default_output}[/green]")

        # Exit with non-zero if critical findings (unless --no-fail-on-critical is set)
        if any(f.get("severity") == "critical" for f in findings):
            console.print("[red]⚠ Critical findings detected![/red]")
            if fail_on_critical:
                sys.exit(1)
            else:
                console.print("[yellow]Continuing with exit code 0 (--no-fail-on-critical enabled)[/yellow]")
                sys.exit(0)
        elif findings:
            sys.exit(0)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Scan failed")
        sys.exit(1)


@app.command()
def version():
    """Show version information."""
    from proactive_security_orchestrator import __version__

    console.print(f"Proactive Security Orchestrator v{__version__}")


if __name__ == "__main__":
    app()

