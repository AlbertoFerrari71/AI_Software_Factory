from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_workflow_health.py"
DOC = ROOT / "docs" / "35_WORKFLOW_HEALTH_CHECK.md"
INDEX = ROOT / "docs" / "34_PROJECT_WORKFLOW_INDEX.md"
CLOSURE_PACK = ROOT / "docs" / "motor" / "0730_END_TO_END_MVP_CLOSURE_PACK.md"
PILOT_NOTES = ROOT / "docs" / "motor" / "0740_MVP_REAL_STEP_PILOT.md"
HOOK_DOC = ROOT / "docs" / "motor" / "0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md"
HOOK_PILOT_DOC = ROOT / "docs" / "motor" / "0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md"
RUNNER_HOOK_MANIFEST_DOC = ROOT / "docs" / "motor" / "0770_RUNNER_HOOK_EVIDENCE_MANIFEST_INTEGRATION.md"
MANIFEST_HOOKS_PILOT_DOC = ROOT / "docs" / "motor" / "0780_MVP_REAL_STEP_PILOT_3_WITH_MANIFEST_HOOKS.md"
POST_MVP_ROADMAP_DOC = ROOT / "docs" / "motor" / "0790_POST_MVP_ROADMAP_AND_HARDENING_PLAN.md"
PWSH_NATIVE_GUARDRAILS_DOC = (
    ROOT / "docs" / "motor" / "0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md"
)
PWSH_PUBLISH_SKILL_SYNC_DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0805_POWERSHELL_PUBLISH_SKILL_SYNC_WITH_PROVEN_RUNNER_FLOW.md"
)
PUBLISH_SCOPE_DISCOVERY_DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0810_PUBLISH_RUNNER_SCOPE_DISCOVERY_RECOVERY_UX_AND_NO_FALSE_COMPLETED_GUARD.md"
)
BRIDGE_OUTPUT_RETRY_DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0820_BRIDGE_OUTPUT_RETRY_FALLBACK_AND_LAST_VALIDATION.md"
)
CODEX_SKILLS_WRITE_DOC = (
    ROOT / "docs" / "motor" / "0870_CODEX_SKILLS_FIRST_CONTROLLED_WRITE_PILOT.md"
)
CODEX_SKILLS_WRITE_RESULT = (
    ROOT / "docs" / "motor" / "0870_CODEX_SKILLS_CONTROLLED_WRITE_RESULT.md"
)
CODEX_SKILLS_WRITE_ROLLBACK = (
    ROOT / "docs" / "motor" / "0870_CODEX_SKILLS_ROLLBACK_PLAN.md"
)
CODEX_SKILLS_REVIEW_DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0880_CODEX_SKILLS_CONTROLLED_WRITE_REVIEW_AND_DECISION.md"
)
CODEX_SKILLS_REVIEW_STATE = (
    ROOT / "docs" / "motor" / "0880_CODEX_SKILLS_EXTERNAL_REPO_STATE_REPORT.md"
)
CODEX_SKILLS_REVIEW_MATRIX = (
    ROOT / "docs" / "motor" / "0880_CODEX_SKILLS_DECISION_MATRIX.md"
)
CODEX_SKILLS_REVIEW_COMMANDS = (
    ROOT / "docs" / "motor" / "0880_CODEX_SKILLS_PREPARED_COMMANDS_NOT_EXECUTED.md"
)
CODEX_SKILLS_LOCAL_COMMIT_DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0890_CODEX_SKILLS_CONTROLLED_LOCAL_COMMIT_EXECUTION.md"
)
CODEX_SKILLS_LOCAL_COMMIT_RESULT = (
    ROOT
    / "docs"
    / "motor"
    / "0890_CODEX_SKILLS_CONTROLLED_LOCAL_COMMIT_RESULT.md"
)
CODEX_SKILLS_PUSH_ROLLBACK_DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0900_CODEX_SKILLS_CONTROLLED_PUSH_OR_ROLLBACK_DECISION.md"
)
CODEX_SKILLS_PUSH_ROLLBACK_STATE = (
    ROOT / "docs" / "motor" / "0900_CODEX_SKILLS_PUSH_ROLLBACK_STATE_REPORT.md"
)
CODEX_SKILLS_PUSH_ROLLBACK_MATRIX = (
    ROOT / "docs" / "motor" / "0900_CODEX_SKILLS_PUSH_ROLLBACK_DECISION_MATRIX.md"
)
CODEX_SKILLS_PUSH_ROLLBACK_COMMANDS = (
    ROOT / "docs" / "motor" / "0900_CODEX_SKILLS_PREPARED_COMMANDS_NOT_EXECUTED.md"
)
CODEX_SKILLS_REMOTE_VERIFICATION_CLOSURE = (
    ROOT
    / "docs"
    / "motor"
    / "0920_CODEX_SKILLS_REMOTE_VERIFICATION_AND_EVIDENCE_CLOSURE.md"
)
CODEX_SKILLS_REMOTE_PUSH_EVIDENCE = (
    ROOT / "docs" / "motor" / "0920_CODEX_SKILLS_REMOTE_PUSH_EVIDENCE_REPORT.md"
)
PUBLISH_RUNNER_COMPAT_FIX_DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0921_PUBLISH_RUNNER_POWERSHELL_COMPATIBILITY_REGRESSION_FIX.md"
)
PUBLISH_RUNNER_GH_CHECKS_FALLBACK_DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0922_PUBLISH_RUNNER_GH_CHECKS_NO_CHECKS_REPORTED_FALLBACK.md"
)
PUBLISH_RUNNER_LF_CRLF_WARNING_DOC = (
    ROOT
    / "docs"
    / "motor"
    / "0923_PUBLISH_RUNNER_LF_CRLF_WARNING_STDERR_HANDLING.md"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_workflow_health_check_files_exist() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert CLOSURE_PACK.exists()
    assert PILOT_NOTES.exists()
    assert HOOK_DOC.exists()
    assert HOOK_PILOT_DOC.exists()
    assert RUNNER_HOOK_MANIFEST_DOC.exists()
    assert MANIFEST_HOOKS_PILOT_DOC.exists()
    assert POST_MVP_ROADMAP_DOC.exists()
    assert PWSH_NATIVE_GUARDRAILS_DOC.exists()
    assert PWSH_PUBLISH_SKILL_SYNC_DOC.exists()
    assert PUBLISH_SCOPE_DISCOVERY_DOC.exists()
    assert BRIDGE_OUTPUT_RETRY_DOC.exists()
    assert CODEX_SKILLS_WRITE_DOC.exists()
    assert CODEX_SKILLS_WRITE_RESULT.exists()
    assert CODEX_SKILLS_WRITE_ROLLBACK.exists()
    assert CODEX_SKILLS_REVIEW_DOC.exists()
    assert CODEX_SKILLS_REVIEW_STATE.exists()
    assert CODEX_SKILLS_REVIEW_MATRIX.exists()
    assert CODEX_SKILLS_REVIEW_COMMANDS.exists()
    assert CODEX_SKILLS_REMOTE_VERIFICATION_CLOSURE.exists()
    assert CODEX_SKILLS_REMOTE_PUSH_EVIDENCE.exists()
    assert PUBLISH_RUNNER_COMPAT_FIX_DOC.exists()
    assert PUBLISH_RUNNER_GH_CHECKS_FALLBACK_DOC.exists()
    assert PUBLISH_RUNNER_LF_CRLF_WARNING_DOC.exists()


def test_workflow_health_check_script_runs_successfully() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Workflow Health Check PASSED" in result.stdout


def test_workflow_health_check_script_avoids_forbidden_patterns() -> None:
    content = read(SCRIPT)

    forbidden_patterns = [
        "git commit",
        "git push",
        "gh pr create",
        "gh pr merge",
        "gh release",
        "git merge",
        "git reset --hard",
        "git clean",
        "Set-ExecutionPolicy",
        "setx PATH",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in content


def test_workflow_health_check_doc_contains_required_context() -> None:
    content = read(DOC)

    required_fragments = [
        "Verification Gate",
        "Documentation Sync",
        "Release Smoke Workflow",
        "Project Workflow Index",
        "read-only",
        "local-first",
        "CI",
    ]
    for fragment in required_fragments:
        assert fragment in content


def test_project_workflow_index_mentions_health_check() -> None:
    content = read(INDEX)

    assert "docs/35_WORKFLOW_HEALTH_CHECK.md" in content
    assert "scripts/check_workflow_health.py" in content


def test_workflow_health_tracks_mvp_closure_pack() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    closure_pack = read(CLOSURE_PACK)

    indexed_fragments = [
        "docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md",
        "MVP STATUS: GO WITH WARNINGS",
        "GO/WARNING/NO-GO",
        "0740) MVP Real Step Pilot",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    closure_fragments = [
        "MVP STATUS: GO WITH WARNINGS",
        "GO/WARNING/NO-GO",
        "0740) MVP Real Step Pilot",
    ]

    for fragment in closure_fragments:
        assert fragment in closure_pack


def test_workflow_health_tracks_mvp_real_step_pilot() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    pilot_notes = read(PILOT_NOTES)

    indexed_fragments = [
        "docs/motor/0740_MVP_REAL_STEP_PILOT.md",
        "PILOT STATUS: GO WITH WARNINGS",
        "tmp/0740_mvp_real_step_pilot",
        "0750) State Machine Publish Runner Event Hooks",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    pilot_fragments = [
        "PILOT STATUS: GO WITH WARNINGS",
        "tmp/0740_mvp_real_step_pilot",
        "0750) State Machine Publish Runner Event Hooks",
    ]

    for fragment in pilot_fragments:
        assert fragment in pilot_notes


def test_workflow_health_tracks_state_machine_publish_runner_event_hooks() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    hook_doc = read(HOOK_DOC)

    indexed_fragments = [
        "docs/motor/0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md",
        "state_machine_enabled",
        "phase_b_started",
        "phase_c_started",
        "main_verified",
        "examples/publish_step/0750_publish_config_state_hooks.example.json",
        "-ApprovePublish",
        "-ApproveMerge",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    hook_fragments = [
        "state_machine_enabled",
        "phase_b_started",
        "phase_b_failed",
        "phase_c_started",
        "phase_c_failed",
        "main_verified",
        "state_close_on_phase_c_success",
        "0760) MVP Real Step Pilot 2 with State Hooks",
    ]

    for fragment in hook_fragments:
        assert fragment in hook_doc


def test_workflow_health_tracks_mvp_real_step_pilot_2_with_state_hooks() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    pilot_doc = read(HOOK_PILOT_DOC)

    indexed_fragments = [
        "docs/motor/0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md",
        "PILOT STATUS: GO WITH WARNINGS",
        "tmp/0760_mvp_real_step_pilot_2_state_hooks",
        "READY_TO_PUBLISH",
        "Phase Plan",
        "LAST-State.json",
        "0770) Runner Hook Evidence Manifest Integration",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    pilot_fragments = [
        "state_machine_enabled",
        "state_expected_before_phase_b",
        "state_expected_before_phase_c",
        "phase_b_started",
        "phase_b_passed",
        "pr_created",
        "phase_c_started",
        "phase_c_passed",
        "main_verified",
        "READY_TO_PUBLISH",
        "PILOT STATUS: GO WITH WARNINGS",
    ]

    for fragment in pilot_fragments:
        assert fragment in pilot_doc


def test_workflow_health_tracks_post_mvp_roadmap_and_hardening_plan() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    post_mvp_doc = read(POST_MVP_ROADMAP_DOC)

    indexed_fragments = [
        "docs/motor/0790_POST_MVP_ROADMAP_AND_HARDENING_PLAN.md",
        "POST-MVP DECISION: HARDENING FIRST",
        "PowerShell Native Command Guardrail Hardening",
        "Bridge Output Retry, Fallback and LAST Validation",
        "0800) PowerShell Native Command Guardrail Hardening",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    post_mvp_fragments = [
        "MVP STATUS: GO WITH WARNINGS",
        "non e' ancora \"fire-and-forget\"",
        "Phase B contiene la verifica equivalente alla Phase A",
        "$LASTEXITCODE",
        "gli argomenti vuoti nei wrapper PowerShell sono pericolosi",
        "recovery delicati devono essere racchiusi in blocchi `& { ... }`",
        "merge senza `-ApproveMerge`",
        "publish senza `-ApprovePublish`",
        "First Real External Workflow Pilot",
        "NEXT STEP: 0800) PowerShell Native Command Guardrail Hardening",
    ]

    for fragment in post_mvp_fragments:
        assert fragment in post_mvp_doc


def test_workflow_health_tracks_powershell_native_command_guardrail_hardening() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    native_doc = read(PWSH_NATIVE_GUARDRAILS_DOC)

    indexed_fragments = [
        "docs/motor/0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md",
        "Invoke-NativeChecked",
        "Assert-NoOutOfScopeFiles",
        "PrNumber",
        "AllowedExitCodes",
        "0810) Publish Runner Recovery UX and No-False-Completed Guard",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    native_fragments = [
        "Invoke-NativeChecked",
        "$LASTEXITCODE",
        "PrNumber",
        "expected_files",
        "Assert-NoOutOfScopeFiles",
        "gh pr checks --watch",
        "COMPLETATO",
        "0810) Publish Runner Recovery UX and No-False-Completed Guard",
    ]

    for fragment in native_fragments:
        assert fragment in native_doc


def test_workflow_health_tracks_codex_skills_first_controlled_write_pilot() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    write_doc = read(CODEX_SKILLS_WRITE_DOC)
    result = read(CODEX_SKILLS_WRITE_RESULT)
    rollback = read(CODEX_SKILLS_WRITE_ROLLBACK)

    indexed_fragments = [
        "docs/motor/0870_CODEX_SKILLS_FIRST_CONTROLLED_WRITE_PILOT.md",
        "docs/motor/0870_CODEX_SKILLS_CONTROLLED_WRITE_RESULT.md",
        "docs/motor/0870_CODEX_SKILLS_ROLLBACK_PLAN.md",
        "examples/publish_runner/0870_codex_skills_controlled_write_evidence.example.json",
        "local-only controlled write",
        "rollback plan",
        "human gate",
        "external_repo_write_performed",
        "external_repo_commit_performed=false",
        "0880) Codex_Skills Controlled Write Review and Rollback/Commit Decision",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    for fragment in [
        "GO_FOR_LOCAL_CONTROLLED_WRITE",
        "nessun commit/push/PR/merge",
        "rollback plan",
        "human gate",
        "0880) Codex_Skills Controlled Write Review and Rollback/Commit Decision",
    ]:
        assert fragment in write_doc

    for fragment in [
        "Write eseguito: `si`",
        "Write bloccato: `no`",
        "nessun commit/push/PR/merge",
    ]:
        assert fragment in result

    for fragment in [
        "Remove-Item -Path",
        "solo dopo review umana",
        "Non usare comandi di cleanup ampio",
    ]:
        assert fragment in rollback


def test_workflow_health_tracks_codex_skills_controlled_write_review_decision() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    review_doc = read(CODEX_SKILLS_REVIEW_DOC)
    state = read(CODEX_SKILLS_REVIEW_STATE)
    matrix = read(CODEX_SKILLS_REVIEW_MATRIX)
    commands = read(CODEX_SKILLS_REVIEW_COMMANDS)

    indexed_fragments = [
        "docs/motor/0880_CODEX_SKILLS_CONTROLLED_WRITE_REVIEW_AND_DECISION.md",
        "docs/motor/0880_CODEX_SKILLS_EXTERNAL_REPO_STATE_REPORT.md",
        "docs/motor/0880_CODEX_SKILLS_DECISION_MATRIX.md",
        "docs/motor/0880_CODEX_SKILLS_PREPARED_COMMANDS_NOT_EXECUTED.md",
        "examples/publish_runner/0880_codex_skills_controlled_write_review_decision.example.json",
        "decision_pack_created",
        "default_recommendation",
        "prepared_commands_executed=false",
        "0890) Codex_Skills Rollback or Controlled Commit Execution",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    for fragment in [
        "A) rollback",
        "B) keep local",
        "C) future controlled commit",
        "Raccomandazione default: A) rollback",
        "0890) Codex_Skills Rollback or Controlled Commit Execution",
    ]:
        assert fragment in review_doc

    for fragment in [
        "?? docs/asf_external_pilot/",
        "File letto: si",
        "Modifiche inattese: no",
    ]:
        assert fragment in state

    assert "Default: A) rollback" in matrix
    assert "NON ESEGUITO" in commands
    assert "DA USARE SOLO DOPO APPROVAZIONE ESPLICITA" in commands


def test_workflow_health_tracks_codex_skills_controlled_local_commit_execution() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    execution_doc = read(CODEX_SKILLS_LOCAL_COMMIT_DOC)
    result = read(CODEX_SKILLS_LOCAL_COMMIT_RESULT)

    indexed_fragments = [
        "docs/motor/0890_CODEX_SKILLS_CONTROLLED_LOCAL_COMMIT_EXECUTION.md",
        "docs/motor/0890_CODEX_SKILLS_CONTROLLED_LOCAL_COMMIT_RESULT.md",
        "examples/publish_runner/0890_codex_skills_controlled_local_commit_evidence.example.json",
        "local_commit_completed",
        "external_repo_commit_performed=true",
        "external_repo_push_performed=false",
        "human gate per push futuro",
        "0900) Codex_Skills Controlled Push or Rollback Decision",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    for fragment in [
        "B) Commit locale controllato su Codex_Skills, senza push",
        "nessun push",
        "nessuna PR",
        "Qualunque push futuro richiede un human gate separato",
    ]:
        assert fragment in execution_doc

    for fragment in [
        "Commit eseguito",
        "Push eseguito: no",
        "PR eseguita: no",
        "Merge eseguito: no",
        "Deploy eseguito: no",
    ]:
        assert fragment in result


def test_workflow_health_tracks_codex_skills_push_or_rollback_decision() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    decision_doc = read(CODEX_SKILLS_PUSH_ROLLBACK_DOC)
    state = read(CODEX_SKILLS_PUSH_ROLLBACK_STATE)
    matrix = read(CODEX_SKILLS_PUSH_ROLLBACK_MATRIX)
    commands = read(CODEX_SKILLS_PUSH_ROLLBACK_COMMANDS)

    indexed_fragments = [
        "docs/motor/0900_CODEX_SKILLS_CONTROLLED_PUSH_OR_ROLLBACK_DECISION.md",
        "docs/motor/0900_CODEX_SKILLS_PUSH_ROLLBACK_STATE_REPORT.md",
        "docs/motor/0900_CODEX_SKILLS_PUSH_ROLLBACK_DECISION_MATRIX.md",
        "docs/motor/0900_CODEX_SKILLS_PREPARED_COMMANDS_NOT_EXECUTED.md",
        "examples/publish_runner/0900_codex_skills_push_or_rollback_decision.example.json",
        "push_performed_in_0900=false",
        "rollback_performed_in_0900=false",
        "prepared_commands_executed=false",
        "0910) Codex_Skills Controlled Push Execution or Local Rollback",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    for fragment in [
        "A) Push controllato",
        "B) Rollback locale",
        "C) Keep local temporaneo",
        "Lo STEP 0900 non esegue nessuna delle tre opzioni",
    ]:
        assert fragment in decision_doc

    for fragment in [
        "## main...origin/main [ahead 1]",
        "b488745 0870 add ASF controlled write pilot note",
        "non verificato live per vincolo no-fetch",
    ]:
        assert fragment in state

    assert "Nessuna opzione viene eseguita nello STEP 0900" in matrix
    assert "NON ESEGUITI" in commands


def test_workflow_health_tracks_codex_skills_remote_verification_closure() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    closure = read(CODEX_SKILLS_REMOTE_VERIFICATION_CLOSURE)
    evidence = read(CODEX_SKILLS_REMOTE_PUSH_EVIDENCE)

    indexed_fragments = [
        "docs/motor/0920_CODEX_SKILLS_REMOTE_VERIFICATION_AND_EVIDENCE_CLOSURE.md",
        "docs/motor/0920_CODEX_SKILLS_REMOTE_PUSH_EVIDENCE_REPORT.md",
        "examples/publish_runner/0920_codex_skills_remote_verification_evidence.example.json",
        "push_completed=true",
        "push_exit_code=0",
        "36b065d..bec96ff main -> main",
        "$env:USERPROFILE",
        "no-fetch/no-pull",
        "0930) External Repo Push Pattern Generalization",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    for fragment in [
        "0910A-3",
        "Codex_Skills",
        "b488745",
        "bec96ff",
        "## main...origin/main",
        "remote verification is based on local tracking state",
    ]:
        assert fragment in closure
        assert fragment in evidence

    for fragment in ["PR", "merge", "deploy", "tag"]:
        assert fragment in closure
        assert fragment in evidence


def test_workflow_health_tracks_publish_runner_compat_regression_fix() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    fix_doc = read(PUBLISH_RUNNER_COMPAT_FIX_DOC)

    indexed_fragments = [
        "docs/motor/0921_PUBLISH_RUNNER_POWERSHELL_COMPATIBILITY_REGRESSION_FIX.md",
        "scripts/asf_minimal_docx.py",
        "examples/publish_runner/0921_publish_runner_regression_fix_evidence.example.json",
        "safe PSNativeCommandUseErrorActionPreference handling",
        "valid DOCX bridge output",
        "PrepareConfig command argument normalization",
        "state hook event preservation",
        "0920 publish retry after 0921 fix",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    for fragment in [
        "PSNativeCommandUseErrorActionPreference",
        "ProcessStartInfo.ArgumentList",
        "scripts/asf_minimal_docx.py",
        "DOCX zip valido",
        "Out-of-scope changes detected",
    ]:
        assert fragment in fix_doc


def test_workflow_health_tracks_publish_runner_gh_checks_fallback() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    fallback_doc = read(PUBLISH_RUNNER_GH_CHECKS_FALLBACK_DOC)

    indexed_fragments = [
        "docs/motor/0922_PUBLISH_RUNNER_GH_CHECKS_NO_CHECKS_REPORTED_FALLBACK.md",
        "tests/unit/test_asf_publish_step_gh_checks_fallback.py",
        "gh run list --commit",
        "completed/success",
        "no checks reported",
        "0930) External Repo Push Pattern Generalization",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    for fragment in [
        "gh pr view <PR> --json headRefOid --jq .headRefOid",
        "gh run list --commit <headSha>",
        "status = completed",
        "conclusion = success",
        "headSha = <headSha PR>",
        "Check falliti",
        "non viene marcata PASS",
    ]:
        assert fragment in fallback_doc


def test_workflow_health_tracks_publish_runner_lf_crlf_warning_handling() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    warning_doc = read(PUBLISH_RUNNER_LF_CRLF_WARNING_DOC)

    indexed_fragments = [
        "docs/motor/0923_PUBLISH_RUNNER_LF_CRLF_WARNING_STDERR_HANDLING.md",
        "tests/unit/test_asf_publish_step_lf_crlf_warning_handling.py",
        "stderr warning treated as non-blocking",
        "LF will be replaced by CRLF",
        "CRLF will be replaced by LF",
        "Git command wrote unexpected stderr",
        "0930) External Repo Push Pattern Generalization",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    for fragment in [
        "exit code `0`",
        "stderr non whitelisted",
        "whitespace error",
        "Non viene normalizzato alcun line ending",
        "warning visibile",
    ]:
        assert fragment in warning_doc


def test_workflow_health_tracks_powershell_publish_skill_sync() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    sync_doc = read(PWSH_PUBLISH_SKILL_SYNC_DOC)

    indexed_fragments = [
        "docs/motor/0805_POWERSHELL_PUBLISH_SKILL_SYNC_WITH_PROVEN_RUNNER_FLOW.md",
        "config JSON esplicito",
        "scripts/asf_publish_step.ps1",
        "gh pr list --head",
        "-ApprovePublish",
        "-ApproveMerge",
        "Set-Clipboard -Path",
        "0810) Publish Runner Recovery UX and No-False-Completed Guard",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    sync_fragments = [
        "STEP 0790",
        "STEP 0800",
        "Phase B -> recupero PR -> Phase C",
        "expected_files",
        "changed_files",
        "PR number is not numeric",
        "DOCX e' best-effort",
        "COMPLETATO",
        "0810) Publish Runner Recovery UX and No-False-Completed Guard",
    ]

    for fragment in sync_fragments:
        assert fragment in sync_doc


def test_workflow_health_tracks_publish_runner_scope_discovery_recovery_ux() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    scope_doc = read(PUBLISH_SCOPE_DISCOVERY_DOC)

    indexed_fragments = [
        "docs/motor/0810_PUBLISH_RUNNER_SCOPE_DISCOVERY_RECOVERY_UX_AND_NO_FALSE_COMPLETED_GUARD.md",
        "PrepareConfig",
        "Get-RepositoryChangedFiles",
        "Recovery_Out_Of_Scope",
        "COMPLETATO CON WARNING NON BLOCCANTE",
        "DOCX",
        "best-effort",
        "0820) Bridge Output Retry, Fallback and LAST Validation",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    scope_fragments = [
        "0800",
        "0805",
        "expected_files",
        "changed_files",
        "fail-closed",
        "git --no-pager diff --name-only",
        "git --no-pager diff --cached --name-only",
        "git ls-files --others --exclude-standard",
        "warning LF/CRLF",
        "DOCX",
        "best-effort",
        "COMPLETATO CON WARNING NON BLOCCANTE",
    ]

    for fragment in scope_fragments:
        assert fragment in scope_doc


def test_workflow_health_tracks_bridge_output_retry_fallback_last_validation() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    bridge_doc = read(BRIDGE_OUTPUT_RETRY_DOC)

    indexed_fragments = [
        "docs/motor/0820_BRIDGE_OUTPUT_RETRY_FALLBACK_AND_LAST_VALIDATION.md",
        "Set-ContentWithRetry",
        "Write-BridgeFileWithRetry",
        "Update-LastFileWithRetry",
        "Validate-BridgeLastOutputs",
        "fallback",
        "single writer ownership",
        "0830) MVP Real Step Pilot 4 - Slightly More Operational",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    bridge_fragments = [
        "0800",
        "0805",
        "0810",
        "The process cannot access the file because it is being used by another process",
        "BLOCCATO",
        "retry",
        "fallback",
        "Compact Markdown is mandatory",
        "DOCX remains best-effort",
        "LAST-Output_Compatto.md",
        "single writer ownership",
        "Start-Transcript",
        "NNNN-Wrapper_Log_*.txt",
        "Set-Clipboard -Path",
    ]

    for fragment in bridge_fragments:
        assert fragment in bridge_doc


def test_workflow_health_tracks_runner_hook_evidence_manifest_integration() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    manifest_doc = read(RUNNER_HOOK_MANIFEST_DOC)

    indexed_fragments = [
        "docs/motor/0770_RUNNER_HOOK_EVIDENCE_MANIFEST_INTEGRATION.md",
        "runner_hooks",
        "--include-runner-hooks",
        "--expected-events",
        "sample_manifest_input_runner_hooks_closed.json",
        "sample_closed_with_runner_hooks_state.json",
        "0780) MVP Real Step Pilot 3 with Manifest Hooks",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    manifest_fragments = [
        "runner_hooks",
        "--state-file",
        "--state-bridge-root",
        "--publish-runner-output",
        "--publish-config",
        "--require-closed-state",
        "--expected-step",
        "--expected-final-state",
        "--expected-events",
        "CLOSED",
        "INCOMPLETE",
        "FAIL_CLOSED",
        "no Phase B",
        "no Phase C",
    ]

    for fragment in manifest_fragments:
        assert fragment in manifest_doc


def test_workflow_health_tracks_mvp_real_step_pilot_3_with_manifest_hooks() -> None:
    script = read(SCRIPT)
    doc = read(DOC)
    index = read(INDEX)
    pilot_doc = read(MANIFEST_HOOKS_PILOT_DOC)

    indexed_fragments = [
        "docs/motor/0780_MVP_REAL_STEP_PILOT_3_WITH_MANIFEST_HOOKS.md",
        "PILOT STATUS: GO WITH WARNINGS",
        "tmp/0780_mvp_real_step_pilot_3_manifest_hooks",
        "READY_TO_PUBLISH",
        "Phase Plan",
        "--include-runner-hooks",
        "--expected-final-state",
        "0790) Post-MVP Roadmap and Hardening Plan",
    ]

    for fragment in indexed_fragments:
        assert fragment in script
        assert fragment in doc
        assert fragment in index

    pilot_fragments = [
        "state_machine_enabled",
        "state_expected_before_phase_b",
        "state_expected_before_phase_c",
        "phase_b_started",
        "phase_b_passed",
        "pr_created",
        "phase_c_started",
        "phase_c_passed",
        "main_verified",
        "close_step",
        "--include-runner-hooks",
        "--state-file",
        "--expected-step",
        "--expected-final-state CLOSED",
        "--expected-events",
        "LAST-State.json",
        "LAST-Run_Manifest.json",
        "PILOT STATUS: GO WITH WARNINGS",
    ]

    for fragment in pilot_fragments:
        assert fragment in pilot_doc
