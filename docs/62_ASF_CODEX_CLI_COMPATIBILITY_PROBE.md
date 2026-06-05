# 62 - ASF Codex CLI Compatibility Probe

## 1. Scope

This document defines the local Codex CLI compatibility probe.

The probe is metadata-only by default. It checks command availability and help output. It must not call the model and must not modify any repository.

## 2. Script

```text
scripts/asf_codex_cli_compatibility_probe.py
```

Example:

```powershell
python scripts/asf_codex_cli_compatibility_probe.py --output-json tmp/asf_codex_cli_compatibility_probe/cli_compatibility_probe.json --output-markdown tmp/asf_codex_cli_compatibility_probe/cli_compatibility_probe.md
```

To probe a specific command path:

```powershell
python scripts/asf_codex_cli_compatibility_probe.py --codex-command C:\Tools\codex.cmd --output-json tmp/asf_codex_cli_compatibility_probe/cli_compatibility_probe.json
```

## 3. Metadata inspected

When the executable is available, the probe inspects:

- executable presence;
- `codex --version`;
- `codex --help`;
- `codex exec --help`;
- support evidence for `exec`;
- support evidence for `--sandbox`;
- support evidence for `read-only`;
- support evidence for `--json`;
- support evidence for `--output-last-message`;
- support evidence for stdin prompt using `-` when clearly present in help.

## 4. Missing Codex

If the command is missing, the probe emits:

```text
CODEX_NOT_AVAILABLE
```

This is not a target failure. It means the environment cannot run the read-only Codex trial now.

## 5. Output contract

The JSON output contains:

- `schema_version`;
- `report_type`;
- `mode: metadata-only`;
- `calls_model: false`;
- executable evidence;
- classifications;
- version probe output excerpts;
- support evidence;
- individual probe command results.

## 6. Safety limits

- The probe does not run `codex exec` with a prompt.
- The probe does not call the model.
- The probe does not enable workspace-write.
- The probe does not use danger-full-access.
- The probe does not modify any repository.

