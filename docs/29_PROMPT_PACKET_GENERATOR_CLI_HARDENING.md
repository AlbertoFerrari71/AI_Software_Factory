# Prompt Packet Generator CLI Hardening

## 1. Purpose

Prompt Packet Generator CLI Hardening introduces a small local CLI for generating Codex task packets from explicit arguments.

The goal is to reduce copy/paste mistakes while keeping the process local-first, readable and easy to review.

---

## 2. Manual template vs CLI generator

Use the manual template when:

- the task needs heavy editing before it is ready;
- Alberto wants to write a fully custom packet;
- the task is exploratory or still in FASE 1.

Use the CLI generator when:

- step number, title, branch and objective are already known;
- a quick structured starting point is useful;
- the generated packet will be reviewed and refined before Codex execution.

The CLI does not replace human review. It creates a draft task packet.

---

## 3. Usage

Generate a task packet file:

```powershell
python scripts/generate_task_packet.py --step 170 --title "Prompt Packet Generator CLI Hardening" --branch step-170-prompt-packet-generator-cli-hardening --objective "Harden the prompt packet generator CLI." --output tmp/generated_step_170_task_packet.md --force
```

Print to stdout without writing a file:

```powershell
python scripts/generate_task_packet.py --step 170 --title "Prompt Packet Generator CLI Hardening" --branch step-170-prompt-packet-generator-cli-hardening --objective "Harden the prompt packet generator CLI." --print
```

Generate and mark the packet as Strict-ready:

```powershell
python scripts/generate_task_packet.py --step 170 --title "Prompt Packet Generator CLI Hardening" --branch step-170-prompt-packet-generator-cli-hardening --objective "Harden the prompt packet generator CLI." --output tmp/generated_step_170_task_packet.md --strict-ready --force
```

---

## 4. Arguments

Required:

- `--step`: numeric step number, multiple of 10;
- `--title`: step title;
- `--branch`: expected dedicated branch, without spaces;
- `--objective`: short step objective.

Output:

- `--output`: output Markdown file path;
- `--print`: print generated Markdown to stdout. If `--output` is omitted, stdout is the only output;
- `--force`: overwrite an existing output file;
- `--strict-ready`: add an explicit note for `validate_task_packet.py --strict`.

---

## 5. Input validation

The CLI fails with a clear error when:

- a required argument is missing;
- `--step` is not numeric;
- `--step` is not a multiple of 10;
- `--branch` is empty or contains spaces;
- `--output` already exists and `--force` is not provided;
- neither `--output` nor `--print` is provided.

The CLI creates the output directory when needed.

---

## 6. Validation relationship

Generated packets are designed to pass Prompt Packet Validation Lite:

```powershell
python scripts/validate_task_packet.py <generated-task-packet.md>
```

They are also designed to be compatible with Strict Mode:

```powershell
python scripts/validate_task_packet.py --strict <generated-task-packet.md>
```

`--strict-ready` adds an explicit Strict validation note to the generated packet. Strict Mode remains optional and is not integrated into CI or `scripts/verify.ps1` by this step.

---

## 7. Error handling

Errors are printed to stderr and return a non-zero exit code.

Examples:

- existing output file without `--force`;
- invalid step number;
- branch name with spaces.

The script does not call GitHub API, does not run Git commands, does not install hooks and does not modify `core.hooksPath`.

---

## 8. Current limits

This step does not add:

- JSON/YAML schema;
- external Python dependencies;
- CI integration;
- automatic task execution;
- GitHub writes;
- automatic validation of every generated packet.

The output is a strong starting point, not a guarantee that the task packet is semantically complete.

---

## 9. STEP 180 packaging relationship

STEP 180 adds local packaging around this CLI without changing the core generation logic.

The Python CLI remains canonical:

```text
scripts/generate_task_packet.py
```

The PowerShell wrapper is a thin convenience entry point:

```text
scripts/generate_task_packet.ps1
```

The packaging document is `docs/30_PROMPT_PACKET_GENERATOR_PACKAGING.md`, and the generated reference sample is stored under `examples/task_packets/generated/`.

---

## 10. Future hardening

Future steps can add:

- reusable output presets;
- optional validation directly after generation;
- local release smoke workflow;
- report JSON;
- stricter task-type templates;
- more golden samples for generated output.
