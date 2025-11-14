# Research: Semgrep + Gitleaks Integration into Proactive Codebase Testing

## Scope

**Target**: Integrate Semgrep (static analysis) and Gitleaks (secrets detection) into a unified orchestrator that can be invoked as a parent security scanner, coordinating child tool agents to produce structured findings.

**Components/Services**:
- Parent Orchestrator: `SecurityScanner` (routes findings, validates output)
- Child Agent 1: `SemgrepAnalyzer` (runs static analysis)
- Child Agent 2: `GitleaksScanner` (detects secrets in git history)
- Output Formatter: converts tool outputs to JSON, SARIF, HTML

---

## Peta File & Simbol

| Path | Lines | Role |
|------|-------|------|
| `src/security_orchestrator.py` | [L1-L50] | Parent SecurityScanner class definition |
| `src/security_orchestrator.py` | [L51-L120] | Main orchestration logic & tool routing |
| `src/tools/semgrep_analyzer.py` | [L1-L80] | Semgrep wrapper, runs `semgrep` CLI |
| `src/tools/gitleaks_scanner.py` | [L1-L80] | Gitleaks wrapper, runs `gitleaks` CLI |
| `src/formatters/output_formatter.py` | [L1-L60] | Converts tool outputs to JSON/SARIF/HTML |
| `config/semgrep/rules.yaml` | [L1-L100] | Semgrep ruleset (security + code-quality) |
| `config/gitleaks/.gitleaksignore` | [L1-L50] | False-positive exclusions for gitleaks |
| `src/validators/finding_validator.py` | [L1-L40] | Validates findings against schema |
| `.agents/research.md` | (this file) | Investigation output (ARTIFACT) |
| `.agents/plan.md` | (phase 2) | Detailed per-file changes (ARTIFACT) |
| `.agents/progress.md` | (phase 3) | Step-by-step implementation log (ARTIFACT) |

---

## Alur Eksekusi End-to-End

```
1. [Entry] User calls SecurityScanner.scan(repo_path, targets)
   └─ routes to [L51-L120] orchestration logic

2. [Child 1] SemgrepAnalyzer spawns:
   └─ runs `semgrep --config config/semgrep/rules.yaml --json <repo_path>`
   └─ returns findings (path, lines, rule_id, message)

3. [Child 2] GitleaksScanner spawns:
   └─ runs `gitleaks detect --source <repo_path> --json`
   └─ returns secret detections (path, line, entropy, type)

4. [Validator] FindingValidator merges & validates all findings
   └─ ensures each finding matches child_agent_schema.json
   └─ filters duplicates, confirms severity levels

5. [Formatter] OutputFormatter produces:
   └─ JSON (canonical)
   └─ SARIF (GitHub Code Scanning API)
   └─ HTML dashboard (human review)

6. [Exit] SecurityScanner returns merged findings object
```

---

## Tes & Observabilitas

### Tests to Run
- **Unit**: `tests/test_semgrep_analyzer.py` → mock `semgrep` CLI calls
- **Unit**: `tests/test_gitleaks_scanner.py` → mock `gitleaks` CLI calls
- **Integration**: `tests/test_security_orchestrator.py` → end-to-end scan on sample repo
- **Schema**: `tests/test_finding_validator.py` → verify all findings match JSON schema

### How to Run
```bash
# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific tool tests
pytest tests/test_semgrep_analyzer.py -v
pytest tests/test_gitleaks_scanner.py -v

# Integration test (scans a test fixture)
pytest tests/test_security_orchestrator.py::test_end_to_end_scan -v

# Check a real repo (manual verification)
python -m src.security_orchestrator scan /path/to/repo --format json > findings.json
```

### Observabilidad (Logs/Metrics)
- Tool invocation logs: `src/tools/*.py` [DEBUG] level
- Finding counts: counter per tool (semgrep_findings_total, gitleaks_findings_total)
- Validation errors: caught & logged, don't crash orchestrator
- Output files: `findings.json`, `findings.sarif`, `dashboard.html`

---

## Risiko & Asumsi

| Risk | Assumption | Mitigation |
|------|-----------|-----------|
| Semgrep/Gitleaks not installed | Tools are available in PATH or virtualenv | Install via `pip install semgrep gitleaks` in setup.py |
| Tool versions differ (output format) | Using semgrep ≥1.45, gitleaks ≥8.16 | Pin versions in requirements.txt |
| Huge repos timeout | Scans complete in <60s | Implement timeout + partial results fallback |
| Duplicate findings across tools | De-duplicated in validator | Group by (path, line, rule_id) |
| Large findings JSON → memory | JSON serialization is lazy | Stream results if >10k findings |
| Secrets in gitleaks output | Accidental exposure in logs | Redact in formatters, never log raw gitleaks output |
| Schema mismatch | All tools produce valid JSON | Validator rejects non-compliant findings (fail-safe) |

---

## Bukti (Code Snippets)

### 1. Parent Orchestrator Entry Point
```python
# src/security_orchestrator.py [L1-L30]
class SecurityScanner:
    def __init__(self, config_dir="config"):
        self.semgrep = SemgrepAnalyzer(config_dir / "semgrep")
        self.gitleaks = GitleaksScanner(config_dir / "gitleaks")
        self.validator = FindingValidator()
    
    def scan(self, repo_path, targets=None):
        """Main orchestration entry point."""
        findings = []
        findings.extend(self.semgrep.analyze(repo_path))
        findings.extend(self.gitleaks.scan(repo_path))
        validated = self.validator.validate_all(findings)
        return validated
```

### 2. Semgrep Analyzer Child Agent
```python
# src/tools/semgrep_analyzer.py [L1-L30]
import subprocess, json
class SemgrepAnalyzer:
    def analyze(self, repo_path):
        cmd = ["semgrep", "--config", str(self.rules_path), "--json", repo_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        data = json.loads(result.stdout)
        return [self._to_finding(r) for r in data.get("results", [])]
    
    def _to_finding(self, semgrep_result):
        return {
            "tool": "semgrep",
            "rule_id": semgrep_result["check_id"],
            "path": semgrep_result["path"],
            "lines": f"L{semgrep_result['start']['line']}-L{semgrep_result['end']['line']}"
        }
```

### 3. Gitleaks Scanner Child Agent
```python
# src/tools/gitleaks_scanner.py [L1-L30]
class GitleaksScanner:
    def scan(self, repo_path):
        cmd = ["gitleaks", "detect", "--source", repo_path, "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout or "[]")
        return [self._to_finding(m) for m in data]
    
    def _to_finding(self, gitleaks_match):
        return {
            "tool": "gitleaks",
            "rule_id": gitleaks_match.get("RuleID"),
            "path": gitleaks_match.get("File"),
            "lines": f"L{gitleaks_match.get('LineNumber')}"
        }
```

### 4. Finding Validator (Schema Enforcement)
```python
# src/validators/finding_validator.py [L1-L25]
import jsonschema
class FindingValidator:
    def __init__(self):
        self.schema = load_json_schema("contracts/child_agent_schema.json")
    
    def validate_all(self, findings):
        valid = []
        for f in findings:
            try:
                jsonschema.validate(f, self.schema)
                valid.append(f)
            except jsonschema.ValidationError as e:
                logger.warning(f"Skipped invalid finding: {e}")
        return valid
```

### 5. Output Formatter (Multi-format)
```python
# src/formatters/output_formatter.py [L1-L30]
class OutputFormatter:
    def to_json(self, findings):
        return json.dumps(findings, indent=2)
    
    def to_sarif(self, findings):
        """Convert findings to SARIF (GitHub Code Scanning format)."""
        return { "version": "2.1.0", "runs": [...] }
    
    def to_html(self, findings):
        """Generate HTML dashboard for human review."""
        return "<html>...</html>"
```

---

## Summary

This research identifies:
1. **Architecture**: Parent orchestrator + 2 child tool agents (Semgrep, Gitleaks)
2. **Data Flow**: Tool outputs → JSON schema validation → multi-format output
3. **Key Files**: 6 core modules + 2 config directories + 5 test modules
4. **Risks**: Tool availability, version mismatches, timeouts (all mitigated)
5. **Testability**: Unit + integration tests, schema validation, mock CLI
