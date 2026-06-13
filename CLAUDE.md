# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

AI Software Factory is **not an application** — it is a local-first, safety-first *workflow framework* (internal method: "Codex Alchemy Method") for turning natural-language software ideas into controlled, human-gated implementation steps. The deliverables are living documentation (`docs/`), reusable templates (`templates/`), machine-readable safety policies (`policies/`), and a set of standalone Python/PowerShell **runner scripts** (`scripts/`) that orchestrate a human-supervised pipeline across ChatGPT, Codex, GitHub, and tests.

`src/ai_software_factory/` is an intentional **skeleton only** — every module README says "STEP 030 skeleton only, no application logic yet." Do not assume application logic lives there. The actual working tools are the CLI scripts under `scripts/`. The pilot/test-bed project for the method is *Family Photo Organizer* (a separate repo).

`AGENTS.md` is the authoritative operating contract for any agent working here — **read it first**. The points below summarize the parts most likely to trip you up.

## Commands

Setup and tests (Windows / PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest                 # full suite (pytest config in pyproject.toml: testpaths=tests, pythonpath=src)
python -m pytest tests/unit/test_asf_risk_classifier.py            # single file
python -m pytest tests/unit/test_asf_risk_classifier.py::test_name # single test
python -m pytest -k "publish_step"                                 # by keyword
```

Verification gate before any commit/push/PR (mirrors CI in `.github/workflows/ci.yml`):
```powershell
python -m pytest
python scripts/check_workflow_health.py          # read-only: validates workflow docs/script cross-references
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1   # pytest + git diff --check + git status
git --no-pager diff --check
git --no-pager status --short
```
CI runs only on Python 3.13 (Ubuntu): `pip install -e ".[dev]"`, `pytest`, `git diff --check`. Requires Python >= 3.11. There is **no linter or formatter** configured — match surrounding style. Dependencies are stdlib-only by design (only dev dep is `pytest`); do not add runtime dependencies without explicit approval.

Read-only status helpers: `python scripts/show_workflow_status.py`.

## Architecture: the runner scripts

Most scripts in `scripts/` follow the same contract — they are **dry-run / planning tools that emit structured JSON + Markdown evidence and never perform Git, GitHub, publish, merge, or live-API actions on their own.** They are deterministic and fail-closed. Each script has a paired `docs/` doc (numbered) and a `tests/unit/test_*.py`. Key clusters:

- **Prompt/Task Packet pipeline:** `generate_task_packet.py`, `validate_task_packet.py` (`--strict` opt-in), golden samples in `examples/task_packets/{valid,invalid}/`.
- **ASF "Motore" (engine) MVP** — a local supervised gate loop (docs in `docs/motor/`, examples in `examples/`): `asf_dry_run_loop_runner.py` → `asf_risk_classifier.py` (rule-based L0–L4 + required gate) → `asf_gate_decision_report.py` → `asf_verification_profile_selector.py` → `asf_publish_config_generator.py` → `asf_step_state_machine.py` (JSON state under `tmp/`) → `asf_motor_run_manifest.py` (evidence pack) → `asf_e2e_mvp_smoke.py`.
- **Codex read-only invocation prototypes:** `asf_codex_*` scripts — invocation must stay read-only; never enable workspace-write or danger-full-access.
- **OpenAI adapter:** `asf_openai_api_adapter.py` and friends — dry-run/mock by default, no SDK, no live calls without explicit gates (`ASF_OPENAI_LIVE_*` env + `--confirm-live-openai`).
- **`scripts/asf_publish_step.ps1`** — the canonical PowerShell publish runner. Phases via `-Phase {Plan|PrepareConfig|A|B|C}`: Phase A = local verification; **Phase B requires `-ApprovePublish`**, **Phase C requires `-ApproveMerge` and `-PrNumber`**. Driven by an explicit JSON config (see `examples/publish_step/`, `examples/publish_runner/`). Prefer this over hand-pasting large PowerShell blocks into chat.

`docs/34_PROJECT_WORKFLOW_INDEX.md` is the master "I need to do X → which doc/script/template" table. `docs/36_WORKFLOW_QUICK_REFERENCE.md` and `docs/38_WORKFLOW_COMMAND_COOKBOOK.md` are the command cookbooks.

## ASF supervised loop direction

STEP 0940 defines the final ASF V1 supervised loop architecture. Claude, Fabula, Mythos or other support agents may help with planning, review and diagnostics, but must not bypass the lane model:

- deterministic lane: PowerShell Fast Lane for known low-risk commands;
- reasoning lane: GPT / ChatGPT for plans, reviews and diagnostics;
- code-editing lane: Codex CLI / `codex exec` for local edits only when a step authorizes it.

The handoff between lanes goes through Bridge files, `state.json`, reports and semaphores. GPT does not directly execute PowerShell; a local supervisor or runner must authorize and execute allowed tools. Alberto remains the approval gate for publish, merge, deploy and strategic milestone decisions.

No support agent should write automatic OS appunti, create hidden publication steps, or convert warnings into success without evidence.

## Critical conventions

- **Step numbering:** all work is organized as numbered steps `NNNN) Title` inside a series namespace. Use cross-series references such as `motor/1050`, `collaboration/0200`, or `skills/0260`; a four-digit number is unique only inside its directory/series. Preserve existing numbering when adding docs and do not renumber historical gaps.
- **Artifact naming:** progressive artifacts use `NNNN-II-Tipo_Nome.ext`. `LAST-*` is deprecated as a general repository artifact pattern. The only exception is standard operational Bridge output under Bridge/codex_command, Bridge/pwsh_command, or existing publish runner/state machine Bridge mirrors. Do not create permanent repository artifacts named `LAST-*`; to find the latest durable artifact of a type, use `max(II)` for `(step, type)`.
- **The "Bridge":** the ChatGPT Bridge is operational scratch storage, **not authoritative** — Git and versioned files are the source of truth. Test-time Bridge output must go under `tmp/` or an ignored location, never to real Dropbox.
- **Human gates are mandatory:** do not commit, push, open PRs, merge, tag, or deploy unless the user explicitly asks. If asked, run the verification gate first and stop on failure. Publishing to `main` is **branch + PR by default**; direct push to `main` is forbidden absent an explicit emergency bypass.
- **Scope discipline:** do not delete/move/rename/overwrite files outside the requested scope; do not modify external target repositories unless explicitly requested. A target repo becoming dirty after a read-only run is a serious safety failure.
- **Git warnings:** treat LF/CRLF warnings as non-blocking when `git diff --check`, tests, and the verify gate pass (exit code 0).
- **PowerShell command packs:** use a short safe bootstrap that writes a full `.ps1`, validates with `[scriptblock]::Create(...)`, then runs `pwsh -NoProfile -ExecutionPolicy Bypass -File`. Use `Invoke-NativeChecked` / explicit native exit-code checks and `ArgList` (never `$Args` as a parameter name). Avoid fragile nested here-strings and outer `try/finally` in pasted blocks. Any pasted PowerShell block must end with `# terminatore copia-incolla` followed by one real blank final line; do not use `WScript.Shell`, `SendKeys`, or automatic Enter as the default paste-completion workaround.
- **Encoding:** keep `AGENTS.md` and `docs/` ASCII-only to avoid mojibake.

## Final report format

When closing an implementation step, write the user-facing final report **in Italian** (unless asked otherwise), using the lettered structure A–J defined in `AGENTS.md` (Step eseguito, Stato, File creati/modificati, Sintesi tecnica, Test eseguiti, Verifiche Git, Vincoli rispettati, Problemi aperti/warning, Prossimo step consigliato, Riepilogo finale). Update the relevant docs / `docs/34_PROJECT_WORKFLOW_INDEX.md` / `CHANGELOG.md` / `README.md` when a change affects workflow behavior.
