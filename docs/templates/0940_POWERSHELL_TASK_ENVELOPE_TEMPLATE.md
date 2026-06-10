# 0940 - PowerShell Task Envelope Template

This template describes one deterministic task that PowerShell Fast Lane may execute after policy checks.

```json
{
  "task_id": "task-0001",
  "step_id": "0940",
  "working_directory": "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
  "command_kind": "script_file",
  "script_path": "scripts\\verify.ps1",
  "arguments": [],
  "allowed_paths": [
    "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
    "D:\\FG-SAB Dropbox\\Alberto Ferrari\\ChatGPT_Bridge\\AI_Software_Factory"
  ],
  "forbidden_patterns": [
    "destructive_reset",
    "destructive_clean",
    "rebase",
    "destructive_checkout",
    "push_without_approval",
    "merge_without_approval",
    "deploy_without_approval",
    "os_appunti_write",
    "secret_read_or_exfiltration"
  ],
  "timeout_seconds": 900,
  "idle_timeout_seconds": 120,
  "max_retry_absolute": 10,
  "current_retry": 0,
  "expected_exit_codes": [0],
  "safe_stderr_patterns": [
    "LF will be replaced by CRLF",
    "CRLF will be replaced by LF",
    "Already up to date."
  ],
  "output_paths": {
    "stdout": "supervised_loop\\task-0001-stdout.txt",
    "stderr": "supervised_loop\\task-0001-stderr.txt",
    "report": "supervised_loop\\task-0001-report.json"
  },
  "classification": {
    "risk_level": "L1",
    "lane": "deterministic",
    "failure_class": null
  },
  "status": "READY",
  "next_recommended_action": "RUN"
}
```

## Validation rules

- `working_directory` must be inside an allowed repository path.
- `script_path` must be relative to `working_directory` unless explicitly approved.
- `max_retry_absolute` must never exceed 10.
- `current_retry` must be less than or equal to `max_retry_absolute`.
- Any publish, merge, deploy or destructive action requires Alberto approval and must not run in Fast Lane by default.
- Output paths must stay under Bridge or another authorized local evidence root.

