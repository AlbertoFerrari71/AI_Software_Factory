# 0940 - PowerShell Task Envelope Template

This template describes one deterministic task that PowerShell Fast Lane may execute after policy checks.

Every task must be authorized by an envelope. Inline commands are disabled by default; prefer saved `.ps1` scripts for anything longer than a short read-only command.

## Canonical JSON shape

```json
{
  "task_id": "task-0001",
  "step_id": "0940",
  "working_directory": "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
  "command_kind": "script_file",
  "script_path": "scripts\\verify.ps1",
  "inline_command_allowed": false,
  "arguments": [],
  "allowed_paths": [
    "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
    "D:\\FG-SAB Dropbox\\Alberto Ferrari\\ChatGPT_Bridge\\AI_Software_Factory"
  ],
  "forbidden_patterns": [
    "git reset",
    "git clean",
    "git rebase",
    "git checkout --",
    "git push",
    "gh pr merge",
    "deploy",
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
  "unsafe_stderr_patterns": [
    "fatal:",
    "Authentication failed",
    "could not read Username",
    "Permission denied"
  ],
  "output_paths": [
    "supervised_loop\\task-0001-stdout.txt",
    "supervised_loop\\task-0001-stderr.txt",
    "supervised_loop\\task-0001-compact.md",
    "supervised_loop\\task-0001-full.log"
  ],
  "stdout_path": "supervised_loop\\task-0001-stdout.txt",
  "stderr_path": "supervised_loop\\task-0001-stderr.txt",
  "compact_output_path": "supervised_loop\\task-0001-compact.md",
  "full_output_path": "supervised_loop\\task-0001-full.log",
  "classification": {
    "risk_level": "L1",
    "lane": "deterministic",
    "failure_class": null
  },
  "status": "READY",
  "next_recommended_action": "RUN",
  "requires_alberto": false,
  "approval_reason": "",
  "created_at": "2026-06-10T00:00:00+02:00",
  "updated_at": "2026-06-10T00:00:00+02:00"
}
```

## Example - Phase A locale

```json
{
  "task_id": "0940-phase-a-local",
  "step_id": "0940",
  "working_directory": "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
  "command_kind": "script_file",
  "script_path": "scripts\\asf_publish_step.ps1",
  "inline_command_allowed": false,
  "arguments": ["-Phase", "A", "-ConfigPath", "examples\\publish_runner\\0940_phase_a.example.json"],
  "allowed_paths": ["C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory"],
  "forbidden_patterns": ["-ApprovePublish", "-ApproveMerge", "git push", "gh pr merge"],
  "timeout_seconds": 1200,
  "idle_timeout_seconds": 180,
  "max_retry_absolute": 10,
  "current_retry": 0,
  "expected_exit_codes": [0],
  "safe_stderr_patterns": ["LF will be replaced by CRLF", "CRLF will be replaced by LF"],
  "unsafe_stderr_patterns": ["fatal:", "Authentication failed", "Permission denied"],
  "output_paths": ["supervised_loop\\0940-phase-a-local-stdout.txt", "supervised_loop\\0940-phase-a-local-stderr.txt"],
  "stdout_path": "supervised_loop\\0940-phase-a-local-stdout.txt",
  "stderr_path": "supervised_loop\\0940-phase-a-local-stderr.txt",
  "compact_output_path": "supervised_loop\\0940-phase-a-local-compact.md",
  "full_output_path": "supervised_loop\\0940-phase-a-local-full.log",
  "classification": "VERIFY_RUNNING",
  "status": "READY",
  "next_recommended_action": "RUN_PHASE_A_ONLY",
  "requires_alberto": false,
  "approval_reason": "",
  "created_at": "2026-06-10T00:00:00+02:00",
  "updated_at": "2026-06-10T00:00:00+02:00"
}
```

## Example - git status read-only

```json
{
  "task_id": "0940-git-status-readonly",
  "step_id": "0940",
  "working_directory": "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
  "command_kind": "native_read_only",
  "script_path": "",
  "inline_command_allowed": true,
  "arguments": ["git", "--no-pager", "status", "--short"],
  "allowed_paths": ["C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory"],
  "forbidden_patterns": ["git reset", "git clean", "git push", "git merge"],
  "timeout_seconds": 60,
  "idle_timeout_seconds": 15,
  "max_retry_absolute": 10,
  "current_retry": 0,
  "expected_exit_codes": [0],
  "safe_stderr_patterns": [],
  "unsafe_stderr_patterns": ["fatal:", "Authentication failed"],
  "output_paths": ["supervised_loop\\0940-git-status-stdout.txt"],
  "stdout_path": "supervised_loop\\0940-git-status-stdout.txt",
  "stderr_path": "supervised_loop\\0940-git-status-stderr.txt",
  "compact_output_path": "supervised_loop\\0940-git-status-compact.md",
  "full_output_path": "supervised_loop\\0940-git-status-full.log",
  "classification": "POWERSHELL_READY",
  "status": "READY",
  "next_recommended_action": "CLASSIFY_WORKTREE",
  "requires_alberto": false,
  "approval_reason": "",
  "created_at": "2026-06-10T00:00:00+02:00",
  "updated_at": "2026-06-10T00:00:00+02:00"
}
```

## Example - workflow health check

```json
{
  "task_id": "0940-workflow-health",
  "step_id": "0940",
  "working_directory": "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
  "command_kind": "python_module",
  "script_path": "scripts\\check_workflow_health.py",
  "inline_command_allowed": false,
  "arguments": ["python", "scripts\\check_workflow_health.py"],
  "allowed_paths": ["C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory"],
  "forbidden_patterns": ["git push", "gh pr create", "gh pr merge", "deploy"],
  "timeout_seconds": 300,
  "idle_timeout_seconds": 60,
  "max_retry_absolute": 10,
  "current_retry": 0,
  "expected_exit_codes": [0],
  "safe_stderr_patterns": [],
  "unsafe_stderr_patterns": ["Traceback", "Permission denied"],
  "output_paths": ["supervised_loop\\0940-workflow-health-stdout.txt", "supervised_loop\\0940-workflow-health-stderr.txt"],
  "stdout_path": "supervised_loop\\0940-workflow-health-stdout.txt",
  "stderr_path": "supervised_loop\\0940-workflow-health-stderr.txt",
  "compact_output_path": "supervised_loop\\0940-workflow-health-compact.md",
  "full_output_path": "supervised_loop\\0940-workflow-health-full.log",
  "classification": "VERIFY_RUNNING",
  "status": "READY",
  "next_recommended_action": "CONTINUE_IF_PASSED",
  "requires_alberto": false,
  "approval_reason": "",
  "created_at": "2026-06-10T00:00:00+02:00",
  "updated_at": "2026-06-10T00:00:00+02:00"
}
```

## Example - verify.ps1

```json
{
  "task_id": "0940-verify-ps1",
  "step_id": "0940",
  "working_directory": "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
  "command_kind": "script_file",
  "script_path": "scripts\\verify.ps1",
  "inline_command_allowed": false,
  "arguments": ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\\verify.ps1"],
  "allowed_paths": ["C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory"],
  "forbidden_patterns": ["git push", "gh pr create", "gh pr merge", "deploy", "os_appunti_write"],
  "timeout_seconds": 1200,
  "idle_timeout_seconds": 180,
  "max_retry_absolute": 10,
  "current_retry": 0,
  "expected_exit_codes": [0],
  "safe_stderr_patterns": ["LF will be replaced by CRLF", "CRLF will be replaced by LF"],
  "unsafe_stderr_patterns": ["fatal:", "Authentication failed", "Permission denied"],
  "output_paths": ["supervised_loop\\0940-verify-stdout.txt", "supervised_loop\\0940-verify-stderr.txt"],
  "stdout_path": "supervised_loop\\0940-verify-stdout.txt",
  "stderr_path": "supervised_loop\\0940-verify-stderr.txt",
  "compact_output_path": "supervised_loop\\0940-verify-compact.md",
  "full_output_path": "supervised_loop\\0940-verify-full.log",
  "classification": "VERIFY_RUNNING",
  "status": "READY",
  "next_recommended_action": "PASS_IF_EXIT_ZERO",
  "requires_alberto": false,
  "approval_reason": "",
  "created_at": "2026-06-10T00:00:00+02:00",
  "updated_at": "2026-06-10T00:00:00+02:00"
}
```

## Validation rules

- `working_directory` must be inside an allowed repository path.
- `script_path` must be relative to `working_directory` unless explicitly approved.
- `max_retry_absolute` must never exceed 10.
- `current_retry` must be less than or equal to `max_retry_absolute`.
- Any publish, merge, deploy or destructive action requires Alberto approval and must not run in Fast Lane by default.
- Output paths must stay under Bridge or another authorized local evidence root.
