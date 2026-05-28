# Prompt Packet Validation Strict Mode

## 1. Purpose

Prompt Packet Validation Strict Mode adds more granular checks to the Lite validator for important Codex task packets.

Strict Mode is still keyword-based and lightweight. It does not introduce a formal schema, but it catches more incomplete packets before Codex starts work.

---

## 2. Lite vs Strict

| Mode | Checks | Use |
|---|---|---|
| Lite | Minimum sections and essential keywords | Fast validation and compatibility with existing task packets |
| Strict | Granular checks for branch, scope, forbidden actions, Verification Gate, Documentation Sync, Soft Protection and final report | Important, complex or sensitive task packets |

Lite remains the default mode.

Strict is opt-in and must be requested explicitly.

---

## 3. Usage

Lite mode:

```powershell
python scripts/validate_task_packet.py <file>
```

Strict mode:

```powershell
python scripts/validate_task_packet.py --strict <file>
```

The output reports the active mode:

```text
Mode: Lite
```

or:

```text
Mode: Strict
```

---

## 4. Strict checks

Strict Mode checks:

- branch instructions include a dedicated branch, `main`, and working tree awareness;
- allowed scope has a concrete allowed path pattern;
- forbidden scope includes `src/**`, `policies/**`, CI, secret or `.env` references;
- forbidden actions include no commit, no push, no PR, no merge, no direct GitHub changes, no hook install or hooksPath change, and no `ASF_ALLOW_MAIN_BYPASS`;
- Verification Gate includes `python -m pytest`, `git diff --check`, and `git status --short`;
- Documentation Sync includes `CHANGELOG.md`, roadmap and decisions;
- Soft Protection includes soft guardrails or Soft Protection, `.githooks` or `core.hooksPath`, and hook opt-in or no-install wording;
- Final Codex report includes all required A-I sections and the final summary fields.

Strict Mode may warn when a packet does not reference golden samples. That warning is informational unless the project later makes it required.

---

## 5. Exit codes

Exit codes:

- `0` passed;
- `1` failed because one or more required checks are missing;
- `2` usage or input error.

---

## 6. Golden samples

Strict Mode samples are documented in `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md`.

Valid Strict sample:

```text
examples/task_packets/valid/step_valid_strict_task_packet.md
```

Invalid Strict sample:

```text
examples/task_packets/invalid/strict_missing_bypass_guard.md
```

Run:

```powershell
python scripts/validate_task_packet.py --strict examples/task_packets/valid/step_valid_strict_task_packet.md
python scripts/validate_task_packet.py --strict examples/task_packets/invalid/strict_missing_bypass_guard.md
```

The valid sample must return exit code `0`. The invalid sample must return exit code `1`.

---

## 7. Limitations

Strict Mode is not:

- a formal schema;
- a full semantic validator;
- a replacement for Alberto review;
- a replacement for the Verification Gate;
- a replacement for tests.

A task packet can pass Strict Mode and still be wrong if the objective, scope or risk assessment is poor.

---

## 8. Future hardening

STEP 170 can continue with Prompt Packet Generator CLI Hardening.

Future steps can add:

- optional JSON/YAML schema;
- JSON report output;
- CI integration;
- integration in `scripts/verify.ps1`;
- validation of multiple templates;
- stricter checks by task type.
