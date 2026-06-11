from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_powershell_recovery_classifier.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_powershell_recovery_classifier", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def classify(**kwargs: object) -> dict[str, object]:
    module = load_module()
    data = module.RecoveryInput(**kwargs)
    return module.classify_recovery(data)


def test_classifies_prompt_continuation_and_parse_error() -> None:
    continuation = classify(stderr="PowerShell prompt >> incomplete command", exit_code=None)
    parse = classify(stderr="ParserError: unexpected token finally", exit_code=1)

    assert continuation["classification"] == "POWERSHELL_PROMPT_CONTINUATION"
    assert continuation["retry_allowed"] is True
    assert parse["classification"] == "POWERSHELL_PARSE_ERROR"


def test_classifies_git_pager_file_lock_and_gh_no_checks() -> None:
    pager = classify(stdout="commit list\n(END)", exit_code=None)
    locked = classify(stderr="The process cannot access the file because it is being used by another process", exit_code=1)
    checks = classify(stderr="no checks reported on the 'main' branch", exit_code=1)

    assert pager["classification"] == "GIT_PAGER_BLOCK"
    assert locked["classification"] == "FILE_LOCKED"
    assert checks["classification"] == "GH_NO_CHECKS_REPORTED"
    assert checks["requires_alberto"] is False


def test_classifies_git_warning_credential_and_destructive_command() -> None:
    line_warning = classify(stderr="warning: LF will be replaced by CRLF", exit_code=0)
    credential = classify(stderr="fatal: could not read Username for remote", exit_code=128)
    destructive = classify(command_text="git " + "reset --hard", exit_code=None)

    assert line_warning["classification"] == "LF_CRLF_SAFE_WARNING"
    assert line_warning["retry_allowed"] is False
    assert credential["classification"] == "CREDENTIAL_PROMPT"
    assert credential["requires_alberto"] is True
    assert destructive["classification"] == "POTENTIALLY_DESTRUCTIVE_COMMAND"
    assert destructive["safe_to_retry"] is False


def test_classifies_pytest_verify_workflow_health_and_timeouts() -> None:
    pytest_failure = classify(stdout="pytest short test summary\nFAILED tests/unit/test_x.py", exit_code=1)
    verify_failure = classify(stderr="verify.ps1 failed", exit_code=1)
    health_failure = classify(stdout="Workflow Health Check FAILED", exit_code=1)
    timeout = classify(timed_out=True, exit_code=None)
    idle_timeout = classify(idle_timed_out=True, exit_code=None)

    assert pytest_failure["classification"] == "TEST_FAILURE"
    assert verify_failure["classification"] == "VERIFY_FAILURE"
    assert health_failure["classification"] == "WORKFLOW_HEALTH_FAILURE"
    assert timeout["classification"] == "TIMEOUT"
    assert idle_timeout["classification"] == "IDLE_TIMEOUT"


def test_unknown_failure_stops_and_retry_policy_ceiling_is_not_default() -> None:
    packet = classify(stderr="unrecognized failure", exit_code=1)
    exhausted = classify(stderr="ParserError", exit_code=1, retry_count=10)

    assert packet["classification"] == "UNKNOWN_FAILURE"
    assert packet["requires_alberto"] is True
    assert packet["retry_policy"]["max_retry_absolute"] == 10
    assert packet["retry_policy"]["ceiling_is_default"] is False
    assert exhausted["retry_allowed"] is False
    assert exhausted["stop_reason"] == "STOP_MAX_RETRY_REACHED"


def test_cli_json_output_is_valid() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--stderr",
            "warning: CRLF will be replaced by LF",
            "--exit-code",
            "0",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["classification"] == "LF_CRLF_SAFE_WARNING"
