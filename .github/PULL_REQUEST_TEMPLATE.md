# Pull Request Template

**Link this PR to planning & research artifacts to maintain mental alignment.**

## Context

**Research link**: `.agents/research.md` § [Section Number/Title]

**Plan link**: `.agents/plan.md` § Langkah [Number] -- [Title]

**Progress from**: `.agents/progress.md` § Langkah [N-1]

---

## Ringkasan Perubahan (Summary of Changes)

- [ ] Langkah ke-[N] sesuai rencana
- Changes are bounded to plan.md's specified files & line ranges

### Files Changed
- `path/to/file1.py`: [L50-L100]
- `path/to/file2.yaml`: [L1-L30]

### Dampak singkat (Short Impact)
Describe the change in 1–2 sentences. Examples:
- "Implemented SecurityScanner.scan() to orchestrate child agents (Semgrep, Gitleaks)"
- "Added finding validator with JSON schema enforcement"
- "Created output formatter for SARIF integration"

---

## Verifikasi (Verification)

### Test Command & Results

```bash
# Run tests for this Langkah
pytest tests/test_[module].py -v --cov=src/[module]
```

**Result**:
```
PASSED: [Test names]
Coverage: X% (target: ≥80%)
Duration: Xs
```

**Logs** (if applicable):
```
[Paste relevant logs or error messages]
```

### Manual Testing (if applicable)

```bash
# Example: CLI test
python -m src.cli scan /tmp/test-repo --format json --output /tmp/findings.json
cat /tmp/findings.json | python -m json.tool > /dev/null && echo "Valid JSON ✅"
```

**Result**: [Describe what you verified]

---

## Risiko & Rollback (Risks & Rollback)

### Known Risks
- [ ] Tool version compatibility (e.g., semgrep ≥1.45, gitleaks ≥8.16)
- [ ] Subprocess timeouts (mitigated by timeout parameter)
- [ ] Invalid JSON from tools (mitigated by error handling)
- [ ] Large repos (mitigated by partial results)
- [ ] False positives in findings (mitigated by config exclusions)

### Rollback Procedure

**If this PR breaks**:

1. **Identify issue** (test failure, regression, config error)
2. **Revert** this PR: `git revert HEAD`
3. **Check previous Langkah**: see `.agents/progress.md` § Langkah [N-1]
4. **Fix & re-test**: understand root cause, create targeted fix
5. **Document** in decisions.md why the original approach didn't work

### Feature Flags (if applicable)

If this PR adds a new feature that should be toggleable:

```python
import os

ENABLE_SEMGREP = os.getenv("ENABLE_SEMGREP", "true").lower() == "true"
ENABLE_GITLEAKS = os.getenv("ENABLE_GITLEAKS", "true").lower() == "true"

if ENABLE_SEMGREP:
    findings.extend(self.semgrep.analyze(repo_path))
```

**To disable**: `export ENABLE_SEMGREP=false` before running

---

## Mental Alignment (Why This Design)

### What Changed & Why

**From research**: [Link to research.md finding]

**Plan rationale**: [Link to plan.md explanation]

**Implementation approach**: [2–3 sentences on why this code, not alternatives]

### Example
```
From research.md §Alur Eksekusi, we need a parent orchestrator 
that calls child agents sequentially. 

Plan.md §Langkah 6 specifies:
- SecurityScanner class with scan(repo_path) method
- Call SemgrepAnalyzer, then GitleaksScanner
- Merge findings, validate, return

Implementation: Created SecurityScanner in src/security_orchestrator.py
with __init__(config_dir) and scan(repo_path). Child agents are 
instantiated in __init__, called in sequence in scan(). Error handling 
ensures one tool failure doesn't crash the orchestrator.
```

### decisions.md Updated?

- [ ] **Yes**: Updated `.agents/decisions.md` with rationale
- [ ] **No**: No decisions to document (straightforward implementation)
- [ ] **N/A**: Feature flag not needed

If "Yes": briefly describe the decision (e.g., "Sequential vs. parallel execution: chose sequential for simplicity; can parallelize in v2")

---

## Checklist Before Merging

- [ ] All tests pass (`pytest` shows ≥80% coverage)
- [ ] Diff is bounded to Langkah N (no scope creep)
- [ ] No unrelated refactoring or cleanup
- [ ] Commit message references Langkah (e.g., "[Langkah 5] Implement output formatters")
- [ ] PR links to `.agents/research.md` & `.agents/plan.md`
- [ ] Context hygiene: `.agents/progress.md` updated with ≤20 lines
- [ ] Risks documented (if any)
- [ ] Rollback procedure clear
- [ ] Code is reviewed by at least one other person

---

## Post-Merge (Next Steps)

After this PR is merged:

1. **Update progress.md**: Move "Langkah N" to "Complete" section
2. **Review plan.md**: Confirm Langkah N+1 dependencies are met
3. **Open new Composer session** for Langkah N+1 if not already started
4. **Link new PR** to plan.md § Langkah N+1

---

## Questions for Reviewer

1. **Is the scope correct?** (Does it match plan.md § Langkah N?)
2. **Are tests sufficient?** (Do they cover edge cases from research.md?)
3. **Is error handling robust?** (What if tool not found? Timeout? Invalid JSON?)
4. **Is this code production-ready?** (Would you deploy this?)
5. **Any alternative approaches?** (Feedback on design decisions)

---

## Additional Notes

[Use this section for any clarifications, links to related issues, or follow-up tasks.]

Example:
- Related to issue #123 (parent orchestrator integration)
- Follow-up PR needed for CI/CD integration (Langkah 12)
- Known limitation: doesn't support parallel tool execution (future work)
