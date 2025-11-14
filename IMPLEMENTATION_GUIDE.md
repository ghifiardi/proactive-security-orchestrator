# Implementation Guide: Using the Orchestrator

This guide walks you through **setting up and using** the Proactive Codebase Testing orchestrator in your Cursor IDE to integrate Semgrep + Gitleaks.

---

## Part 1: Initial Setup (5 min)

### 1.1 Extract Files

Ensure you have the complete orchestrator directory structure:

```
orchestrator/
├── .agents/
├── prompts/
├── contracts/
├── config/
├── src/
├── tests/
├── .github/
├── .cursorrules
├── setup.py
├── README.md
└── [other files]
```

### 1.2 Install Dependencies

```bash
cd orchestrator

# Install Python package + dependencies
python -m pip install -e .

# Verify Semgrep & Gitleaks are installed
semgrep --version
gitleaks --version

# If not installed:
pip install semgrep gitleaks
```

### 1.3 Run Tests (to confirm setup)

```bash
pytest tests/ -v --tb=short

# Expected: All tests pass (or most pass if tools not found)
# Expected output: "X passed"
```

---

## Part 2: Open Cursor & Prepare (5 min)

### 2.1 Open Your Project in Cursor

```bash
cd orchestrator
cursor .
```

### 2.2 Create/Verify `.cursorrules` File

Ensure `.cursorrules` exists in the project root. This enforces the workflow.

```bash
ls -la .cursorrules
# Should show the .cursorrules file
```

Cursor will automatically read this file and enforce the guardrails.

### 2.3 Prepare Prompts

All prompts are in `prompts/` directory:
- `parent_system_prompt.md` (set as SYSTEM)
- `research_prompt.md` (for Phase A)
- `plan_prompt.md` (for Phase B)
- `implement_prompt.md` (for Phase C)

Keep this window open: `File → Open File → prompts/parent_system_prompt.md`

---

## Part 3: Phase A – RESEARCH (90 min)

### 3.1 Open Composer

In Cursor:
```
Ctrl+K (or Cmd+K on Mac) → "Composer"
```

### 3.2 Set System Prompt

In Composer:
1. Click **"System"** dropdown (top-left)
2. Paste entire contents of: `prompts/parent_system_prompt.md`
3. (Optional) Save as reusable prompt: "Proactive Testing Orchestrator"

### 3.3 Paste Research Prompt

In the **User** box:

```
[Copy entire contents of prompts/research_prompt.md here]

TARGET CHANGE: Integrate Semgrep + Gitleaks into orchestrator
              to automatically detect security vulnerabilities
              and secrets before code deployment.

Codebase location: /path/to/orchestrator
```

### 3.4 Run Composer

Click **"Generate"** or press Ctrl+Enter (Cmd+Enter on Mac)

**Expected output**:
- Parent orchestrator reads the target
- (If codebase is large) spawns child agents (Surveyor, Symbol Mapper, Test Enumerator)
- Produces `.agents/research.md` with:
  - §Scope
  - §Peta File & Simbol (file map)
  - §Alur Eksekusi (execution flow)
  - §Tes & Observabilitas
  - §Risiko & Asumsi
  - §Bukti (code snippets)

### 3.5 Human Review: Approve or Revise

**Open `.agents/research.md`**:

```bash
cat .agents/research.md | less
```

**Checklist**:
- [ ] Scope is clear (target feature, components)
- [ ] File map complete (all key files listed)
- [ ] Execution flow makes sense (entry → exit)
- [ ] Risks documented
- [ ] Evidence snippets are accurate

**If unclear**: Edit research.md or run Directed Restart:

```
HENTIKAN. Sesi baru untuk research.

Fokus pada: [specific section that's unclear]

Ulangi riset dengan perhatian khusus.
```

Then go back to 3.3 & rerun Composer with clarification.

**If approved**: Proceed to Phase B.

---

## Part 4: Phase B – PLAN (120 min)

### 4.1 Keep Cursor Composer Open

Same Composer session, same System prompt (parent_system_prompt.md).

### 4.2 Paste Plan Prompt

In the **User** box, replace research_prompt with:

```
[Copy entire contents of prompts/plan_prompt.md here]

Using .agents/research.md, create the implementation plan.
```

### 4.3 Run Composer

Click **"Generate"** or Ctrl+Enter

**Expected output**:
- Parent reads `.agents/research.md`
- Produces `.agents/plan.md` with:
  - §Goal & Non-Goals
  - §Perubahan per File (changes per file)
  - §Urutan Eksekusi (Langkah 1..12 with uji cepat commands)
  - §Acceptance Criteria
  - §Rollback & Guardrails
  - §Risiko Sisa & Mitigasi

### 4.4 Human Review: Approve or Revise

**Open `.agents/plan.md`**:

```bash
cat .agents/plan.md | less
```

**Checklist**:
- [ ] Each Langkah is atomic (≤1 hour work)
- [ ] Uji cepat (test command) is clear & fast
- [ ] Dependencies ordered (Langkah 1 before 2, etc.)
- [ ] Acceptance criteria are testable
- [ ] Rollback procedure documented
- [ ] PR grouping makes sense (≤300 LOC per PR)

**If unclear**: Request refinement or Directed Restart.

**If approved**: Proceed to Phase C.

---

## Part 5: Phase C – IMPLEMENT (Langkah 1..N, ~45 min each)

### 5.1 For Each Langkah (starting with Langkah 1):

#### Step 5.1.1: Paste Implement Prompt

In **User** box:

```
[Copy entire contents of prompts/implement_prompt.md here]

LANGKAH: 1

[Copy the "Langkah 1" section from .agents/plan.md]
```

#### Step 5.1.2: Run Composer

Click **"Generate"** or Ctrl+Enter

**Expected output**:
- Unified diff patch (shows changes to make)
- Test command & results
- Update for `.agents/progress.md` (≤20 lines)

#### Step 5.1.3: Review Diff & Apply

In Cursor:
1. Select the diff section from Composer output
2. Right-click → **"Apply Diff"** (or equivalent)
3. OR manually copy/paste changes into files

#### Step 5.1.4: Run Test Command

In Cursor Terminal:

```bash
pytest tests/test_security_orchestrator.py -v
# Or whatever uji cepat command is in the diff
```

**Expected**: Tests pass ✅

#### Step 5.1.5: Verify Progress Update

Open `.agents/progress.md`:

```bash
cat .agents/progress.md | tail -30
```

Should see new section: "## Langkah N -- Ringkasan"

#### Step 5.1.6: Commit & Open PR

```bash
git add -A
git commit -m "[Langkah 1] Set up project structure & dependencies"
# Create PR using GitHub UI
```

Link PR to `.agents/research.md` and `.agents/plan.md` in PR description.

#### Step 5.1.7: Repeat for Langkah 2, 3, ... N

Return to 5.1.1, but now paste "Langkah 2" instead of Langkah 1.

Continue until all 12 Langkah are complete.

---

## Part 6: Post-Implementation (30 min)

### 6.1 Verify Full Test Coverage

```bash
pytest tests/ -v --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Expected**: ≥80% coverage

### 6.2 Test on Real Repository

```bash
python -m src.cli scan ~/my-project --format json --output findings.json

# View findings
cat findings.json | python -m json.tool | head -50
```

**Expected**: Valid JSON, findings detected

### 6.3 Generate Outputs

```bash
# JSON output
python -m src.cli scan ~/my-project --format json --output findings.json

# SARIF output (for GitHub)
python -m src.cli scan ~/my-project --format sarif --output findings.sarif

# HTML dashboard
python -m src.cli scan ~/my-project --format html --output dashboard.html
open dashboard.html
```

### 6.4 Docker Build & Test (Optional)

```bash
# Build container
docker build -t security-orchestrator .

# Test container
docker run -v ~/my-project:/repo security-orchestrator scan /repo --format json
```

### 6.5 Document Decisions

Update `.agents/decisions.md`:

```markdown
# Design Decisions

## Decision 1: Sequential vs. Parallel Tool Execution
- **Chosen**: Sequential (Semgrep first, then Gitleaks)
- **Why**: Simpler error handling, easier to debug
- **Future**: Can parallelize in v2 if performance is bottleneck
```

### 6.6 Final Checklist

- [ ] All 12 Langkah complete
- [ ] Test coverage ≥80%
- [ ] All PRs merged
- [ ] Manual testing passed
- [ ] Docker image builds
- [ ] README updated
- [ ] decisions.md documented
- [ ] GitHub Actions workflow configured

---

## Troubleshooting During Implementation

### Issue: Composer Can't Find Code

**Cause**: `.cursorrules` not read

**Solution**: 
```bash
# Verify .cursorrules exists
ls -la .cursorrules

# Restart Cursor (hard reload)
Cursor → Quit
cursor .
```

### Issue: Langkah Requires Out-of-Scope Changes

**Example**: Plan says "change lines 50–60" but you need to change lines 50–60 + 100–110

**Solution**: **Request Directed Restart**

In Composer, paste:

```
HENTIKAN. Langkah N scope drift.

Plan specifies [Lx-Ly]. Implementation needs [OTHER RANGE].

Direktur restart untuk clarify scope atau split Langkah.
```

Then refine `.agents/plan.md` and restart.

### Issue: Test Fails After Applying Diff

**Cause**: Diff applied incorrectly or syntax error

**Solution**:
```bash
# Debug the test
pytest tests/test_X.py -vvs --tb=long

# View what changed
git diff src/

# If broken: revert
git checkout src/file.py
```

Then run Composer again for the same Langkah.

### Issue: Context Too Heavy (Composer feels slow)

**Cause**: Too much pasted into Composer (>40% of window)

**Solution**: Summarize progress.md ruthlessly

In `.agents/progress.md`:
```markdown
# CONDENSED SUMMARY (was 100 lines, now 15)

## Langkah 1–5 Complete
- ✅ Setup, schema, Semgrep, Gitleaks, formatters working
- ✅ All tests passing (80%+ coverage)
- ✅ No blockers

## Current State (Langkah 6)
- Next: Implement orchestrator
- See full history in git log
```

Then use this condensed version in Composer.

### Issue: Stuck on a Langkah

**Solution**: Debug in isolation

```bash
# Create debug branch
git checkout -b debug/langkah-N

# Make test pass
pytest tests/test_X.py -vvs

# Once fixed, revert plan & try again
git checkout .
```

---

## Quick Command Reference

```bash
# Setup
python -m pip install -e .
semgrep --version && gitleaks --version

# Tests
pytest tests/ -v
pytest tests/test_X.py::test_foo -v
pytest --cov=src --cov-report=html

# CLI
python -m src.cli scan /repo --format json --output findings.json
python -m src.cli scan /repo --format sarif --output findings.sarif
python -m src.cli scan /repo --format html --output dashboard.html

# Docker
docker build -t security-orchestrator .
docker run -v /repo:/repo security-orchestrator scan /repo --format json

# Git
git status
git diff
git commit -m "[Langkah N] Title"
git log --oneline | head -20

# View artifacts
cat .agents/research.md | less
cat .agents/plan.md | less
cat .agents/progress.md | tail -50
```

---

## Success Metrics

✅ **Phase A Complete** when `.agents/research.md` is approved

✅ **Phase B Complete** when `.agents/plan.md` is approved

✅ **Phase C Complete** when:
- All 12 Langkah implemented
- All tests pass (≥80% coverage)
- All PRs merged
- `.agents/progress.md` shows "Complete ✅" for all Langkah
- Manual testing on real repo works

✅ **Production Ready** when:
- Docker image builds
- GitHub Actions passes
- SARIF output compatible with GitHub Code Scanning
- `.agents/decisions.md` documented

---

## Next Steps After Implementation

1. **Deploy**: Push Docker image to registry, configure GitHub Actions
2. **Integrate**: Add to your CI/CD pipeline (GitHub, GitLab, Jenkins, etc.)
3. **Monitor**: Track findings over time, measure security improvements
4. **Extend**: Add more tools (Trivy, Sonarqube, etc.) using same orchestrator pattern
5. **Share**: Use this orchestrator as template for other spec-first LLM projects

---

## Questions?

Refer to:
- **README.md**: Quick start, directory structure, usage examples
- **ARCHITECTURE.md**: Technical deep-dive, data flow, schemas
- **.agents/research.md**: Investigation findings
- **.agents/plan.md**: Implementation plan
- **.agents/progress.md**: Execution log
- **prompts/parent_system_prompt.md**: Orchestrator rules

---

## Key Principles

🔒 **Spec First**: Research → Plan → Code (never skip phases)

🎯 **Atomic Steps**: Each Langkah ≤1 hour, testable, no dependencies (except ordering)

📝 **Artifact-Driven**: All decisions documented in `.agents/`

🔍 **Context Hygiene**: Keep Composer <40%, reference instead of paste

✅ **Reversible**: Every change can be rolled back, feature flags available

🤖 **LLM-Friendly**: Prompts structured for consistency, schemas enforce quality

---

Done! You now have a **production-ready Proactive Codebase Testing orchestrator**. 🚀

Next: Run Phase A!

```bash
cursor .
# Open Composer → System: parent_system_prompt.md
# User: research_prompt.md + target change
# Run → Generates .agents/research.md
```

Good luck! 🎉
