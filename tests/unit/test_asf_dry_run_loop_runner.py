from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_dry_run_loop_runner.py"
DOC = ROOT / "docs" / "motor" / "0580_DRY_RUN_LOOP_RUNNER.md"
INTEGRATION_DOC = ROOT / "docs" / "motor" / "0610_RISK_CLASSIFIER_DRY_RUN_INTEGRATION.md"
REQUEST_EXAMPLE = ROOT / "examples" / "dry_run_loop" / "step_0580_simulated_request.json"
PLAN_EXAMPLE = ROOT / "examples" / "dry_run_loop" / "step_0580_execution_plan.json"
INTEGRATION_EXAMPLES = [
    ROOT / "examples" / "dry_run_loop" / "step_0610_docs_only_request.json",
    ROOT / "examples" / "dry_run_loop" / "step_0610_code_change_request.json",
    ROOT / "examples" / "dry_run_loop" / "step_0610_publish_intent_request.json",
    ROOT / "examples" / "dry_run_loop" / "step_0610_l4_blocked_request.json",
]


FORBIDDEN_PATTERNS = [
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(read(path))


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_script(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False)


def git_available() -> bool:
    return shutil.which("git") is not None


def make_git_repo(tmp_path: Path, branch: str = "step-0580-dry-run-loop-runner") -> Path:
    if not git_available():
        pytest.skip("git executable not available")

    repo = tmp_path / "target_repo"
    repo.mkdir()
    init_result = run_git(repo, "init", "-b", "main")
    if init_result.returncode != 0:
        init_result = run_git(repo, "init")
    assert init_result.returncode == 0, init_result.stdout + init_result.stderr

    run_git(repo, "config", "user.email", "test@example.invalid")
    run_git(repo, "config", "user.name", "ASF Test")
    (repo / "README.md").write_text("# Temporary repo\n", encoding="utf-8")
    assert run_git(repo, "add", "README.md").returncode == 0
    commit_result = run_git(repo, "commit", "-m", "initial commit")
    assert commit_result.returncode == 0, commit_result.stdout + commit_result.stderr

    switch_result = run_git(repo, "switch", "-c", branch)
    if switch_result.returncode != 0:
        switch_result = run_git(repo, "checkout", "-b", branch)
    assert switch_result.returncode == 0, switch_result.stdout + switch_result.stderr
    return repo


def write_request(
    tmp_path: Path,
    repo: Path,
    branch: str = "step-0580-dry-run-loop-runner",
    **overrides: object,
) -> Path:
    request = {
        "allowed_scope": [
            "scripts/asf_dry_run_loop_runner.py",
            "docs/motor/0580_DRY_RUN_LOOP_RUNNER.md",
            "tests/unit/test_asf_dry_run_loop_runner.py",
        ],
        "branch": branch,
        "checks": [
            "python -m pytest",
            "python scripts/check_workflow_health.py",
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1",
        ],
        "forbidden_actions": [
            "live provider calls",
            "secret or API key usage",
            "target repository writes",
            "commit",
            "push",
            "PR",
            "merge",
            "deploy",
        ],
        "objective": "Demonstrate a local supervised dry-run loop.",
        "project_name": "Temp_Project",
        "repo_path": str(repo),
        "step": "0580",
        "title": "Dry-run Loop Runner",
    }
    request.update(overrides)
    path = tmp_path / "request.json"
    write_json(path, request)
    return path


def valid_plan() -> dict[str, object]:
    return {
        "external_provider_calls": False,
        "git_publication_actions": False,
        "mode": "dry-run",
        "plan_id": "provided-test-plan",
        "states": [
            {"actions": ["load_request"], "checkpoint": "request_loaded", "state": "PLAN_NEXT_STEP"},
            {"actions": ["generate_packet"], "checkpoint": "task_packet_generated", "state": "BUILD_TASK_PACKET"},
            {"actions": ["classify"], "checkpoint": "risk_report_generated", "state": "RISK_CLASSIFY"},
            {"actions": ["preview"], "checkpoint": "dry_run_preview_generated", "state": "EXECUTE_DRY_OR_WRITE"},
            {
                "actions": ["record_checks"],
                "checkpoint": "test_plan_report_generated",
                "checks": ["python -m pytest"],
                "state": "RUN_TESTS",
            },
            {"actions": ["review"], "checkpoint": "review_generated", "state": "INDEPENDENT_REVIEW"},
            {"actions": ["decide"], "checkpoint": "gate_decision_generated", "state": "GATE_DECISION"},
            {"actions": ["hold"], "checkpoint": "final_hold_report_generated", "state": "COMMIT_OR_HOLD"},
        ],
        "writes_target_repo": False,
    }


def test_dry_run_loop_runner_help_returns_success() -> None:
    result = run_script("--help")

    assert result.returncode == 0
    assert "--request-json" in result.stdout
    assert "--plan-json" in result.stdout
    assert "--fail-on-dirty" in result.stdout


def test_dry_run_loop_generates_full_artifacts_with_generated_plan(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    request = write_request(tmp_path, repo)
    output_dir = tmp_path / "out"

    result = run_script("--request-json", request, "--output-dir", output_dir)

    assert result.returncode == 0, result.stdout + result.stderr
    step_dir = output_dir / "Temp_Project" / "step_0580"
    expected = [
        "normalized_request.json",
        "execution_plan.json",
        "state_log.jsonl",
        "dry_run_task_packet.md",
        "risk_report.json",
        "risk_report.md",
        "execution_preview.md",
        "test_report.md",
        "independent_review.json",
        "gate_decision.json",
        "gate_decision.md",
        "final_report.md",
    ]
    for name in expected:
        assert (step_dir / name).exists(), name

    gate = read_json(step_dir / "gate_decision.json")
    review = read_json(step_dir / "independent_review.json")
    risk = read_json(step_dir / "risk_report.json")
    events = read(step_dir / "state_log.jsonl").strip().splitlines()

    assert gate["decision"] == "NEEDS_HUMAN"
    assert review["verdict"] == "PASS"
    assert risk["status"] == "PASS"
    assert risk["checkpoint"] == "RISK_CLASSIFY"
    assert risk["risk"]["risk_level"] == "L2"
    assert risk["risk"]["required_gate"] == "local_verification"
    assert risk["gate"]["declared_satisfied"] is False
    assert risk["dry_run"]["fail_closed"] is False
    assert len(events) == 8
    assert "Dry-run Loop Runner Final Report" in read(step_dir / "final_report.md")
    assert run_git(repo, "status", "--short").stdout.strip() == ""


def test_dry_run_loop_accepts_provided_plan(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    request = write_request(tmp_path, repo)
    plan_path = tmp_path / "plan.json"
    write_json(plan_path, valid_plan())

    result = run_script("--request-json", request, "--plan-json", plan_path, "--output-dir", tmp_path / "out")

    assert result.returncode == 0, result.stdout + result.stderr
    plan = read_json(tmp_path / "out" / "Temp_Project" / "step_0580" / "execution_plan.json")
    assert plan["plan_id"] == "provided-test-plan"


def test_dry_run_loop_fail_closes_on_live_provider_plan(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    request = write_request(tmp_path, repo)
    plan = valid_plan()
    plan["external_provider_calls"] = True
    plan_path = tmp_path / "bad_plan.json"
    write_json(plan_path, plan)

    result = run_script("--request-json", request, "--plan-json", plan_path, "--output-dir", tmp_path / "out")

    assert result.returncode == 3, result.stdout + result.stderr
    step_dir = tmp_path / "out" / "Temp_Project" / "step_0580"
    assert read_json(step_dir / "gate_decision.json")["decision"] == "FAIL"
    assert read_json(step_dir / "risk_report.json")["status"] == "FAIL"
    assert read_json(step_dir / "risk_report.json")["dry_run"]["fail_closed"] is True
    assert "external provider calls" in read(step_dir / "independent_review.json")


def test_dry_run_loop_dirty_target_requires_human_by_default(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    request = write_request(tmp_path, repo)
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    result = run_script("--request-json", request, "--output-dir", tmp_path / "out")

    assert result.returncode == 0, result.stdout + result.stderr
    review = read_json(tmp_path / "out" / "Temp_Project" / "step_0580" / "independent_review.json")
    assert review["verdict"] == "PASS"
    assert "dirty" in json.dumps(review).casefold()


def test_dry_run_loop_invokes_real_risk_classifier_for_docs_only_low_risk(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    request = write_request(
        tmp_path,
        repo,
        title="Documentation update",
        objective="Update docs only and inspect README.md.",
        allowed_scope=["README.md", "docs/motor/0610_RISK_CLASSIFIER_DRY_RUN_INTEGRATION.md"],
        checks=["git --no-pager diff --check"],
    )

    result = run_script("--request-json", request, "--output-dir", tmp_path / "out")

    assert result.returncode == 0, result.stdout + result.stderr
    risk = read_json(tmp_path / "out" / "Temp_Project" / "step_0580" / "risk_report.json")
    assert risk["risk"]["risk_level"] in {"L0", "L1"}
    assert risk["risk"]["fail_closed"] is False
    assert any(match["rule_id"].startswith("l0_") for match in risk["risk"]["matched_rules"])


def test_dry_run_loop_code_change_uses_l2_gate_policy(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    request = write_request(
        tmp_path,
        repo,
        objective="Implement local Python code and tests with standard-library-only local execution.",
        allowed_scope=["scripts/asf_dry_run_loop_runner.py", "tests/unit/test_asf_dry_run_loop_runner.py"],
        checks=["python -m pytest tests/unit/test_asf_dry_run_loop_runner.py"],
    )

    result = run_script("--request-json", request, "--output-dir", tmp_path / "out")

    assert result.returncode == 0, result.stdout + result.stderr
    risk = read_json(tmp_path / "out" / "Temp_Project" / "step_0580" / "risk_report.json")
    assert risk["risk"]["risk_level"] == "L2"
    assert risk["risk"]["required_gate"] == "local_verification"
    assert risk["gate"]["runner_executes_gate"] is False


def test_dry_run_loop_publish_intent_is_l3_without_publication(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    request = write_request(
        tmp_path,
        repo,
        objective="Prepare commit, push branch and open PR after human approval.",
        allowed_scope=["docs/motor/0610_RISK_CLASSIFIER_DRY_RUN_INTEGRATION.md"],
        checks=["git --no-pager diff --check"],
    )

    result = run_script("--request-json", request, "--output-dir", tmp_path / "out")

    assert result.returncode == 0, result.stdout + result.stderr
    step_dir = tmp_path / "out" / "Temp_Project" / "step_0580"
    risk = read_json(step_dir / "risk_report.json")
    gate = read_json(step_dir / "gate_decision.json")
    assert risk["status"] == "PASS"
    assert risk["risk"]["risk_level"] == "L3"
    assert risk["risk"]["required_gate"] == "explicit_publish_approval"
    assert risk["gate"]["declared_satisfied"] is False
    assert gate["decision"] == "NEEDS_HUMAN"
    assert run_git(repo, "status", "--short").stdout.strip() == ""


def test_dry_run_loop_plan_publish_signal_is_classified_l3(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    request = write_request(
        tmp_path,
        repo,
        title="Documentation update",
        objective="Update docs only and inspect README.md.",
        allowed_scope=["README.md"],
        checks=["git --no-pager diff --check"],
    )
    plan = valid_plan()
    for state in plan["states"]:  # type: ignore[index]
        if isinstance(state, dict) and state.get("state") == "RUN_TESTS":
            state["checks"] = ["git push"]
    plan_path = tmp_path / "plan.json"
    write_json(plan_path, plan)

    result = run_script("--request-json", request, "--plan-json", plan_path, "--output-dir", tmp_path / "out")

    assert result.returncode == 0, result.stdout + result.stderr
    risk = read_json(tmp_path / "out" / "Temp_Project" / "step_0580" / "risk_report.json")
    assert risk["risk"]["risk_level"] == "L3"
    assert risk["risk"]["required_gate"] == "explicit_publish_approval"
    assert risk["gate"]["runner_executes_gate"] is False
    assert run_git(repo, "status", "--short").stdout.strip() == ""


def test_dry_run_loop_l4_without_gate_fails_closed(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    request = write_request(
        tmp_path,
        repo,
        objective="Deploy to production, merge the PR and delete generated data.",
        allowed_scope=["docs/motor/0610_RISK_CLASSIFIER_DRY_RUN_INTEGRATION.md"],
        checks=["git --no-pager diff --check"],
    )

    result = run_script("--request-json", request, "--output-dir", tmp_path / "out")

    assert result.returncode == 3, result.stdout + result.stderr
    step_dir = tmp_path / "out" / "Temp_Project" / "step_0580"
    risk = read_json(step_dir / "risk_report.json")
    assert risk["status"] == "FAIL"
    assert risk["risk"]["risk_level"] == "L4"
    assert risk["dry_run"]["fail_closed"] is True
    assert read_json(step_dir / "gate_decision.json")["decision"] == "FAIL"
    assert run_git(repo, "status", "--short").stdout.strip() == ""


def test_dry_run_loop_ambiguous_request_fails_closed(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    request = write_request(
        tmp_path,
        repo,
        title="Ambiguous step",
        objective="Handle the thing.",
        allowed_scope=[],
        checks=[],
    )

    result = run_script("--request-json", request, "--output-dir", tmp_path / "out")

    assert result.returncode == 3, result.stdout + result.stderr
    risk = read_json(tmp_path / "out" / "Temp_Project" / "step_0580" / "risk_report.json")
    assert risk["status"] == "FAIL"
    assert risk["risk"]["fail_closed"] is True
    assert risk["risk"]["risk_level"] == "L4"


def test_dry_run_loop_files_docs_and_examples_exist() -> None:
    assert SCRIPT.exists()
    assert DOC.exists()
    assert INTEGRATION_DOC.exists()
    assert REQUEST_EXAMPLE.exists()
    assert PLAN_EXAMPLE.exists()
    for path in INTEGRATION_EXAMPLES:
        assert path.exists()

    doc = read(DOC)
    for fragment in [
        "PLAN_NEXT_STEP",
        "BUILD_TASK_PACKET",
        "RISK_CLASSIFY",
        "NEEDS_HUMAN",
        "asf_risk_classifier.py",
        "tmp/asf_dry_run_loop",
    ]:
        assert fragment in doc


def test_dry_run_loop_script_avoids_operational_forbidden_patterns() -> None:
    content = read(SCRIPT)

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in content

    assert "shell=True" not in content
    assert "from asf_risk_classifier import ClassifierInput, classify" in content
    assert "def classify_risk" not in content
    assert "RiskRule(" not in content
