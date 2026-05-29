# Prompt Packet Generator Release Smoke Workflow

## 1. Purpose

The Prompt Packet Generator Release Smoke Workflow is a local-first smoke check for the task packet generator.

It verifies that the local generator wrapper can create a task packet and that the generated packet passes both Prompt Packet Validation Lite Mode and Strict Mode.

This is not a public release process. It is a quick operator check before considering the generator usable after local changes.

---

## 2. Why local

The generator is an internal repository tool. A local smoke workflow is enough for this stage because it:

- runs without GitHub writes;
- avoids PyPI or registry publishing;
- avoids CI changes;
- keeps verification close to the files being changed;
- gives Alberto a fast copy/paste command.

---

## 3. What it checks

The smoke workflow checks:

- the PowerShell wrapper `scripts/generate_task_packet.ps1`;
- generation of a temporary task packet under `tmp/`;
- Lite Mode validation with `scripts/validate_task_packet.py`;
- Strict Mode validation with `scripts/validate_task_packet.py --strict`;
- clear exit status for pass or fail.

---

## 4. What it does not check

The smoke workflow does not:

- run the full Verification Gate;
- replace `python -m pytest`;
- replace CI;
- publish a package;
- create a GitHub Release;
- create a pull request;
- change Git configuration;
- install hooks;
- validate every possible task packet scenario.

---

## 5. Difference from Verification Gate

The Verification Gate checks the repository state more broadly: tests, whitespace diff, Git status, and other project-level checks.

The release smoke workflow is narrower. It checks only that the Prompt Packet Generator can be used locally through the wrapper and that the produced packet passes Lite Mode and Strict Mode.

Use both when the generator changes:

1. run the release smoke workflow for generator usability;
2. run the Verification Gate for repository readiness.

For the full operating sequence from task packet preparation to merge on `main`, use `docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md`.

For a quick operator-oriented introduction to generator, validation, smoke workflow and lifecycle, use `docs/33_PROMPT_PACKET_GENERATOR_DEVELOPER_ONBOARDING.md`.

---

## 6. Difference from CI

CI runs remotely on GitHub Actions and validates the repository on push or pull request.

This smoke workflow runs locally before commit, push, PR, or merge. It is intentionally not wired into CI in STEP 190.

---

## 7. Usage

Run with defaults:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_prompt_packet_release.ps1
```

Default output:

```text
tmp\smoke_prompt_packet_release.md
```

Optional custom output must still stay under `tmp/`:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_prompt_packet_release.ps1 -Output "tmp\custom_smoke_packet.md"
```

---

## 8. Interpreting results

Positive result:

```text
Prompt Packet Generator Release Smoke Workflow PASSED
```

This means the wrapper generated a task packet and both Lite Mode and Strict Mode validation passed.

Negative result:

- the script exits with a non-zero code;
- the failing step is printed;
- the generated temporary output can be inspected under `tmp/` if it exists.

Fix the smallest relevant issue, then rerun the smoke workflow.

---

## 9. Relationship with Lite Mode and Strict Mode

Lite Mode confirms that the packet contains the minimum required sections and keywords.

Strict Mode confirms the stronger task packet requirements introduced for important steps: branch awareness, allowed scope, forbidden scope, forbidden actions, Verification Gate, Documentation Sync, Soft Protection, and the final Codex report.

The smoke workflow always runs both.

---

## 10. Current limits

Current limits:

- no CI integration;
- no package metadata;
- no installer;
- no GitHub Release;
- no PyPI or registry publication;
- no automatic cleanup of the `tmp/` output;
- no semantic review of the generated task packet objective.

These limits are intentional for STEP 190.

---

## 11. Future work

Future steps can add:

- optional smoke checks for generated examples;
- release checklist wording for local-only tool updates;
- eventual CI opt-in if the workflow proves stable.
