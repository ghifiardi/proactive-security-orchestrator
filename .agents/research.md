# Scope
- Target change/bug/feature: Force GitHub Actions to pick up the latest security workflow by touching `.github/workflows/security-scan.yml` without altering logic.
- Components/Services: `.github/workflows/security-scan.yml` (workflow definition used by upstream repos).

# Peta File & Simbol (path + [Lx-Ly] + 1-line role)
- `.github/workflows/security-scan.yml [L1-L133]` – defines the security scan workflow, including install, scan, and upload steps.

# Alur Eksekusi end-to-end (linked to lines)
1. Workflow triggers via push/PR/dispatch (`security-scan.yml [L3-L16]`).
2. Job `security-scan` runs steps to install tools, run scanner, upload SARIF/artifacts ([L21-L103]).
3. External repos consume workflow via `workflow_call`; they require refreshed YAML to apply changes.

# Tes & Observabilitas (tests, log, how-to-run)
- No automated tests for comments; verification is by pushing commit and watching GitHub use updated workflow (new run should show `upload-sarif@v4` etc.).
- Optional lint: `actionlint .github/workflows/security-scan.yml` to confirm syntax unaffected.

# Risiko & Asumsi
- Workflow logic must remain unchanged; only harmless metadata/comment addition allowed.
- Assume touching file (comment) is sufficient to force GitHub to reload definition.
- No CI run locally; relies on GitHub to execute after commit.

# Bukti (3–5 mini snippets only)
```21:103:.github/workflows/security-scan.yml
# Existing workflow already includes PYTHONPATH export, pinned rich, v4 uploads.
```
```1:20:.github/workflows/security-scan.yml
name: Security Scan
on:
  workflow_call: ...
```
```0:0:GitHub UI
Workflow run still shows v3 upload → indicates old commit snapshot in effect.
```
