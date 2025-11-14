# Proactive Codebase Testing Orchestrator
## Semgrep + Gitleaks Integration with Research → Plan → Implement Workflow

This repository contains a **spec-first, Cursor-native orchestrator** for integrating Semgrep (static analysis) and Gitleaks (secrets detection) into a unified security scanning platform. The entire development process follows a strict **Research → Plan (per-file) → Implement** workflow with Parent/Child agent orchestration.

---

## 🎯 Quick Start

### Prerequisites
- Python 3.11+
- Cursor IDE (or compatible LLM development environment)
- `semgrep` and `gitleaks` installed locally
- Git for version control

### Installation

```bash
# Clone or extract the orchestrator
cd orchestrator

# Install dependencies
python -m pip install -e .

# Verify tools are available
semgrep --version
gitleaks --version

# Run tests to confirm setup
pytest tests/ -v --cov=src
```

### First Scan

```bash
# Scan a repository for vulnerabilities and secrets
python -m src.cli scan /path/to/repo --format json --output findings.json

# View results
cat findings.json | python -m json.tool | less

# Or generate HTML dashboard
python -m src.cli scan /path/to/repo --format html --output dashboard.html
open dashboard.html
```

---

## 📁 Directory Structure

```
orchestrator/
├── .agents/                          # Workflow artifacts (READ-ONLY after phase)
│   ├── research.md                   # Investigation document (Phase A output)
│   ├── plan.md                       # Implementation plan (Phase B output)
│   ├── progress.md                   # Step-by-step execution log (Phase C output)
│   ├── decisions.md                  # Design decisions & rationale
│   └── risks.md                      # Risk register & mitigations
│
├── prompts/                          # LLM prompt templates
│   ├── parent_system_prompt.md       # Set as Cursor SYSTEM prompt
│   ├── research_prompt.md            # Phase A: Investigation
│   ├── plan_prompt.md                # Phase B: Planning
│   └── implement_prompt.md           # Phase C: Coding
│
├── contracts/                        # JSON schemas
│   └── child_agent_schema.json       # Finding validation schema
│
├── src/                              # Core implementation
│   ├── __init__.py
│   ├── __main__.py                   # Entry point for `python -m src`
│   ├── cli.py                        # CLI interface (typer)
│   ├── security_orchestrator.py      # Parent orchestrator (SecurityScanner)
│   ├── tools/                        # Child tool agents
│   │   ├── semgrep_analyzer.py       # Semgrep wrapper
│   │   └── gitleaks_scanner.py       # Gitleaks wrapper
│   ├── formatters/                   # Output formatters
│   │   └── output_formatter.py       # JSON, SARIF, HTML
│   └── validators/                   # Validation logic
│       └── finding_validator.py      # JSON schema validation
│
├── config/                           # Tool configurations
│   ├── semgrep/
│   │   └── rules.yaml                # Semgrep ruleset
│   └── gitleaks/
│       └── .gitleaksignore           # False-positive patterns
│
├── tests/                            # Test suite
│   ├── test_security_orchestrator.py # Orchestrator tests
│   ├── test_semgrep_analyzer.py      # Semgrep wrapper tests
│   ├── test_gitleaks_scanner.py      # Gitleaks wrapper tests
│   ├── test_finding_validator.py     # Validator tests
│   ├── test_output_formatter.py      # Formatter tests
│   ├── test_cli.py                   # CLI tests
│   ├── test_integration.py           # End-to-end tests
│   └── fixtures/                     # Test data
│
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md      # PR template (links artifacts)
│   └── workflows/
│       └── security-scan.yml         # GitHub Actions CI/CD
│
├── .cursorrules                      # Guardrails for workflow (read by Cursor)
├── setup.py                          # Package metadata & dependencies
├── requirements.txt                  # Pinned versions
├── Dockerfile                        # Containerized scanner
├── .dockerignore
├── README.md                         # This file
└── ARCHITECTURE.md                   # Technical deep-dive

```

---

## 🔄 Workflow: Research → Plan → Implement

This orchestrator enforces a **strict three-phase workflow** to ensure high-quality, well-documented code. Each phase produces an artifact that is reviewed before proceeding.

### Phase A: RESEARCH (60–90 min)

**Goal**: Investigate the codebase and produce `.agents/research.md`

**How to run**:
1. Open Cursor → open Composer
2. Set **System** prompt to: `prompts/parent_system_prompt.md`
3. In **User** box, paste: `prompts/research_prompt.md`
4. Add target description (1–2 sentences):
   ```
   TARGET CHANGE: Integrate Semgrep + Gitleaks into unified orchestrator
   
   Codebase location: /path/to/orchestrator
   ```
5. Run Composer → Parent generates `.agents/research.md`
6. **Halt**: Human reviews & approves before moving to Phase B

**Output**: `.agents/research.md` with:
- Scope: target feature, components
- Peta File & Simbol: file map with [Lx-Ly] references
- Alur Eksekusi: execution flow (entry → exit, linked to code)
- Tes & Observabilitas: test coverage, how to run
- Risiko & Asumsi: risks & mitigations
- Bukti: 3–5 code snippets proving findings

### Phase B: PLAN (90–120 min)

**Goal**: Convert research into a detailed implementation plan (`.agents/plan.md`)

**Prerequisites**: Phase A research approved by human

**How to run**:
1. Same Composer, same **System** prompt
2. Paste **User** prompt: `prompts/plan_prompt.md`
3. Composer reads `.agents/research.md`, generates `.agents/plan.md`
4. **Halt**: Human reviews plan, confirms Langkah are atomic & testable

**Output**: `.agents/plan.md` with:
- Goal & Non-Goals
- Perubahan per File: for each file, [Lx-Ly], concrete changes, why, impact
- Urutan Eksekusi: Langkah 1..N, each with uji cepat command
- Acceptance Criteria: testable done-ness
- Rollback & Guardrails: feature flags, revert procedure
- Risiko Sisa: remaining risks & mitigations

### Phase C: IMPLEMENT (Langkah N, 45–60 min each)

**Goal**: Execute exactly one Langkah per session, produce working code + passing tests

**Prerequisites**: Phase B plan approved by human

**How to run** (repeat for each Langkah):
1. Same Composer, same **System** prompt
2. Paste **User** prompt: `prompts/implement_prompt.md`
3. Add current Langkah:
   ```
   LANGKAH: 1
   
   [Copy Langkah 1 from .agents/plan.md]
   ```
4. Composer implements Langkah 1:
   - Produces unified diff
   - Runs uji cepat (test command)
   - Appends ≤20 lines to `.agents/progress.md`
5. Human applies diff, runs tests, opens PR
6. Move to Langkah 2 (repeat)

**Output**: Working code + test results + progress update per Langkah

---

## 📊 Artifacts & Context Hygiene

### Artifacts (STRICT FORMAT)

These files **MUST** exist and follow exact format (enforced by `.cursorrules`):

| Artifact | Phase | Purpose | Format |
|----------|-------|---------|--------|
| `.agents/research.md` | A | Investigation | Markdown, §Scope, §Peta File, §Alur Eksekusi, §Tes, §Risiko, §Bukti |
| `.agents/plan.md` | B | Implementation plan | Markdown, §Goal, §Perubahan per File, §Urutan Eksekusi, §Acceptance, §Rollback, §Risiko |
| `.agents/progress.md` | C | Execution log | Markdown, "## Langkah N -- Ringkasan" per step (≤20 lines each) |
| `.agents/decisions.md` | A–C | Design decisions | Markdown, §Decision X: Why we chose Y instead of Z |
| `.agents/risks.md` | A–C | Risk register | Markdown table: Risk, Assumption, Mitigation |

### Context Hygiene: Keep <40% of Window

**Good** (≤40%):
- Small slice of plan.md (current Langkah only)
- Last 20 lines of progress.md
- 2–3 code snippets (just the [Lx-Ly] chunks)
- Use path + [Lx-Ly] references for everything else

**Bad** (>40%, causes drift):
- Entire research.md/plan.md pasted
- All 200 lines of progress.md
- 5 full source files
- Narrative explanation of code (just reference it)

---

## 🛠️ Prompts: How to Use in Cursor

### Step 1: Set System Prompt (One-Time)

```
Cursor → Composer → System prompt dropdown
→ Paste entire contents of: prompts/parent_system_prompt.md
→ Save (Optional: mark as "Reusable Prompt" for future projects)
```

### Step 2: Run Phase A (Research)

```
Cursor → Composer → User box
→ Paste: prompts/research_prompt.md
→ Add target: "TARGET CHANGE: [2-3 lines]"
→ Run
→ Output: .agents/research.md
→ Human review before Phase B
```

### Step 3: Run Phase B (Plan)

```
Cursor → Composer (same System prompt)
→ User box: paste prompts/plan_prompt.md
→ Run
→ Output: .agents/plan.md
→ Human review before Phase C
```

### Step 4: Run Phase C (Implement)

For each Langkah:
```
Cursor → Composer (same System prompt)
→ User box: paste prompts/implement_prompt.md + "LANGKAH: N"
→ Run
→ Output: diff patch + uji cepat results + progress.md update
→ Human applies diff, tests, opens PR
→ Repeat for Langkah N+1
```

---

## 🧪 Testing & Coverage

### Run All Tests

```bash
pytest tests/ -v --cov=src --cov-report=html
```

**Expected**: ≥80% coverage, all tests pass

### Run Specific Tests

```bash
# Test orchestrator
pytest tests/test_security_orchestrator.py -v

# Test Semgrep wrapper
pytest tests/test_semgrep_analyzer.py -v

# Test Gitleaks wrapper
pytest tests/test_gitleaks_scanner.py -v

# Test validators
pytest tests/test_finding_validator.py -v

# Test formatters
pytest tests/test_output_formatter.py -v

# Integration test (end-to-end)
pytest tests/test_integration.py::test_end_to_end_scan -v
```

### Check Coverage Report

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## 🚀 Usage Examples

### Example 1: Scan a Repository (JSON Output)

```bash
python -m src.cli scan ~/my-project --format json --output findings.json

# View findings
cat findings.json | python -m json.tool | head -50
```

### Example 2: Generate SARIF for GitHub Code Scanning

```bash
python -m src.cli scan ~/my-project --format sarif --output findings.sarif

# Upload to GitHub (in GitHub Actions workflow)
# (see .github/workflows/security-scan.yml)
```

### Example 3: Generate HTML Dashboard

```bash
python -m src.cli scan ~/my-project --format html --output dashboard.html

# Open in browser
open dashboard.html
```

### Example 4: Docker Container Scan

```bash
# Build container
docker build -t security-orchestrator .

# Scan a repo
docker run -v /path/to/repo:/repo security-orchestrator scan /repo --format json

# Or mount and output to local file
docker run -v /path/to/repo:/repo -v $(pwd):/output \
  security-orchestrator scan /repo --format json --output /output/findings.json
```

---

## ⚙️ Configuration

### Semgrep Rules (`config/semgrep/rules.yaml`)

```yaml
rules:
  - id: p/owasp-top-ten
  - id: p/cwe-top-25
  - id: p/python-security
  - id: p/gitleaks  # Detect secrets (complement to gitleaks tool)

paths:
  exclude:
    - .git
    - node_modules
    - __pycache__
    - .venv
    - *.min.js

timeout: 10
max-lines-per-finding: 5
```

### Gitleaks Ignore (`config/gitleaks/.gitleaksignore`)

```
# Test credentials (false positives)
password123
api_key_test
test_secret_key

# GitHub Actions token placeholders
GITHUB_TOKEN

# Example configurations
example_api_key: "abc123"
```

---

## 📋 PR Template & Linking

When opening a PR, use `.github/PULL_REQUEST_TEMPLATE.md`. Key sections:

- **Context**: Link to `.agents/research.md` § and `.agents/plan.md` § Langkah N
- **Changes**: Describe what changed (1–2 sentences)
- **Verification**: Report test results + coverage
- **Risks & Rollback**: Flag any risks, rollback procedure
- **Mental Alignment**: Why this design? Link to decisions.md

Example:
```markdown
## Context

Research: `.agents/research.md` § Alur Eksekusi
Plan: `.agents/plan.md` § Langkah 5

## Ringkasan Perubahan

Implemented OutputFormatter class with to_json(), to_sarif(), to_html() methods.
Converts validated findings to multiple formats for different consumers (CI/CD, GitHub, human review).

## Verifikasi

\`\`\`bash
pytest tests/test_output_formatter.py -v --cov=src/formatters
\`\`\`

Result: 6/6 tests pass ✅, 92% coverage

## Risiko & Rollback

No risks. If SARIF format breaks: revert to JSON-only fallback.

## Mental Alignment

From research.md § Alur Eksekusi, findings must be output in 3 formats.
Implemented as separate methods (to_json, to_sarif, to_html) for clarity & testability.
```

---

## 🔍 Troubleshooting

### Issue: `semgrep: command not found`

**Solution**: Install semgrep
```bash
pip install semgrep
```

Or via Homebrew:
```bash
brew install semgrep
```

### Issue: `gitleaks: command not found`

**Solution**: Install gitleaks
```bash
pip install detect-secrets  # Fallback
# OR
brew install gitleaks  # macOS
apt-get install gitleaks  # Ubuntu
```

### Issue: Orchestrator hangs on large repo

**Solution**: Set timeout or split repo
```bash
# Increase timeout (in src/security_orchestrator.py)
self.semgrep = SemgrepAnalyzer(config_dir, timeout=120)
self.gitleaks = GitleaksScanner(config_dir, timeout=120)

# OR scan subdirectory
python -m src.cli scan /path/to/repo/src --format json
```

### Issue: False positives in findings

**Solution**: Configure exclusions
```bash
# Edit config/semgrep/rules.yaml (add exclude paths)
# Edit config/gitleaks/.gitleaksignore (add false-positive patterns)
```

### Issue: Test coverage <80%

**Solution**: Check coverage report
```bash
pytest --cov=src --cov-report=term-missing tests/
# Look for "⚠️" lines not covered, add tests
```

---

## 📚 Documentation

- **ARCHITECTURE.md**: Deep-dive on data flow, schemas, tool descriptions
- **.cursorrules**: Enforcement rules for the workflow (read by Cursor)
- **prompts/parent_system_prompt.md**: LLM system prompt for orchestration
- **prompts/research_prompt.md**: Phase A prompt (investigation)
- **prompts/plan_prompt.md**: Phase B prompt (planning)
- **prompts/implement_prompt.md**: Phase C prompt (coding)

---

## 🎓 Learning Path

1. **First time?** Read `.cursorrules` + `ARCHITECTURE.md`
2. **Run Phase A**: Follow `.agents/research.md` structure
3. **Run Phase B**: Follow `.agents/plan.md` structure
4. **Run Phase C**: Execute Langkah 1, then 2, etc.
5. **Refine workflow**: Use decisions.md + risks.md for team alignment

---

## 📦 Deployment

### GitHub Actions (Automated CI/CD)

```bash
# .github/workflows/security-scan.yml already configured
# PR → GitHub Actions runs tests + scans → SARIF to Code Scanning
```

### Local CI/CD (Pre-commit Hook)

```bash
# (Optional) Add to .git/hooks/pre-commit
python -m src.cli scan . --format json > /tmp/findings.json
# Fail if critical findings detected
```

### Docker Registry

```bash
# Build & push to registry
docker build -t myregistry/security-orchestrator:latest .
docker push myregistry/security-orchestrator:latest

# Use in CI/CD
docker pull myregistry/security-orchestrator:latest
docker run myregistry/security-orchestrator:latest scan /repo
```

---

## 📖 References

- **Semgrep Docs**: https://semgrep.dev/docs/
- **Gitleaks Docs**: https://github.com/gitleaks/gitleaks
- **SARIF Spec**: https://docs.oasis-open.org/sarif/sarif/v2.1.0/csd02/sarif-v2.1.0-csd02.html
- **Cursor IDE**: https://cursor.com/
- **Typer CLI**: https://typer.tiangolo.com/

---

## 🤝 Contributing

This project follows **Research → Plan → Implement** workflow strictly.

To add a feature:
1. **Research**: Run Phase A (update `.agents/research.md`)
2. **Plan**: Run Phase B (update `.agents/plan.md`)
3. **Implement**: Run Phase C (Langkah 1..N)
4. **PR**: Link to artifacts, include test coverage

---

## 📝 License

(Add your license here)

---

## 🎉 Summary

This orchestrator provides:
- ✅ **Spec-first workflow**: Research → Plan → Implement
- ✅ **Structured artifacts**: research.md, plan.md, progress.md
- ✅ **LLM-friendly prompts**: Reusable in Cursor or any LLM IDE
- ✅ **Atomic Langkah**: Each step ≤1 hour, testable
- ✅ **Context hygiene**: <40% active window, no scope drift
- ✅ **Production-ready**: 80%+ test coverage, Docker, CI/CD

Ready to scan? 🚀

```bash
python -m src.cli scan /path/to/repo --format json --output findings.json
```

Questions? See `.agents/research.md`, `.agents/plan.md`, `.agents/progress.md`, or `ARCHITECTURE.md`.
