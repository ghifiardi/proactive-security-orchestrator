# Proactive Security Orchestrator
## Comprehensive Codebase Documentation

**Version:** 1.0.7
**Last Updated:** December 27, 2025
**Python Version:** 3.11+
**License:** [Your License]

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Workflow](#workflow)
5. [Installation & Setup](#installation--setup)
6. [Usage Guide](#usage-guide)
7. [Configuration](#configuration)
8. [Output Formats](#output-formats)
9. [API Reference](#api-reference)
10. [Development Guide](#development-guide)
11. [Testing](#testing)
12. [Deployment](#deployment)
13. [Troubleshooting](#troubleshooting)

---

## Project Overview

### What is Proactive Security Orchestrator?

The **Proactive Security Orchestrator** is a unified security scanning platform that integrates multiple security tools (Semgrep and Gitleaks) into a single, easy-to-use CLI tool. It provides comprehensive security analysis by combining:

- **Static Application Security Testing (SAST)** via Semgrep
- **Secret Detection** via Gitleaks
- **Unified Output Formats** (JSON, SARIF, HTML, PDF)
- **CI/CD Integration** via GitHub Actions

### Key Features

#### 🔍 **Multi-Tool Integration**
- **Semgrep:** Static analysis for code vulnerabilities (OWASP Top 10, CWE Top 25)
- **Gitleaks:** Secret and credential detection
- **Unified Findings:** Merged, de-duplicated, and validated results

#### 📊 **Multiple Output Formats**
- **JSON:** Machine-readable for automation
- **SARIF 2.1.0:** GitHub Code Scanning integration
- **HTML:** Human-readable dashboard with visualizations
- **PDF:** Professional reports with bullet points and structure

#### 🚀 **Production-Ready**
- **Feature Flags:** Enable/disable tools dynamically
- **Kill Switch:** Emergency shutdown capability
- **Graceful Degradation:** Continues on tool failure
- **Timeout Controls:** Prevents hanging scans
- **Exit Code Handling:** CI/CD friendly

#### 🛡️ **Security First**
- **Secret Redaction:** Sensitive data masked in output
- **Input Validation:** Path and format verification
- **No Shell Injection:** Safe subprocess execution
- **Minimal Dependencies:** Reduced attack surface

### Use Cases

1. **CI/CD Pipeline Integration**
   ```yaml
   # GitHub Actions
   - name: Security Scan
     run: security-scan scan . --format sarif --output findings.sarif
   ```

2. **Local Development**
   ```bash
   # Scan before commit
   security-scan scan /path/to/repo --format html --output report.html
   ```

3. **Security Audits**
   ```bash
   # Generate comprehensive PDF report
   security-scan scan /path/to/repo --format pdf --output audit-report.pdf
   ```

4. **Automated Monitoring**
   ```bash
   # Scheduled scans with JSON output
   security-scan scan /path/to/repo --format json | jq '.[] | select(.severity=="critical")'
   ```

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│                    (cli.py - Typer)                         │
│  • Argument parsing  • Validation  • Output control         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Parent Orchestrator                         │
│              (security_orchestrator.py)                      │
│  • Tool coordination  • Feature flags  • Aggregation        │
└───────┬──────────────────────────────────────┬──────────────┘
        │                                      │
        ▼                                      ▼
┌──────────────────┐                  ┌──────────────────┐
│  Semgrep Agent   │                  │ Gitleaks Agent   │
│ (semgrep_       │                  │ (gitleaks_       │
│  analyzer.py)    │                  │  scanner.py)     │
│                  │                  │                  │
│ • SAST analysis  │                  │ • Secret scan    │
│ • Rule engine    │                  │ • Entropy check  │
│ • Vulnerability  │                  │ • Pattern match  │
│   detection      │                  │                  │
└──────────────────┘                  └──────────────────┘
        │                                      │
        └──────────────┬───────────────────────┘
                       ▼
        ┌──────────────────────────────┐
        │    Finding Validator         │
        │  (finding_validator.py)      │
        │  • Schema validation         │
        │  • De-duplication            │
        │  • Severity sorting          │
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │    Output Formatter          │
        │  (output_formatter.py)       │
        │  • JSON  • SARIF             │
        │  • HTML  • PDF               │
        └──────────────────────────────┘
```

### Component Hierarchy

```
proactive_security_orchestrator/
│
├── cli.py                          # Entry point (CLI interface)
│   └─> SecurityScanner             # Orchestrates tools
│       ├─> SemgrepAnalyzer         # Child agent 1
│       ├─> GitleaksScanner         # Child agent 2
│       └─> FindingValidator        # Validates findings
│           └─> OutputFormatter     # Formats output
```

### Data Flow

```
1. User Input (CLI)
   └─> Argument parsing (Typer)
       └─> Path validation
           └─> Format validation

2. Orchestration (Parent Agent)
   ├─> Initialize tools
   ├─> Run Semgrep analysis
   ├─> Run Gitleaks scan
   └─> Collect findings

3. Validation (Validator)
   ├─> JSON schema validation
   ├─> De-duplication (path + line + rule_id)
   └─> Severity sorting (critical → high → medium → low → info)

4. Formatting (Formatter)
   ├─> Convert to requested format
   └─> Save to file or stdout

5. Exit
   └─> Exit code based on findings (0 or 1)
```

---

## Core Components

### 1. CLI Module (`cli.py`)

**Purpose:** Command-line interface and user interaction

**Key Functions:**

```python
@app.command()
def scan(
    repo_path: str,              # Repository to scan
    format: str = "json",        # Output format
    output: Path | None = None,  # Output file
    config_dir: Path = "config", # Configuration directory
    timeout: int = 60,           # Scan timeout
    verbose: bool = False,       # Verbose logging
    fail_on_critical: bool = True  # Exit code on critical findings
):
    """Scan repository for security vulnerabilities and secrets."""
```

**Features:**
- ✅ Typer-based CLI with type hints
- ✅ Rich terminal output with colors
- ✅ Input validation (paths, formats)
- ✅ Error handling (KeyboardInterrupt, exceptions)
- ✅ Exit code management

**Example:**
```bash
security-scan scan /path/to/repo --format sarif --output findings.sarif --timeout 120
```

---

### 2. Security Orchestrator (`security_orchestrator.py`)

**Purpose:** Parent agent coordinating child tools

**Class Definition:**

```python
class SecurityScanner:
    """Parent orchestrator for security scanning."""

    def __init__(
        self,
        config_dir: Path | str = "config",
        timeout: int = 60,
        env: Dict[str, str] | None = None
    ) -> None:
        """Initialize security scanner."""

    def scan(
        self,
        repo_path: str | Path,
        targets: List[str] | None = None
    ) -> List[Dict[str, Any]]:
        """Run security scan on repository."""
```

**Feature Flags:**

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `ENABLE_SEMGREP` | `true` | Enable/disable Semgrep |
| `ENABLE_GITLEAKS` | `true` | Enable/disable Gitleaks |
| `STRICT_VALIDATION` | `false` | Fail fast vs graceful degradation |
| `ORCHESTRATOR_DISABLED` | `false` | Kill switch |

**Workflow:**

```python
# 1. Initialize tools
self.semgrep = SemgrepAnalyzer(semgrep_config, timeout)
self.gitleaks = GitleaksScanner(gitleaks_config, timeout)

# 2. Run scans (graceful degradation)
try:
    semgrep_findings = self.semgrep.analyze(repo_path)
except Exception as e:
    logger.error(f"Semgrep failed: {e}")
    if not self.strict_validation:
        continue  # Continue with other tools

# 3. Merge findings
all_findings = semgrep_findings + gitleaks_findings

# 4. Validate and de-duplicate
validated_findings = self.validator.validate_all(all_findings)
```

**Key Features:**
- ✅ Tool coordination
- ✅ Error resilience (graceful degradation)
- ✅ Feature flags
- ✅ Metrics logging
- ✅ Timeout management

---

### 3. Semgrep Analyzer (`tools/semgrep_analyzer.py`)

**Purpose:** Child agent for static analysis

**Class Definition:**

```python
class SemgrepAnalyzer:
    """Child agent for Semgrep static analysis."""

    def analyze(self, repo_path: str | Path) -> List[Dict[str, Any]]:
        """Run Semgrep analysis on repository."""
```

**How It Works:**

1. **Command Construction:**
   ```python
   if self.rules_path.exists():
       cmd = ["semgrep", "--config", str(self.rules_path), "--json", str(repo_path)]
   else:
       # Fallback to default security rules
       cmd = ["semgrep", "--config", "auto", "--json", str(repo_path)]
   ```

2. **Subprocess Execution:**
   ```python
   result = subprocess.run(
       cmd,
       capture_output=True,
       text=True,
       timeout=self.timeout,
       check=False  # Don't raise on non-zero exit
   )
   ```

3. **JSON Parsing:**
   ```python
   data = json.loads(result.stdout)
   results = data.get("results", [])
   ```

4. **Finding Conversion:**
   ```python
   for result in results:
       finding = self._to_finding(result)  # Convert to standard format
       findings.append(finding)
   ```

**Semgrep Rules:**
- OWASP Top 10 (`p/owasp-top-ten`)
- CWE Top 25 (`p/cwe-top-25`)
- Python Security (`p/python-security`)
- JavaScript Security (`p/javascript-security`)
- Hardcoded Secrets (`p/hardcoded-secret`)

**Error Handling:**
- ✅ Timeout handling (returns empty list)
- ✅ Command not found (logs error, returns empty)
- ✅ Invalid JSON (logs error, returns empty)
- ✅ Non-zero exit codes (attempts to parse anyway)

---

### 4. Gitleaks Scanner (`tools/gitleaks_scanner.py`)

**Purpose:** Child agent for secret detection

**Class Definition:**

```python
class GitleaksScanner:
    """Child agent for Gitleaks secrets detection."""

    def scan(self, repo_path: str | Path) -> List[Dict[str, Any]]:
        """Run Gitleaks scan on repository."""
```

**How It Works:**

1. **Command Construction:**
   ```python
   cmd = [
       "gitleaks",
       "detect",
       "--source", str(repo_path),
       "--report-format", "json",
       "--report-path", str(temp_output),
       "--no-git"  # Scan filesystem, not git history
   ]
   ```

2. **Exit Code Interpretation:**
   ```python
   if result.returncode == 0:
       # No leaks found
       return []
   elif result.returncode == 1:
       # Leaks found, parse output
       findings = self._parse_gitleaks_output(temp_output)
   else:
       # Error occurred
       logger.error(f"Gitleaks failed with code {result.returncode}")
       return []
   ```

3. **Secret Redaction:**
   ```python
   def _redact_secret(self, secret: str) -> str:
       """Redact secret value for safe logging."""
       if len(secret) <= 8:
           return "***REDACTED***"
       return f"{secret[:4]}...{secret[-4:]}"  # Show first/last 4 chars
   ```

**Security Features:**
- ✅ **Secret redaction** in all output
- ✅ **Entropy detection** (high-entropy strings)
- ✅ **Pattern matching** (API keys, tokens, passwords)
- ✅ **Severity:** All secrets marked as `critical`

**Example Finding:**

```json
{
  "finding": "Secret detected: generic-api-key",
  "evidence": [
    {
      "path": "config.py",
      "lines": "L42",
      "why_relevant": "Gitleaks detected potential secret with entropy 7.50",
      "code_snippet": "API_KEY = 'sk_t...abc'  # REDACTED"
    }
  ],
  "confidence": 0.95,
  "tool": "gitleaks",
  "severity": "critical",
  "rule_id": "generic-api-key",
  "remediation": "Remove secret from code and rotate credentials. Match: sk_t...abc"
}
```

---

### 5. Finding Validator (`validators/finding_validator.py`)

**Purpose:** Validate, de-duplicate, and sort findings

**Class Definition:**

```python
class FindingValidator:
    """Validator for security findings."""

    def validate_all(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate all findings against schema."""

    def deduplicate_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate findings."""

    def sort_by_severity(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort findings by severity."""
```

**Validation Process:**

1. **JSON Schema Validation:**
   ```python
   # Load schema
   schema = self._load_schema()

   # Validate each finding
   for finding in findings:
       try:
           jsonschema.validate(instance=finding, schema=schema)
           valid_findings.append(finding)
       except jsonschema.ValidationError as e:
           logger.warning(f"Invalid finding: {e.message}")
   ```

2. **De-duplication:**
   ```python
   # Use (path, line, rule_id) as unique key
   seen = set()
   for finding in findings:
       key = (
           finding["evidence"][0]["path"],
           finding["evidence"][0]["lines"],
           finding["rule_id"]
       )
       if key not in seen:
           seen.add(key)
           unique_findings.append(finding)
   ```

3. **Severity Sorting:**
   ```python
   severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

   sorted_findings = sorted(
       findings,
       key=lambda f: (
           severity_order.get(f.get("severity", "info"), 4),
           f["evidence"][0].get("path", ""),
           f["evidence"][0].get("lines", "")
       )
   )
   ```

**JSON Schema:**

```json
{
  "type": "object",
  "required": ["finding", "evidence", "confidence", "tool", "severity", "rule_id"],
  "properties": {
    "finding": {"type": "string"},
    "evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "lines", "why_relevant"],
        "properties": {
          "path": {"type": "string"},
          "lines": {"type": "string", "pattern": "^L\\d+(-L\\d+)?$"},
          "why_relevant": {"type": "string"},
          "code_snippet": {"type": "string"}
        }
      }
    },
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "tool": {"type": "string", "enum": ["semgrep", "gitleaks"]},
    "severity": {"type": "string", "enum": ["critical", "high", "medium", "low", "info"]},
    "rule_id": {"type": "string"},
    "remediation": {"type": "string"}
  }
}
```

---

### 6. Output Formatter (`formatters/output_formatter.py`)

**Purpose:** Convert findings to various output formats

**Class Definition:**

```python
class OutputFormatter:
    """Formatter for security findings."""

    def to_json(self, findings: List[Dict[str, Any]]) -> str:
        """Convert findings to JSON."""

    def to_sarif(self, findings: List[Dict[str, Any]]) -> str:
        """Convert findings to SARIF 2.1.0 format."""

    def to_html(self, findings: List[Dict[str, Any]]) -> str:
        """Convert findings to HTML dashboard."""

    def to_pdf(self, findings: List[Dict[str, Any]]) -> bytes:
        """Convert findings to PDF report."""

    def save_to_file(self, findings: List[Dict[str, Any]], format: str, output_path: Path):
        """Save findings to file in specified format."""
```

**Format Details:**

#### JSON Format
```json
[
  {
    "finding": "SQL Injection vulnerability",
    "evidence": [
      {
        "path": "app.py",
        "lines": "L42-L45",
        "why_relevant": "User input directly concatenated into SQL query",
        "code_snippet": "query = 'SELECT * FROM users WHERE id=' + user_id"
      }
    ],
    "confidence": 0.95,
    "tool": "semgrep",
    "severity": "critical",
    "rule_id": "python.sql-injection",
    "remediation": "Use parameterized queries or ORM methods"
  }
]
```

#### SARIF Format (GitHub Code Scanning)
```json
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Proactive Security Orchestrator",
          "version": "1.0.7",
          "rules": [
            {
              "id": "python.sql-injection",
              "name": "SQL Injection",
              "shortDescription": {"text": "SQL Injection vulnerability"},
              "fullDescription": {"text": "User input directly concatenated into SQL query"}
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "python.sql-injection",
          "message": {"text": "SQL Injection vulnerability"},
          "level": "error",
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {"uri": "app.py"},
                "region": {"startLine": 42, "endLine": 45}
              }
            }
          ]
        }
      ]
    }
  ]
}
```

#### HTML Format
```html
<!DOCTYPE html>
<html>
<head>
  <title>Security Scan Report</title>
  <style>
    .critical { background-color: #ff4444; }
    .high { background-color: #ff9944; }
    .medium { background-color: #ffdd44; }
    .low { background-color: #44ff44; }
  </style>
</head>
<body>
  <h1>Security Scan Report</h1>
  <div class="summary">
    <h2>Summary</h2>
    <p>Total Findings: 5</p>
    <p>Critical: 2 | High: 1 | Medium: 2</p>
  </div>
  <div class="findings">
    <div class="finding critical">
      <h3>SQL Injection vulnerability</h3>
      <p><strong>File:</strong> app.py (L42-L45)</p>
      <p><strong>Severity:</strong> Critical</p>
      <p><strong>Remediation:</strong> Use parameterized queries</p>
    </div>
  </div>
</body>
</html>
```

#### PDF Format
- Professional layout with headers/footers
- Executive summary section
- Findings grouped by severity
- Code snippets with syntax highlighting
- Remediation guidance boxes

---

## Workflow

### Development Workflow (Research → Plan → Implement)

The orchestrator follows a strict **three-phase workflow** for feature development:

#### Phase A: RESEARCH (60-90 min)

**Goal:** Investigate codebase and produce `.agents/research.md`

**Process:**
1. Open Cursor Composer
2. Set system prompt: `prompts/parent_system_prompt.md`
3. Run research prompt: `prompts/research_prompt.md`
4. Output: `.agents/research.md` with:
   - Scope analysis
   - File map with line references
   - Execution flow
   - Test coverage
   - Risk assessment

**Example Research Output:**
```markdown
## Scope
Target: Add PDF output format to OutputFormatter

## Peta File
- src/formatters/output_formatter.py [L1-L150]
- tests/test_output_formatter.py [L1-L80]

## Alur Eksekusi
1. User calls: security-scan scan . --format pdf
2. CLI validates format (cli.py:L50)
3. Formatter.to_pdf() called (output_formatter.py:L120)
4. PDF generated using reportlab
5. Saved to output file
```

#### Phase B: PLAN (90-120 min)

**Goal:** Convert research into implementation plan (`.agents/plan.md`)

**Process:**
1. Review approved research.md
2. Run planning prompt: `prompts/plan_prompt.md`
3. Output: `.agents/plan.md` with:
   - Implementation steps (Langkah 1..N)
   - Per-file changes with line references
   - Testing strategy
   - Acceptance criteria
   - Rollback procedure

**Example Plan Output:**
```markdown
## Langkah 1: Add PDF generation method

**File:** src/formatters/output_formatter.py
**Lines:** L120-L180 (new)
**Changes:**
- Import reportlab dependencies
- Add to_pdf(findings) method
- Generate PDF with summary table
- Add finding details with code snippets

**Test:** pytest tests/test_output_formatter.py::test_to_pdf -v
```

#### Phase C: IMPLEMENT (45-60 min per Langkah)

**Goal:** Execute one Langkah, produce working code + passing tests

**Process:**
1. Run implementation prompt: `prompts/implement_prompt.md`
2. Specify current Langkah
3. Implement changes
4. Run tests
5. Update `.agents/progress.md`
6. Open PR

**Example Progress Update:**
```markdown
## Langkah 1 - Add PDF generation method

**Status:** ✅ Complete
**Test Results:** 4/4 tests passing
**Duration:** 45 minutes
**Changes:** Added OutputFormatter.to_pdf() method
```

---

## Installation & Setup

### Prerequisites

- **Python 3.11+**
- **Semgrep** (static analysis tool)
- **Gitleaks** (secret detection tool)
- **Git** (version control)

### Installation Methods

#### Method 1: From Source (Development)

```bash
# Clone repository
git clone https://github.com/ghifiardi/proactive-security-orchestrator.git
cd proactive-security-orchestrator

# Install in editable mode
python -m pip install -e .

# Install development dependencies
pip install -r requirements.txt

# Verify installation
security-scan --help
```

#### Method 2: From PyPI (Future)

```bash
# Install from PyPI (when published)
pip install proactive-security-orchestrator

# Verify installation
security-scan --help
```

#### Method 3: From Docker

```bash
# Build Docker image
docker build -t security-orchestrator .

# Run scan
docker run -v /path/to/repo:/repo security-orchestrator scan /repo --format json
```

### Tool Installation

#### Install Semgrep

```bash
# Method 1: pip
pip install semgrep

# Method 2: Homebrew (macOS)
brew install semgrep

# Method 3: Binary download
# See https://semgrep.dev/docs/getting-started/

# Verify
semgrep --version
```

#### Install Gitleaks

```bash
# Method 1: Homebrew (macOS)
brew install gitleaks

# Method 2: apt (Ubuntu/Debian)
sudo apt-get install gitleaks

# Method 3: Binary download
curl -sSfL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks-linux-amd64 \
  -o /usr/local/bin/gitleaks
chmod +x /usr/local/bin/gitleaks

# Verify
gitleaks version
```

### Configuration

Create `.env` file (optional):

```bash
# .env
ENABLE_SEMGREP=true
ENABLE_GITLEAKS=true
STRICT_VALIDATION=false
ORCHESTRATOR_DISABLED=false
```

Customize Semgrep rules:

```bash
# Edit config/semgrep/rules.yaml
nano config/semgrep/rules.yaml
```

Configure Gitleaks ignore patterns:

```bash
# Edit config/gitleaks/.gitleaksignore
nano config/gitleaks/.gitleaksignore
```

---

## Usage Guide

### Basic Usage

**Scan a repository:**
```bash
security-scan scan /path/to/repo
```

**Specify output format:**
```bash
security-scan scan /path/to/repo --format json
security-scan scan /path/to/repo --format sarif
security-scan scan /path/to/repo --format html
security-scan scan /path/to/repo --format pdf
```

**Save to file:**
```bash
security-scan scan /path/to/repo --format json --output findings.json
```

**Increase timeout:**
```bash
security-scan scan /path/to/repo --timeout 300  # 5 minutes
```

**Enable verbose logging:**
```bash
security-scan scan /path/to/repo --verbose
```

**Don't fail on critical findings (CI/CD):**
```bash
security-scan scan /path/to/repo --no-fail-on-critical
```

### Advanced Usage

#### Scan with custom config

```bash
security-scan scan /path/to/repo --config /path/to/config
```

#### Disable specific tools

```bash
# Disable Semgrep
ENABLE_SEMGREP=false security-scan scan /path/to/repo

# Disable Gitleaks
ENABLE_GITLEAKS=false security-scan scan /path/to/repo
```

#### Emergency shutdown

```bash
# Kill switch (disables all scanning)
ORCHESTRATOR_DISABLED=true security-scan scan /path/to/repo
# Returns empty findings immediately
```

#### Filter critical findings with jq

```bash
security-scan scan /path/to/repo --format json | \
  jq '.[] | select(.severity=="critical")'
```

### Docker Usage

**Build image:**
```bash
docker build -t security-orchestrator .
```

**Scan repository:**
```bash
docker run -v /path/to/repo:/repo \
  security-orchestrator scan /repo --format json
```

**Save output to host:**
```bash
docker run \
  -v /path/to/repo:/repo \
  -v $(pwd):/output \
  security-orchestrator scan /repo --format sarif --output /output/findings.sarif
```

**Override timeout:**
```bash
docker run -v /path/to/repo:/repo \
  security-orchestrator scan /repo --timeout 300
```

### CI/CD Integration

#### GitHub Actions

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install tools
        run: |
          pip install semgrep
          brew install gitleaks  # or download binary

      - name: Install orchestrator
        run: pip install proactive-security-orchestrator

      - name: Run security scan
        run: |
          security-scan scan . \
            --format sarif \
            --output findings.sarif \
            --no-fail-on-critical

      - name: Upload to Code Scanning
        uses: github/codeql-action/upload-sarif@v4
        with:
          sarif_file: findings.sarif
```

#### GitLab CI

```yaml
# .gitlab-ci.yml
security_scan:
  stage: test
  image: python:3.11
  script:
    - pip install semgrep gitleaks proactive-security-orchestrator
    - security-scan scan . --format json --output findings.json
  artifacts:
    paths:
      - findings.json
    expire_in: 1 week
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_SEMGREP` | `true` | Enable Semgrep static analysis |
| `ENABLE_GITLEAKS` | `true` | Enable Gitleaks secret detection |
| `STRICT_VALIDATION` | `false` | Fail fast on tool errors |
| `ORCHESTRATOR_DISABLED` | `false` | Emergency kill switch |

### Semgrep Configuration

**File:** `config/semgrep/rules.yaml`

```yaml
rules:
  # Security rule packs
  - id: p/owasp-top-ten      # OWASP Top 10
  - id: p/cwe-top-25         # CWE Top 25
  - id: p/python-security    # Python-specific
  - id: p/javascript-security # JavaScript-specific
  - id: p/hardcoded-secret   # Secret detection

# Exclude patterns
exclude:
  - .git
  - node_modules
  - venv
  - __pycache__
  - "*.min.js"

# Timeout per file (seconds)
timeout: 30

# Max lines to show per finding
max-lines-per-finding: 5
```

**Custom Rules:**

```yaml
rules:
  - id: my-custom-rule
    pattern: |
      eval($USER_INPUT)
    message: "Dangerous use of eval() with user input"
    severity: ERROR
    languages: [python]
    metadata:
      cwe: "CWE-94"
      owasp: "A03:2021"
```

### Gitleaks Configuration

**File:** `config/gitleaks/.gitleaksignore`

```
# Test credentials (false positives)
password123
test_api_key
example_secret

# Environment variable names (not actual secrets)
API_KEY
SECRET_KEY
DATABASE_PASSWORD

# Documentation examples
your_api_key_here
<your-token>
```

### CLI Configuration

**Default config directory:**
```
config/
├── semgrep/
│   └── rules.yaml
└── gitleaks/
    └── .gitleaksignore
```

**Custom config directory:**
```bash
security-scan scan /path/to/repo --config /custom/config/dir
```

---

## Output Formats

### JSON Format

**Use Case:** Machine-readable, automation, scripting

**Example:**
```json
[
  {
    "finding": "SQL Injection vulnerability detected",
    "evidence": [
      {
        "path": "src/database.py",
        "lines": "L42-L45",
        "why_relevant": "User input concatenated directly into SQL query",
        "code_snippet": "query = 'SELECT * FROM users WHERE id=' + user_id"
      }
    ],
    "confidence": 0.95,
    "tool": "semgrep",
    "severity": "critical",
    "rule_id": "python.sql-injection",
    "remediation": "Use parameterized queries or ORM with parameter binding"
  }
]
```

**Usage:**
```bash
security-scan scan /repo --format json --output findings.json

# Filter critical only
cat findings.json | jq '.[] | select(.severity=="critical")'

# Count by severity
cat findings.json | jq 'group_by(.severity) | map({severity: .[0].severity, count: length})'
```

### SARIF Format

**Use Case:** GitHub Code Scanning, IDE integration, standardized reporting

**Example:**
```json
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Proactive Security Orchestrator",
          "version": "1.0.7",
          "informationUri": "https://github.com/ghifiardi/proactive-security-orchestrator",
          "rules": [
            {
              "id": "python.sql-injection",
              "name": "SQL Injection",
              "shortDescription": {"text": "SQL Injection vulnerability"},
              "fullDescription": {"text": "User input directly concatenated into SQL query"},
              "help": {
                "text": "Use parameterized queries or ORM methods to prevent SQL injection"
              }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "python.sql-injection",
          "message": {"text": "SQL Injection vulnerability detected"},
          "level": "error",
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {"uri": "src/database.py"},
                "region": {"startLine": 42, "endLine": 45}
              }
            }
          ]
        }
      ]
    }
  ]
}
```

**GitHub Integration:**
```yaml
- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v4
  with:
    sarif_file: findings.sarif
```

### HTML Format

**Use Case:** Human-readable reports, sharing with stakeholders

**Features:**
- Executive summary
- Findings grouped by severity
- Color-coded severity badges
- Expandable code snippets
- Remediation guidance
- Responsive design

**Example Output:**
```html
<!DOCTYPE html>
<html>
<head>
  <title>Security Scan Report - 2025-12-27</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .summary { background: #f0f0f0; padding: 15px; margin-bottom: 20px; }
    .finding { border-left: 4px solid; padding: 10px; margin: 10px 0; }
    .critical { border-color: #d32f2f; background: #ffebee; }
    .high { border-color: #f57c00; background: #fff3e0; }
    .medium { border-color: #fbc02d; background: #fffde7; }
    .code { background: #263238; color: #aed581; padding: 10px; }
  </style>
</head>
<body>
  <h1>Security Scan Report</h1>
  <div class="summary">
    <h2>Summary</h2>
    <p>Total Findings: <strong>5</strong></p>
    <ul>
      <li>Critical: 2</li>
      <li>High: 1</li>
      <li>Medium: 2</li>
    </ul>
  </div>
  <div class="findings">
    <div class="finding critical">
      <h3>🔴 SQL Injection vulnerability</h3>
      <p><strong>File:</strong> src/database.py (L42-L45)</p>
      <p><strong>Tool:</strong> Semgrep</p>
      <p><strong>Confidence:</strong> 95%</p>
      <div class="code">
        <pre>query = 'SELECT * FROM users WHERE id=' + user_id</pre>
      </div>
      <p><strong>Remediation:</strong> Use parameterized queries</p>
    </div>
  </div>
</body>
</html>
```

### PDF Format

**Use Case:** Professional reports, audits, compliance documentation

**Features:**
- Professional layout with headers/footers
- Executive summary section
- Table of contents
- Findings grouped and numbered
- Syntax-highlighted code snippets
- Remediation boxes
- Page numbers and timestamps

**Structure:**
1. **Cover Page**
   - Report title
   - Generated date
   - Scan target
   - Tool version

2. **Executive Summary**
   - Total findings
   - Severity distribution
   - Top risks

3. **Findings Details**
   - Numbered findings
   - Severity badges
   - File locations
   - Code snippets
   - Remediation guidance

4. **Appendix**
   - Configuration used
   - Tool versions
   - Scan parameters

---

## API Reference

### SecurityScanner Class

```python
from proactive_security_orchestrator.security_orchestrator import SecurityScanner

scanner = SecurityScanner(
    config_dir="config",      # Configuration directory
    timeout=60,               # Timeout in seconds
    env={"ENABLE_SEMGREP": "true"}  # Environment overrides
)

findings = scanner.scan(
    repo_path="/path/to/repo",
    targets=None              # Optional: specific files/dirs
)
```

### SemgrepAnalyzer Class

```python
from proactive_security_orchestrator.tools.semgrep_analyzer import SemgrepAnalyzer

analyzer = SemgrepAnalyzer(
    config_dir="config/semgrep",
    timeout=60
)

findings = analyzer.analyze("/path/to/repo")
```

### GitleaksScanner Class

```python
from proactive_security_orchestrator.tools.gitleaks_scanner import GitleaksScanner

scanner = GitleaksScanner(
    config_dir="config/gitleaks",
    timeout=60
)

findings = scanner.scan("/path/to/repo")
```

### FindingValidator Class

```python
from proactive_security_orchestrator.validators.finding_validator import FindingValidator

validator = FindingValidator()

# Validate all findings
validated = validator.validate_all(findings)

# De-duplicate
unique = validator.deduplicate_findings(findings)

# Sort by severity
sorted_findings = validator.sort_by_severity(findings)
```

### OutputFormatter Class

```python
from proactive_security_orchestrator.formatters.output_formatter import OutputFormatter

formatter = OutputFormatter()

# Convert to JSON
json_str = formatter.to_json(findings)

# Convert to SARIF
sarif_str = formatter.to_sarif(findings)

# Convert to HTML
html_str = formatter.to_html(findings)

# Convert to PDF
pdf_bytes = formatter.to_pdf(findings)

# Save to file
formatter.save_to_file(findings, "json", "output.json")
```

---

## Development Guide

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/ghifiardi/proactive-security-orchestrator.git
cd proactive-security-orchestrator

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install tools
pip install semgrep
brew install gitleaks

# Run tests
pytest tests/ -v
```

### Code Style

**Formatting:**
```bash
# Format with black
black src/ tests/

# Check with flake8
flake8 src/ tests/

# Type check with mypy
mypy src/
```

**Type Hints:**
```python
from pathlib import Path
from typing import List, Dict, Any

def scan(repo_path: str | Path) -> List[Dict[str, Any]]:
    """Use modern type hints (Python 3.11+)."""
    pass
```

### Adding New Features

**Follow Research → Plan → Implement workflow:**

1. **Research Phase:**
   - Document in `.agents/research.md`
   - Identify affected files and line numbers
   - Assess risks

2. **Planning Phase:**
   - Create `.agents/plan.md`
   - Break into atomic Langkah steps
   - Define acceptance criteria

3. **Implementation Phase:**
   - Implement one Langkah at a time
   - Write tests first (TDD)
   - Update `.agents/progress.md`
   - Open PR with artifact links

### Testing Guidelines

**Write tests for:**
- All new functions
- Edge cases
- Error scenarios
- Integration points

**Example Test:**
```python
def test_scan_with_timeout():
    """Test scan respects timeout setting."""
    scanner = SecurityScanner(timeout=5)

    with pytest.raises(subprocess.TimeoutExpired):
        scanner.scan(large_repository_fixture)
```

### Pull Request Template

```markdown
## Context
Research: `.agents/research.md` § Section
Plan: `.agents/plan.md` § Langkah N

## Changes
Brief description of what changed

## Verification
- [ ] Tests passing
- [ ] Coverage maintained
- [ ] Documentation updated

## Risks
Any potential risks and mitigation
```

---

## Testing

### Running Tests

**All tests:**
```bash
pytest tests/ -v
```

**With coverage:**
```bash
pytest tests/ -v --cov=src --cov-report=html
```

**Specific test file:**
```bash
pytest tests/test_cli.py -v
```

**Specific test function:**
```bash
pytest tests/test_cli.py::test_cli_help -v
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures
├── test_cli.py                    # CLI tests
├── test_security_orchestrator.py  # Orchestrator tests
├── test_semgrep_analyzer.py       # Semgrep tests
├── test_gitleaks_scanner.py       # Gitleaks tests
├── test_finding_validator.py      # Validator tests
├── test_output_formatter.py       # Formatter tests
└── test_integration.py            # End-to-end tests
```

### Test Coverage Report

```
Name                                           Stmts   Miss  Cover
------------------------------------------------------------------
src/__init__.py                                    1      0   100%
src/cli.py                                        72     15    79%
src/security_orchestrator.py                      75     16    79%
src/tools/semgrep_analyzer.py                     70     10    86%
src/tools/gitleaks_scanner.py                     72     16    78%
src/formatters/output_formatter.py                79      8    90%
src/validators/finding_validator.py               58      4    93%
------------------------------------------------------------------
TOTAL                                            430     72    83%
```

---

## Deployment

### Production Deployment

**Prerequisites:**
- Python 3.11+
- Semgrep and Gitleaks installed
- Configuration files prepared

**Deployment Steps:**

1. **Install package:**
   ```bash
   pip install proactive-security-orchestrator
   ```

2. **Configure tools:**
   ```bash
   # Copy configuration
   cp -r config/ /etc/security-orchestrator/

   # Set environment variables
   export ENABLE_SEMGREP=true
   export ENABLE_GITLEAKS=true
   ```

3. **Verify installation:**
   ```bash
   security-scan --help
   semgrep --version
   gitleaks version
   ```

4. **Test scan:**
   ```bash
   security-scan scan /test/repo --format json
   ```

### Docker Deployment

```bash
# Build image
docker build -t security-orchestrator:1.0.7 .

# Tag for registry
docker tag security-orchestrator:1.0.7 myregistry/security-orchestrator:1.0.7

# Push to registry
docker push myregistry/security-orchestrator:1.0.7

# Run in production
docker run -d \
  -v /repos:/repos \
  -v /output:/output \
  myregistry/security-orchestrator:1.0.7 \
  scan /repos/myapp --format sarif --output /output/findings.sarif
```

### Kubernetes Deployment

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: security-scan
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scanner
            image: myregistry/security-orchestrator:1.0.7
            args:
              - scan
              - /repos
              - --format
              - sarif
              - --output
              - /output/findings.sarif
            volumeMounts:
              - name: repo-volume
                mountPath: /repos
              - name: output-volume
                mountPath: /output
          volumes:
            - name: repo-volume
              persistentVolumeClaim:
                claimName: repo-pvc
            - name: output-volume
              persistentVolumeClaim:
                claimName: output-pvc
          restartPolicy: OnFailure
```

---

## Troubleshooting

### Common Issues

#### 1. Semgrep Not Found

**Error:**
```
Semgrep command not found
```

**Solution:**
```bash
# Install Semgrep
pip install semgrep

# Or via Homebrew
brew install semgrep

# Verify
semgrep --version
```

#### 2. Gitleaks Not Found

**Error:**
```
Gitleaks command not found
```

**Solution:**
```bash
# Install Gitleaks
brew install gitleaks

# Or download binary
curl -sSfL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks-linux-amd64 \
  -o /usr/local/bin/gitleaks
chmod +x /usr/local/bin/gitleaks

# Verify
gitleaks version
```

#### 3. Scan Timeout

**Error:**
```
Semgrep timed out after 60s
```

**Solution:**
```bash
# Increase timeout
security-scan scan /repo --timeout 300

# Or scan subdirectories separately
security-scan scan /repo/src --timeout 120
security-scan scan /repo/tests --timeout 60
```

#### 4. High False Positive Rate

**Error:**
```
Too many false positives in Gitleaks results
```

**Solution:**
```bash
# Add patterns to .gitleaksignore
echo "test_api_key" >> config/gitleaks/.gitleaksignore
echo "password123" >> config/gitleaks/.gitleaksignore

# Re-run scan
security-scan scan /repo --format json
```

#### 5. Invalid Semgrep Configuration

**Error:**
```
Semgrep exited with code 7
```

**Solution:**
```bash
# Validate configuration
semgrep --validate --config config/semgrep/rules.yaml

# Or use default rules
rm config/semgrep/rules.yaml  # Will auto-fallback to --config auto
```

### Performance Tuning

**Large repositories:**
```bash
# Increase timeout
--timeout 600

# Exclude unnecessary paths
# Edit config/semgrep/rules.yaml:
exclude:
  - vendor/
  - node_modules/
  - dist/
```

**Memory constraints:**
```bash
# Scan in batches
security-scan scan /repo/src
security-scan scan /repo/tests
security-scan scan /repo/lib
```

---

## Appendix

### Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Current Version:** 1.0.7

**Key Releases:**
- 1.0.7: Added `--no-fail-on-critical` flag
- 1.0.6: Added PDF output format
- 1.0.5: Improved SARIF readability
- 1.0.0: Initial release

### License

[Specify your license here]

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

### Support

- **Issues:** https://github.com/ghifiardi/proactive-security-orchestrator/issues
- **Discussions:** https://github.com/ghifiardi/proactive-security-orchestrator/discussions
- **Documentation:** https://github.com/ghifiardi/proactive-security-orchestrator/wiki

### Acknowledgments

- **Semgrep:** https://semgrep.dev
- **Gitleaks:** https://github.com/gitleaks/gitleaks
- **Typer:** https://typer.tiangolo.com
- **Rich:** https://github.com/Textualize/rich
- **Pydantic:** https://pydantic.dev

---

**Document End**

*Last Updated: December 27, 2025*
*Version: 1.0.7*
*Maintained by: Proactive Security Team*
