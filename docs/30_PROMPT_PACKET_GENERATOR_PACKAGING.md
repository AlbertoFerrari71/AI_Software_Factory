# Prompt Packet Generator Packaging

## 1. Purpose

Prompt Packet Generator Packaging makes the local task packet generator easier to use without turning the repository into a published Python package.

In this project, packaging means adding thin local entry points, documentation, a generated sample, and tests around the existing CLI. The main logic remains in `scripts/generate_task_packet.py`.

---

## 2. Local packaging scope

This step adds:

- Python CLI usage as the canonical path;
- a thin PowerShell wrapper in `scripts/generate_task_packet.ps1`;
- a generated sample in `examples/task_packets/generated/`;
- tests that verify the packaging surface.

This step does not add:

- PyPI publishing;
- a package registry;
- PATH changes;
- PowerShell profile changes;
- hook installation;
- dependency changes;
- CI changes.

---

## 3. Why not PyPI yet

The generator is still part of the local-first method. Publishing it externally would add packaging, versioning, distribution, and support decisions before the interface is stable.

For now, repository-local usage is enough:

- Alberto can run the generator directly;
- Codex can test generated task packets locally;
- docs and examples stay versioned with the method.

---

## 4. Python CLI usage

Use the Python CLI directly when scripting or when the current shell already has Python active:

```powershell
python scripts/generate_task_packet.py --step 180 --title "Prompt Packet Generator Packaging" --branch step-180-prompt-packet-generator-packaging --objective "Package the prompt packet generator for local-first usage." --output tmp/generated_step_180_task_packet.md --force --strict-ready
```

The CLI validates required arguments, creates the output directory when needed, and writes Markdown.

---

## 5. PowerShell wrapper usage

Use the wrapper when working from PowerShell and preferring native parameter names:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\generate_task_packet.ps1 -Step 180 -Title "Prompt Packet Generator Packaging" -Branch "step-180-prompt-packet-generator-packaging" -Objective "Package the prompt packet generator for local-first usage." -Output "tmp\generated_step_180_task_packet.md" -Force -StrictReady
```

The wrapper only translates PowerShell parameters to the Python CLI:

```text
scripts/generate_task_packet.ps1 -> scripts/generate_task_packet.py
```

It does not duplicate validation or generation logic.

---

## 6. Where to save generated packets

Recommended locations:

- `tmp/` for local drafts and manual tests;
- `examples/task_packets/generated/` for versioned generated samples;
- a step-specific working folder only when explicitly requested by the task packet.

Do not save generated packets in secret, environment, dependency, CI, or source-code areas unless a future step explicitly changes the policy.

---

## 7. Validation

Validate generated packets with Lite Mode:

```powershell
python scripts/validate_task_packet.py tmp/generated_step_180_task_packet.md
```

When `--strict-ready` or `-StrictReady` is used, also validate with Strict Mode:

```powershell
python scripts/validate_task_packet.py --strict tmp/generated_step_180_task_packet.md
```

Lite and Strict remain manual checks in this step. They are not added to CI or `scripts/verify.ps1`.

---

## 8. Generated sample

The reference generated sample for this step is:

```text
examples/task_packets/generated/step_180_generated_packaging_sample.md
```

It is generated from the Python CLI with `--strict-ready` and should pass both Lite and Strict validation.

---

## 9. Current limits

The packaging surface is intentionally small.

Current limits:

- no installer;
- no console script entry point;
- no registry publication;
- no JSON/YAML schema;
- no automatic validation after generation;
- no automatic integration with the Verification Gate.

These limits keep the generator easy to review and keep operational control with Alberto.

---

## 10. Future work

Future steps can add:

- a release smoke workflow for the generator;
- onboarding documentation for local users;
- optional validation after generation;
- package metadata only if local usage proves stable;
- a documented local release checklist.
