# Prompt Packet Examples and Golden Samples

## 1. Purpose

Prompt Packet Examples and Golden Samples document and test the minimum expected format for Codex task packets.

They make the Lite validator easier to maintain by providing one known-good packet and focused invalid packets that represent common omissions.

---

## 2. Directory layout

Golden samples live under:

```text
examples/task_packets/valid/
examples/task_packets/invalid/
```

Valid samples must pass `scripts/validate_task_packet.py`.

Invalid samples must fail with validation exit code `1`.

STEP 160 adds Strict Mode samples that must be validated with `--strict`.

---

## 3. Valid sample

The valid sample is:

```text
examples/task_packets/valid/step_valid_minimal_task_packet.md
```

The Strict valid sample is:

```text
examples/task_packets/valid/step_valid_strict_task_packet.md
```

It is intentionally compact but includes the minimum sections required by Prompt Packet Hardening and Prompt Packet Validation Lite:

- project context;
- branch instructions;
- allowed scope;
- forbidden scope;
- forbidden actions;
- Verification Gate;
- Documentation Sync;
- Soft Protection awareness;
- Final Codex report.

---

## 4. Invalid samples

The invalid samples are focused on one missing concept each:

```text
examples/task_packets/invalid/missing_forbidden_actions.md
examples/task_packets/invalid/missing_scope.md
examples/task_packets/invalid/missing_final_report.md
examples/task_packets/invalid/strict_missing_bypass_guard.md
```

They are not examples to copy. They exist to document mistakes the validator should catch:

- missing forbidden actions and no commit/push/PR/merge constraints;
- missing allowed scope and forbidden scope;
- missing final Codex report.
- missing `ASF_ALLOW_MAIN_BYPASS` guard in Strict Mode.

---

## 5. How to run validation

Valid sample:

```powershell
python scripts/validate_task_packet.py examples/task_packets/valid/step_valid_minimal_task_packet.md
```

Expected result: exit code `0`.

Invalid sample:

```powershell
python scripts/validate_task_packet.py examples/task_packets/invalid/missing_forbidden_actions.md
```

Expected result: exit code `1`.

The same failure expectation applies to all files under `examples/task_packets/invalid/`.

Strict sample:

```powershell
python scripts/validate_task_packet.py --strict examples/task_packets/valid/step_valid_strict_task_packet.md
```

Expected result: exit code `0`.

Strict invalid sample:

```powershell
python scripts/validate_task_packet.py --strict examples/task_packets/invalid/strict_missing_bypass_guard.md
```

Expected result: exit code `1`.

---

## 6. Relationship with Lite validator

Prompt Packet Validation Lite checks sections and keywords, not full semantic quality.

Golden samples protect the expected validator behavior:

- the valid sample should remain accepted;
- invalid samples should remain rejected;
- future validator changes can be tested without guessing the intended behavior.

They do not replace Alberto review, the Verification Gate, Documentation Sync or test execution.

---

## 7. Strict mode and future hardening

STEP 160 introduces Prompt Packet Validation Strict Mode in `docs/28_PROMPT_PACKET_VALIDATION_STRICT_MODE.md`.

Possible improvements:

- more granular checks;
- JSON report output;
- optional JSON/YAML schema;
- more golden samples for different task types.
