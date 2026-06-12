# 1080 - Codex Report JSON Sidecar and Latest Resolver

## Purpose

Keep the human Markdown report mandatory and add a machine-readable JSON
sidecar for deterministic review.

## JSON sidecar

Schema: `docs/templates/codex_report.schema.json`.

Minimum fields include:

- schema_version;
- project;
- step or step_range;
- step_title;
- status;
- branch;
- files_created, files_modified, files_deleted;
- checks;
- risks;
- decisions_required;
- next_step;
- report_markdown_path;
- bridge_paths;
- forbidden_actions_confirmed;
- human_gate_required;
- summary.

## Resolver

Script: `scripts/asf_latest_report_resolver.py`.

Examples:

```powershell
python scripts/asf_latest_report_resolver.py --bridge "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\codex_command" --expected-step 1050 --json
python scripts/asf_latest_report_resolver.py --bridge "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\codex_command" --latest
```

Resolver behavior:

- prefers valid JSON sidecar;
- links Markdown when present;
- reports Markdown-only as degraded;
- reports missing, ambiguous and incoherent states explicitly;
- never turns incoherent JSON into PASS.

## Acceptance

- JSON schema is versioned.
- Resolver is stdlib-only and tested.
- Markdown report remains mandatory.
