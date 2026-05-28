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

---

## 3. Valid sample

The valid sample is:

```text
examples/task_packets/valid/step_valid_minimal_task_packet.md
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
```

They are not examples to copy. They exist to document mistakes the validator should catch:

- missing forbidden actions and no commit/push/PR/merge constraints;
- missing allowed scope and forbidden scope;
- missing final Codex report.

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

---

## 6. Relationship with Lite validator

Prompt Packet Validation Lite checks sections and keywords, not full semantic quality.

Golden samples protect the expected validator behavior:

- the valid sample should remain accepted;
- invalid samples should remain rejected;
- future validator changes can be tested without guessing the intended behavior.

They do not replace Alberto review, the Verification Gate, Documentation Sync or test execution.

---

## 7. Future strict mode

STEP 160 can introduce Prompt Packet Validation Strict Mode.

Possible improvements:

- strict mode;
- more granular checks;
- JSON report output;
- optional JSON/YAML schema;
- more golden samples for different task types.
