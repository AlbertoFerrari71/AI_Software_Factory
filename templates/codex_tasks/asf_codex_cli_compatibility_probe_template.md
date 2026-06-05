# ASF Codex CLI Compatibility Probe Template

## Scope

Probe local Codex CLI metadata compatibility without calling the model.

## Command

```powershell
python scripts/asf_codex_cli_compatibility_probe.py --output-json tmp/asf_codex_cli_compatibility_probe/cli_compatibility_probe.json --output-markdown tmp/asf_codex_cli_compatibility_probe/cli_compatibility_probe.md
```

## Required Evidence

- executable presence;
- `codex --version`;
- `codex --help`;
- `codex exec --help`;
- support evidence for `exec`;
- support evidence for `--sandbox`;
- support evidence for `read-only`;
- support evidence for `--json`;
- support evidence for `--output-last-message`;
- support evidence for stdin prompt using `-` if clearly available.

## Safety Limits

- Metadata-only.
- Do not run a model prompt.
- Do not modify any repository.
- Classify missing Codex as `CODEX_NOT_AVAILABLE`.

