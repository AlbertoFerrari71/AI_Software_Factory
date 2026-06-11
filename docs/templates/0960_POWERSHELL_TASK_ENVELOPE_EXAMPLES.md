# 0960 - PowerShell Task Envelope Examples

## Dry-run read-only status

```json
{
  "task_id": "0960-git-status",
  "working_directory": "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
  "command_kind": "native_read_only",
  "script_path": "",
  "arguments": ["git", "--no-pager", "status", "--short"],
  "allowed_paths": ["C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory"],
  "forbidden_patterns": ["destructive_reset", "destructive_clean", "publish_without_approval"],
  "timeout_seconds": 60,
  "idle_timeout_seconds": 15,
  "stdout_path": "tmp\\supervised_loop\\0960-git-status-stdout.txt",
  "stderr_path": "tmp\\supervised_loop\\0960-git-status-stderr.txt",
  "full_output_path": "tmp\\supervised_loop\\0960-git-status-full.log",
  "compact_output_path": "tmp\\supervised_loop\\0960-git-status-compact.md"
}
```

Run validation only:

```powershell
python scripts/asf_powershell_task_runner.py --envelope tmp\0960-git-status.json --json
```

## Workflow health

```json
{
  "task_id": "0960-workflow-health",
  "working_directory": "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
  "command_kind": "python_read_only",
  "script_path": "scripts\\check_workflow_health.py",
  "arguments": ["python", "scripts/check_workflow_health.py"],
  "allowed_paths": ["C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory"],
  "forbidden_patterns": ["publish_without_approval", "merge_without_approval", "deploy_without_approval"],
  "timeout_seconds": 300,
  "idle_timeout_seconds": 60,
  "stdout_path": "tmp\\supervised_loop\\0960-health-stdout.txt",
  "stderr_path": "tmp\\supervised_loop\\0960-health-stderr.txt",
  "full_output_path": "tmp\\supervised_loop\\0960-health-full.log",
  "compact_output_path": "tmp\\supervised_loop\\0960-health-compact.md"
}
```

Execute only after review:

```powershell
python scripts/asf_powershell_task_runner.py --envelope tmp\0960-health.json --execute --json
```
