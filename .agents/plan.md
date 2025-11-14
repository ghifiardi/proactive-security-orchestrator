# Plan: Semgrep + Gitleaks Integration Implementation

## Goal & Non-Goals

### Goal
Implement a unified security scanning orchestrator that invokes Semgrep and Gitleaks as child agents, validates findings against JSON schema, and outputs in JSON/SARIF/HTML formats.

### Non-Goals
- Replace or rewrite Semgrep/Gitleaks (use CLI as-is)
- Build a web UI (HTML dashboard is static report only)
- Implement real-time monitoring (batch scanning only)
- Support custom rule development (use existing Semgrep rulesets)

---

## Perubahan per File

### File 1: `src/security_orchestrator.py`

- **Lokasi**: [L1-L150]
- **Perubahan**:
  - Define `SecurityScanner` class with `__init__(config_dir, timeout, env)`
  - Implement `scan(repo_path, targets=None)` orchestration method
  - Call `SemgrepAnalyzer.analyze(repo_path)` and `GitleaksScanner.scan(repo_path)`
  - Merge findings, pass to `FindingValidator`
  - Return validated findings
  - Add `_log_orchestration_metrics()` for observability
- **Mengapa**: Central orchestrator routes all security scanning; required for Parent pattern
- **Dampak**: Called by CLI/API, depends on SemgrepAnalyzer & GitleaksScanner

### File 2: `src/tools/semgrep_analyzer.py`

- **Lokasi**: [L1-L100]
- **Perubahan**:
  - Define `SemgrepAnalyzer` class with `__init__(config_dir, timeout)`
  - Implement `analyze(repo_path) → List[Dict]`
  - Run `semgrep --config <rules.yaml> --json <repo_path>`
  - Parse JSON output, convert to finding dicts (tool, rule_id, path, lines, severity)
  - Add error handling: tool not found, timeout, invalid JSON
  - Return empty list on error (don't crash orchestrator)
- **Mengapa**: Child agent for static analysis; must be subprocess-safe
- **Dampak**: Called by SecurityScanner, must return JSON-serializable findings

### File 3: `src/tools/gitleaks_scanner.py`

- **Lokasi**: [L1-L100]
- **Perubahan**:
  - Define `GitleaksScanner` class with `__init__(config_dir, timeout)`
  - Implement `scan(repo_path) → List[Dict]`
  - Run `gitleaks detect --source <repo_path> --json --config <.gitleaksignore>`
  - Parse JSON output, convert to finding dicts (tool, rule_id, path, lines, severity)
  - Redact secret values in output (don't log raw secrets)
  - Add error handling: tool not found, timeout, invalid JSON
  - Return empty list on error (don't crash orchestrator)
- **Mengapa**: Child agent for secrets detection; must be subprocess-safe
- **Dampak**: Called by SecurityScanner, must return JSON-serializable findings

### File 4: `src/validators/finding_validator.py`

- **Lokasi**: [L1-L80]
- **Perubahan**:
  - Define `FindingValidator` class with `__init__(schema_path)`
  - Load JSON schema from `contracts/child_agent_schema.json`
  - Implement `validate_all(findings) → List[Dict]`
  - For each finding: validate against schema, skip if invalid (log warning)
  - De-duplicate findings by (path, line, rule_id)
  - Sort by severity (critical → info) and line number
  - Return validated, de-duplicated list
- **Mengapa**: Ensures all findings conform to schema; prevents downstream errors
- **Dampak**: Called by SecurityScanner, output safe for formatters

### File 5: `src/formatters/output_formatter.py`

- **Lokasi**: [L1-L150]
- **Perubahan**:
  - Define `OutputFormatter` class
  - Implement `to_json(findings) → str` (pretty-print with indent=2)
  - Implement `to_sarif(findings) → str` (convert to SARIF 2.1.0 format)
  - Implement `to_html(findings) → str` (render HTML dashboard: summary table + details)
  - Add `save_to_file(findings, format, output_path)` helper
  - Ensure SARIF output includes ruleId, message, location (path/line)
- **Mengapa**: Multi-format output for different consumers (CI/CD, GitHub, human review)
- **Dampak**: Called by CLI/API, produces final output artifacts

### File 6: `config/semgrep/rules.yaml`

- **Lokasi**: [L1-L50]
- **Perubahan**:
  - Define Semgrep config: rules to run (security, code-quality)
  - Include Semgrep registry rules for Python/Go/JavaScript/etc.
  - Set paths to exclude: `.git`, `node_modules`, `venv`, `__pycache__`
  - Define timeout per rule, max-lines-per-finding
- **Mengapa**: Configures Semgrep behavior; must exclude common noise
- **Dampak**: Loaded by SemgrepAnalyzer, controls which rules run

### File 7: `config/gitleaks/.gitleaksignore`

- **Lokasi**: [L1-L30]
- **Perubahan**:
  - List false-positive patterns to exclude (e.g., test credentials, dummy strings)
  - Use Gitleaks regex syntax
  - Add entries for common CI/CD tokens, test API keys
- **Mengapa**: Reduces false positives in secret detection
- **Dampak**: Loaded by GitleaksScanner, filters noisy matches

### File 8: `src/cli.py` (NEW)

- **Lokasi**: [L1-L60]
- **Perubahan**:
  - Define CLI entry point using `typer.Typer()`
  - Add command: `scan <repo_path> --format (json|sarif|html) --output <path>`
  - Parse args, instantiate `SecurityScanner`, call `scan()`
  - Format and save output
- **Mengapa**: User interface for orchestrator
- **Dampak**: Called by users/CI-CD

### File 9: `tests/test_security_orchestrator.py`

- **Lokasi**: [L1-L80]
- **Perubahan**:
  - Mock `SemgrepAnalyzer.analyze()` and `GitleaksScanner.scan()`
  - Test orchestrator merges findings correctly
  - Test orchestrator handles tool errors (empty findings)
  - Test validator is called on merged findings
- **Mengapa**: Unit test for orchestrator
- **Dampak**: Validates orchestration logic before integration tests

### File 10: `tests/test_semgrep_analyzer.py`

- **Lokasi**: [L1-L100]
- **Perubahan**:
  - Mock `subprocess.run()` to return sample Semgrep JSON output
  - Test `analyze()` correctly parses findings
  - Test error handling: tool not found, invalid JSON, timeout
  - Test conversion to finding dict schema
- **Mengapa**: Unit test for Semgrep child agent
- **Dampak**: Validates tool wrapper before integration

### File 11: `tests/test_gitleaks_scanner.py`

- **Lokasi**: [L1-L100]
- **Perubahan**:
  - Mock `subprocess.run()` to return sample Gitleaks JSON output
  - Test `scan()` correctly parses findings
  - Test error handling: tool not found, invalid JSON, timeout
  - Test redaction of secret values
- **Mengapa**: Unit test for Gitleaks child agent
- **Dampak**: Validates tool wrapper before integration

### File 12: `tests/test_finding_validator.py`

- **Lokasi**: [L1-L80]
- **Perubahan**:
  - Test validator rejects findings missing required fields
  - Test validator de-duplicates by (path, line, rule_id)
  - Test validator sorts by severity
  - Test validator accepts valid schema
- **Mengapa**: Unit test for schema validation
- **Dampak**: Ensures strict schema compliance

---

## Urutan Eksekusi (Steps with "Uji Cepat" per Step)

### Langkah 1: Set Up Project Structure & Dependencies

**Files**: `setup.py`, `requirements.txt`, `config/`

**Perubahan**:
1. Create `setup.py` with dependencies: `semgrep`, `gitleaks`, `typer`, `pydantic`, `jsonschema`
2. Create `requirements.txt` with pinned versions
3. Create config directories: `config/semgrep/`, `config/gitleaks/`
4. Verify all directories exist

**Uji Cepat**:
```bash
python -m pip install -e .
python -c "import semgrep; import gitleaks; print('OK')"
semgrep --version
gitleaks --version
ls -la config/
```

**Expected**: All tools installed, directories exist, no errors.

---

### Langkah 2: Implement Finding Schema & Validator

**Files**: `contracts/child_agent_schema.json`, `src/validators/finding_validator.py`

**Perubahan**:
1. Create JSON schema (already in step 1)
2. Implement `FindingValidator` class with schema loading
3. Implement `validate_all()` method with de-duplication

**Uji Cepat**:
```bash
python -m pytest tests/test_finding_validator.py -v
# Expected: All tests pass (schema validation, de-dup, sorting)
```

---

### Langkah 3: Implement Semgrep Analyzer Child Agent

**Files**: `src/tools/semgrep_analyzer.py`, `tests/test_semgrep_analyzer.py`

**Perubahan**:
1. Create `SemgrepAnalyzer` class
2. Implement `analyze(repo_path)` with subprocess call
3. Add JSON parsing and error handling
4. Write unit tests with mocked subprocess

**Uji Cepat**:
```bash
python -m pytest tests/test_semgrep_analyzer.py::test_analyze_success -v
python -m pytest tests/test_semgrep_analyzer.py::test_analyze_tool_not_found -v
# Expected: All unit tests pass
```

---

### Langkah 4: Implement Gitleaks Scanner Child Agent

**Files**: `src/tools/gitleaks_scanner.py`, `tests/test_gitleaks_scanner.py`

**Perubahan**:
1. Create `GitleaksScanner` class
2. Implement `scan(repo_path)` with subprocess call
3. Add JSON parsing, secret redaction, and error handling
4. Write unit tests with mocked subprocess

**Uji Cepat**:
```bash
python -m pytest tests/test_gitleaks_scanner.py::test_scan_success -v
python -m pytest tests/test_gitleaks_scanner.py::test_redact_secrets -v
# Expected: All unit tests pass, secrets redacted
```

---

### Langkah 5: Implement Output Formatters

**Files**: `src/formatters/output_formatter.py`

**Perubahan**:
1. Create `OutputFormatter` class
2. Implement `to_json()`, `to_sarif()`, `to_html()`
3. Test each format with sample findings

**Uji Cepat**:
```bash
python -c "
from src.formatters.output_formatter import OutputFormatter
fmt = OutputFormatter()
sample = [{'tool': 'semgrep', 'path': 'test.py', 'lines': 'L1-L5', 'message': 'test'}]
print(fmt.to_json(sample))  # Should print valid JSON
"
```

**Expected**: All three formats produce valid output (JSON, SARIF, HTML).

---

### Langkah 6: Implement Parent Orchestrator

**Files**: `src/security_orchestrator.py`, `tests/test_security_orchestrator.py`

**Perubahan**:
1. Create `SecurityScanner` class with `__init__()` and `scan()`
2. Call child agents sequentially
3. Merge findings, validate, return
4. Write orchestration tests (mocked children)

**Uji Cepat**:
```bash
python -m pytest tests/test_security_orchestrator.py::test_scan_merged_findings -v
python -m pytest tests/test_security_orchestrator.py::test_scan_handles_tool_errors -v
# Expected: All tests pass, orchestration logic works
```

---

### Langkah 7: Implement CLI Entry Point

**Files**: `src/cli.py`, `tests/test_cli.py`

**Perubahan**:
1. Create `typer.Typer()` app
2. Add `scan` command with args: `repo_path`, `--format`, `--output`
3. Implement command handler: parse args, instantiate orchestrator, format, save
4. Write CLI tests

**Uji Cepat**:
```bash
python -m src.cli scan /path/to/test/repo --format json --output /tmp/findings.json
test -f /tmp/findings.json && echo "OK" || echo "FAIL"
cat /tmp/findings.json | python -m json.tool > /dev/null && echo "Valid JSON"
```

**Expected**: CLI produces valid JSON output file.

---

### Langkah 8: Configure Semgrep Rules

**Files**: `config/semgrep/rules.yaml`

**Perubahan**:
1. Create rules config with Semgrep registry + custom rules
2. Exclude noisy paths (`.git`, `node_modules`, etc.)
3. Set timeouts and limits

**Uji Cepat**:
```bash
semgrep --config config/semgrep/rules.yaml --validate-rules > /dev/null
# Expected: Rules are valid, no errors
```

---

### Langkah 9: Configure Gitleaks Ignore Patterns

**Files**: `config/gitleaks/.gitleaksignore`

**Perubahan**:
1. Add false-positive patterns (test creds, dummy strings)
2. Test on sample repo with known false positives

**Uji Cepat**:
```bash
gitleaks detect --source . --config config/gitleaks/.gitleaksignore --json | python -m json.tool
# Expected: False positives filtered out
```

---

### Langkah 10: Integration Test (End-to-End)

**Files**: `tests/test_integration.py`

**Perubahan**:
1. Create test fixture repo with known vulnerabilities (SQL injection, hardcoded secret)
2. Run full orchestrator on fixture
3. Verify findings detected, formatted correctly

**Uji Cepat**:
```bash
python -m pytest tests/test_integration.py::test_end_to_end_scan -v
# Expected: All findings detected, valid SARIF/JSON output
```

---

### Langkah 11: Test Coverage & Documentation

**Files**: `README.md`, all test files

**Perubahan**:
1. Run coverage: `pytest --cov=src --cov-report=html`
2. Ensure ≥80% coverage
3. Write README: architecture, usage, integration examples

**Uji Cepat**:
```bash
pytest --cov=src --cov-report=term-missing
# Expected: ≥80% coverage, no major gaps
```

---

### Langkah 12: GitHub Actions CI/CD & Docker

**Files**: `.github/workflows/security-scan.yml`, `Dockerfile`

**Perubahan**:
1. Create GitHub Actions workflow: run security scan on PR
2. Create Dockerfile for containerized scanning
3. Test workflow locally with `act`

**Uji Cepat**:
```bash
docker build -t security-orchestrator .
docker run security-orchestrator scan /tmp/repo --format json
# Expected: Docker image builds, scan runs inside container
```

---

## Acceptance Criteria (including Edge Cases)

1. **Schema Compliance**: 100% of findings validated against `child_agent_schema.json`
2. **Tool Integration**: Semgrep & Gitleaks both run, findings merged
3. **Error Handling**: If tool not found or crashes, orchestrator continues (graceful degradation)
4. **Output Formats**: JSON, SARIF, HTML all produce valid, parseable output
5. **De-duplication**: Duplicate findings (same path/line/rule) appear only once
6. **Secret Redaction**: No raw secrets in logs or output (gitleaks-specific)
7. **Test Coverage**: ≥80% coverage for `src/` modules
8. **Performance**: Scan on test repo completes in <10s
9. **CLI Usability**: `--help` works, args validated, errors clear
10. **CI/CD Ready**: GitHub Actions workflow passes, Docker image builds

---

## Rollback & Guardrails

### Feature Flags
- `ENABLE_SEMGREP`: disable Semgrep child if needed (return empty findings)
- `ENABLE_GITLEAKS`: disable Gitleaks child if needed (return empty findings)
- `STRICT_VALIDATION`: if False, skip invalid findings instead of failing

### Rollback Procedure
1. If findings are wrong: revert config files (`config/semgrep/rules.yaml`, `.gitleaksignore`)
2. If child agent crashes: disable via env var, continue with other tools
3. If output format breaks: revert formatter code, use JSON-only fallback
4. If integration fails: roll back to Langkah N-1 (isolated tool testing)

### Kill Switch
- Set `ORCHESTRATOR_DISABLED=true` → orchestrator returns empty findings (safe default)

---

## Risiko Sisa & Mitigasi

| Risk | Mitigation |
|------|-----------|
| Semgrep/Gitleaks in PATH not found at runtime | Verify in `setup.py` install step; document in README |
| Large repos timeout (>100k files) | Implement timeout with partial results; add `--max-target-size` to semgrep |
| Output file too large (>100MB JSON) | Stream results; implement chunking for very large repos |
| SARIF format incorrect for GitHub | Test with GitHub Code Scanning API; validate with `sarif validate` tool |
| False positives in findings | Configure `.gitleaksignore` and Semgrep rules carefully; add custom rule tests |
| Child agents are not idempotent | Always re-validate findings; don't cache across runs |

---

## Summary

**Total Implementation Steps**: 12 phases (Langkah 1-12)

**Key Milestones**:
- Langkah 1-2: Foundation (deps, schema)
- Langkah 3-4: Child agents (Semgrep, Gitleaks)
- Langkah 5-6: Orchestration & formatting
- Langkah 7-9: CLI & configuration
- Langkah 10-12: Integration, testing, deployment

**Expected Timeline**: 12-16 hours of coding + testing (assuming ~45 min per Langkah)

**Definition of Done**: All 12 Langkah completed, ≥80% test coverage, CLI functional, GitHub Actions workflow passing.
