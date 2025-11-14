# Plan Prompt: Detailed Per-File Implementation Planning

**INPUT**: `.agents/research.md` (anggap akurat)

**TUGAS**: Buat rencana implementasi rinci ke `.agents/plan.md`

**KELUARAN**: Sesuai format "plan.md" (lihat `.cursorrules`). Wajib:
- Perubahan per file dengan [Lx-Ly]
- Urutan langkah + "uji cepat" tiap langkah
- Acceptance Criteria + Rollback/Flag
- Pecah jadi PR kecil (≤~300 LOC/PR)

---

## Core Instructions

You are acting as a **PLANNING AGENT** for the Proactive Codebase Testing orchestrator. Your job is to **convert research into a concrete, step-by-step implementation plan** that developers can execute reliably.

### What You Must Do

1. **Parse research.md**:
   - Extract all files and symbols from the "Peta File & Simbol" section
   - Understand the execution flow (Alur Eksekusi)
   - Note risks, assumptions, and mitigation strategies

2. **Define implementation steps (Langkah 1..N)**:
   - Each Langkah should be **small and verifiable** (≤1 hour of work)
   - Include a quick test command ("uji cepat") for each Langkah
   - Order steps logically: dependencies first, then higher-level features

3. **For each file that will change**:
   - Specify path and line ranges [Lx-Ly]
   - Describe concrete changes (bullets, not paragraphs)
   - Link changes to research findings (because, impacts)
   - Note which other files are affected

4. **Define acceptance criteria**:
   - What does "done" look like?
   - Include edge cases
   - Reference test cases

5. **Plan for rollback**:
   - Feature flags or kill switches
   - How to revert if something breaks
   - What to do if a tool fails

6. **Estimate PR size**:
   - Split implementation into small PRs (~300 LOC each)
   - Each PR maps to 2–4 Langkah

---

## Sections to Include in `.agents/plan.md`

### 1. **Goal & Non-Goals**
   - What are we building? (1–2 sentences)
   - What are we NOT building?

### 2. **Perubahan per File** (Changes per File)
   - For each file: path, [Lx-Ly], concrete changes, why, impact
   - Link changes to research.md findings

### 3. **Urutan Eksekusi** (Execution Order)
   - Langkah 1, 2, 3, ... (numbered steps)
   - Each Langkah has: files, changes, uji cepat command, expected result
   - Langkah should be atomic: doable in one session, testable immediately

### 4. **Acceptance Criteria**
   - Functional: what the code must do
   - Non-functional: performance, coverage, compatibility
   - Edge cases: what must not break

### 5. **Rollback & Guardrails**
   - Feature flags (how to disable if broken)
   - Rollback steps (revert files, restore state)
   - Kill switch (safe default)

### 6. **Risiko Sisa & Mitigasi** (Remaining Risks & Mitigation)
   - What could still go wrong?
   - How do we detect & fix it?

---

## How to Structure Langkah (Implementation Steps)

Each Langkah should follow this pattern:

```markdown
### Langkah N: [Short Title]

**Files**: path1.py, path2.py, config.yaml

**Perubahan**:
1. In path1.py [Lx-Ly]: Do X (because research point Y)
2. In path2.py [Lx-Ly]: Do Z (impacts other-file.py)
3. In config.yaml: Add Y setting

**Uji Cepat**:
\`\`\`bash
command_to_verify_step
\`\`\`

**Expected**: Result description (what success looks like)
```

### Characteristics of a Good Langkah

- **Atomic**: Completes in one session (~45 min)
- **Testable**: Has a quick `uji cepat` command
- **Clear**: No ambiguity; developer knows what to do
- **Bounded**: Touches only the files listed
- **Precedent**: Doesn't depend on unfinished Langkah

---

## Template: `.agents/plan.md` Structure

```markdown
# Plan: [Feature Name] Implementation

## Goal & Non-Goals

### Goal
[What we're building]

### Non-Goals
[What we're not building]

---

## Perubahan per File

### File 1: src/module.py

- **Lokasi**: [Lx-Ly]
- **Perubahan**: (bullets)
- **Mengapa**: (link to research)
- **Dampak**: (other files affected)

### File 2: config/settings.yaml

- **Lokasi**: [Lx-Ly]
- **Perubahan**: (bullets)
- **Mengapa**: (link to research)
- **Dampak**: (other files affected)

---

## Urutan Eksekusi (Steps with Quick Tests)

### Langkah 1: [Title]
- **Files**: path1.py, path2.py
- **Perubahan**: (bullets)
- **Uji Cepat**: \`command\`
- **Expected**: result

### Langkah 2: [Title]
- **Files**: path3.py
- **Perubahan**: (bullets)
- **Uji Cepat**: \`command\`
- **Expected**: result

...

---

## Acceptance Criteria

1. Functional: ...
2. Functional: ...
3. Non-functional: coverage ≥80%
4. Edge case: ...

---

## Rollback & Guardrails

### Feature Flags
- FLAG_X: disables feature X
- FLAG_Y: disables feature Y

### Rollback Procedure
1. Revert files
2. Restore state
3. Clear cache (if applicable)

### Kill Switch
- Env var: DISABLE_FEATURE=true

---

## Risiko Sisa & Mitigasi

| Risk | Mitigation |
| ... | ... |
```

---

## Langkah Size Guidelines

### Too Small (< 15 min)
- Just adding imports
- Single-line changes
- Combine with other Langkah

### Right Size (30–60 min)
- Implement one function + tests
- Add config file + validation
- Integrate two modules

### Too Large (> 120 min)
- Multiple major features
- Heavy refactoring
- Break into 2–3 Langkah

---

## PR Mapping

After you define all Langkah, group them into PRs:

```
PR 1 (Foundation): Langkah 1–2
PR 2 (Core Logic): Langkah 3–4
PR 3 (Integration): Langkah 5–7
PR 4 (Testing & Docs): Langkah 8–12
```

Each PR: ≤300 LOC, includes tests, follows PULL_REQUEST_TEMPLATE.md

---

## How to Use This Prompt in Cursor

1. **Open Composer** → set your system prompt to the PARENT system prompt (below)
2. **In User box**, paste:
   ```
   [PASTE PLAN_PROMPT.MD ABOVE]
   
   Using research from .agents/research.md, create the implementation plan.
   ```
3. **Parent generates** `.agents/plan.md` with all Langkah steps
4. **Human reviews** plan, confirms:
   - [ ] All Langkah are atomic & testable
   - [ ] Dependencies ordered correctly
   - [ ] Uji cepat commands are clear
   - [ ] Acceptance criteria are complete

---

## Directed Restart (If Plan Is Unclear)

If implementation plan has gaps or is too vague:

```
HENTIKAN. Sesi baru untuk planning.

Baca ulang: .agents/research.md (§Alur Eksekusi, §Risiko)

Fokus pada Langkah [N]: lebih jelas, detailnya [X, Y, Z]

Ulangi planning dengan perhatian khusus.
```

---

## Quick Reference: Langkah Template

Use this as a starting point for each Langkah:

```markdown
### Langkah N: [Clear, short title]

**Files**: file1.py, file2.yaml, file3.js

**Perubahan**:
- In file1.py [Lx-Ly]: Create class Foo with method bar()
- In file1.py [Lx-Ly]: Add error handling for case X
- In file2.yaml: Add config key Y with default value Z
- Why: From research.md §[Section], we need this for [reason]
- Impacts: file3.js will call Foo.bar(), so ensure return type is Y

**Uji Cepat**:
\`\`\`bash
pytest tests/test_module.py::test_foo_bar -v
\`\`\`

**Expected**: test_foo_bar passes, coverage for file1.py [Lx-Ly] increases
```

---

## Post-Plan Checklist

After plan is complete, human should verify:

- [ ] Every Langkah is ≤1 hour of work
- [ ] Uji cepat commands are simple & fast
- [ ] Dependencies ordered (no forward refs)
- [ ] Acceptance criteria are testable
- [ ] Rollback steps documented
- [ ] PR grouping makes sense (≤300 LOC each)
- [ ] All research.md findings addressed

**If any section unclear → back to planning (Directed Restart)**
