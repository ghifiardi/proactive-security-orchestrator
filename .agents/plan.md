# Goal & Non-Goals
- Goal: Replace `.github/workflows/security-scan.yml` content with the user-supplied workflow that installs Semgrep/Gitleaks, runs the orchestrator, and uploads SARIF/artifacts.
- Non-Goals: Preserve existing workflow_call/test job features, adjust other files, or modify orchestrator source.

# Perubahan per File
- file: .github/workflows/security-scan.yml
  - Lokasi: entire file
  - Perubahan: Overwrite current multi-job workflow with provided single-job version (push/pr/dispatch triggers, explicit steps for installs, run, uploads).
  - Mengapa: Align with user request for clean pipeline that avoids PYTHONPATH overrides and ensures SARIF output.
  - Dampak: Removes workflow_call + test job; security scanning now always uses pinned steps; downstream repos must adopt new config path `security-scan-config.yml`.

# Urutan Eksekusi (Step 1..n + "uji cepat" per step)
1. Replace YAML content per snippet, ensuring indentation accuracy (uji cepat: run `actionlint` if available or `yamllint`).
2. Save file and verify diff matches snippet; optionally dry-run security-scan command locally.

# Acceptance Criteria (incl. edge-cases)
- Workflow contains only push/pull_request/workflow_dispatch triggers.
- Steps match provided spec (checkout, setup python, install Semgrep 1.43.1 via pip, install gitleaks binary, install orchestrator via git, run security-scan with fallback creation of empty SARIF, upload via upload-sarif@v4, upload artifact `security-scan-results`).
- `continue-on-error: true` set for scan step and fallback handles missing file.
- No references to previous config path logic or test job remain.

# Rollback & Guardrails (feature flag/circuit breaker)
- Guardrail: Keep prior version in git history for rollback.
- Rollback: Revert file to previous commit if multi-repo workflow support needed again.

# Risiko Sisa & Mitigasi
- Loss of workflow_call/test job functionality; document for future re-addition if required.
- Hardcoded `security-scan-config.yml`; ensure file exists or generate placeholder to avoid empty fallback.
- Installing orchestrator from GitHub main ignores local changes; mitigate by publishing package or reintroducing workspace install if needed later.
