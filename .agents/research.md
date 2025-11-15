# Scope
- Target change/bug/feature: Replace existing security scan workflow with provided clean version that installs orchestrator from GitHub and ensures SARIF handling.
- Components/Services: `.github/workflows/security-scan.yml` (entire job spec), orchestrator CLI entrypoint (referenced indirectly).

# Peta File & Simbol (path + [Lx-Ly] + 1-line role)
- `.github/workflows/security-scan.yml [L1-L133]` – current workflow includes workspace install logic, config path detection, multi-job setup.
- `src/cli.py` (indirect) – invoked by `security-scan` CLI; confirms expected command.

# Alur Eksekusi end-to-end (linked to lines)
1. Workflow triggers on push/PR/workflow_call ([L3-L16]) and defines jobs security-scan + test ([L21-L125]).
2. security-scan job installs Semgrep/Gitleaks, installs orchestrator with conditional logic ([L47-L85]), runs CLI, uploads SARIF/artifacts ([L86-L103]).
3. test job runs pytest for canonical repo ([L104-L134]).

# Tes & Observabilitas (tests, log, how-to-run)
- After modifying workflow, run `actionlint .github/workflows/security-scan.yml` locally if available.
- Push commit and trigger workflow via GitHub Actions UI `Run workflow` to validate.
- Observe run logs for `security-scan scan` command and presence of SARIF upload.

# Risiko & Asumsi
- Replacing workflow removes workflow_call/test job features; ensure user accepts simplified triggers.
- Hardcoding Semgrep version 1.43.1 may conflict with orchestrator requirements; rely on user-provided spec.
- CLI install from GitHub main may not include local modifications; assumed acceptable.
- Step uses static config path `security-scan-config.yml`; repo must contain file or accept missing (user-provided snippet shows literal string).

# Bukti (3–5 mini snippets only)
```21:103:.github/workflows/security-scan.yml
Existing workflow has multi-job structure and config detection to support external repos.
```
```104:134:.github/workflows/security-scan.yml
Secondary test job runs pytest for canonical repo.
```
```0:0:USER_SNIPPET
Provided YAML defines new triggers, steps, installs, and SARIF upload requirements.
```
```27:118:src/cli.py
Current CLI expects config dir argument; new workflow passes `--config "security-scan-config.yml"`.
```
```0:0:LOG_HISTORY
Prior runs show ModuleNotFoundError and rich conflicts due to old workflow state.
```
