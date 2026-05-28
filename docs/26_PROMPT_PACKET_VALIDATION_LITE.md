# Prompt Packet Validation Lite

## 1. Purpose

Prompt Packet Validation Lite validates Codex task packets with a small set of required sections and concepts.

The goal is to catch incomplete prompts before Codex starts work, without turning task packets into a rigid schema too early.

---

## 2. What it checks

The validator checks for the minimum operating contract introduced by Prompt Packet Hardening:

- project context;
- branch instructions;
- allowed scope;
- forbidden scope;
- forbidden actions;
- no commit, no push, no PR and no merge constraints;
- Verification Gate;
- Documentation Sync;
- Soft Protection awareness;
- Final Codex report.

The checks are based on robust keywords and short section names, not long exact sentences.

---

## 3. What it does not check

Prompt Packet Validation Lite is not:

- a formal schema;
- a complete semantic quality review;
- a replacement for Alberto review;
- a replacement for the Verification Gate;
- a replacement for tests.

A task packet can pass the validator and still need human correction if the objective, scope, risks or rollback are unclear.

---

## 4. Usage

Run the validator against a Markdown or text task packet:

```powershell
python scripts/validate_task_packet.py templates/codex_tasks/codex_task_packet_template.md
```

The output reports each required check as `PASS` or `FAIL`, optional warnings, and a final result.

---

## 5. Exit codes

Exit codes:

- `0` passed;
- `1` failed because one or more required checks are missing;
- `2` usage or input error, such as missing file, unsupported extension or invalid UTF-8.

Warnings do not fail validation unless a required check is missing.

---

## 6. Recommended workflow

Use the validator:

- before handing a complex task packet to Codex;
- when updating the central Codex task packet template;
- when preparing examples that should become reusable references.

In STEP 140 the validator is a manual support tool. It is not integrated automatically into CI or `scripts/verify.ps1`.

---

## 7. Future hardening

STEP 150 can add Prompt Packet Examples and Golden Samples.

Future hardening can add:

- strict mode;
- JSON or YAML schema;
- golden sample validation;
- integration with the Verification Gate;
- CI integration;
- JSON report output.
