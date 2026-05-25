from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "policies" / "safety_policy.v0.json"
PATH_POLICY_PATH = ROOT / "policies" / "path_policy.v0.json"


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def test_safety_policy_file_exists_and_is_json() -> None:
    assert POLICY_PATH.exists()
    policy = load_policy()
    assert policy["schema_version"] == "0.1"
    assert policy["step"] == "030"


def test_all_security_levels_are_defined() -> None:
    policy = load_policy()
    assert set(policy["levels"].keys()) == {"L0", "L1", "L2", "L3", "L4"}


def test_l4_is_never_automatic_and_requires_strong_controls() -> None:
    l4 = load_policy()["levels"]["L4"]
    assert l4["automatic_allowed"] is False
    assert l4["requires_explicit_approval"] is True
    assert l4["requires_dry_run"] is True
    assert l4["requires_backup_or_rollback"] is True
    assert l4["requires_double_confirmation"] is True


def test_l3_requires_approval_and_dry_run_but_not_double_confirmation() -> None:
    l3 = load_policy()["levels"]["L3"]
    assert l3["automatic_allowed"] is False
    assert l3["requires_explicit_approval"] is True
    assert l3["requires_dry_run"] is True
    assert l3["requires_backup_or_rollback"] is True
    assert l3["requires_double_confirmation"] is False


def test_l2_requires_branch_tests_and_rollback_note() -> None:
    l2 = load_policy()["levels"]["L2"]
    assert l2["requires_branch"] is True
    assert l2["requires_tests"] is True
    assert l2["requires_backup_or_rollback"] is True


def test_destructive_examples_are_classified_as_l4() -> None:
    l4_examples = set(load_policy()["levels"]["L4"]["examples"])
    expected = {
        "delete_file",
        "delete_data",
        "force_push",
        "merge_direct_to_main",
        "production_deploy",
        "rotate_credentials",
        "modify_real_database",
    }
    assert expected.issubset(l4_examples)


def test_codex_policy_forbids_commit_push_merge_and_force_push() -> None:
    codex = load_policy()["codex_policy"]
    assert codex["no_commit_without_explicit_request"] is True
    assert codex["no_push_without_explicit_request"] is True
    assert codex["no_merge"] is True
    assert codex["no_force_push"] is True
    assert codex["full_auto_allowed_only_in_sandbox"] is True


def test_mcp_policy_requires_approval_by_default() -> None:
    mcp = load_policy()["mcp_policy"]
    assert mcp["default_require_approval"] is True
    assert mcp["allowed_tools_must_be_explicit"] is True
    assert mcp["never_share_secrets_by_default"] is True


def test_secret_policy_blocks_real_secrets_by_default() -> None:
    secret = load_policy()["secret_policy"]
    assert secret["read_real_secrets_by_default"] is False
    assert secret["write_real_secrets_by_default"] is False
    assert secret["only_placeholders_in_examples"] is True
    assert secret["redact_tokens_in_logs"] is True


def test_path_policy_blocks_sensitive_patterns() -> None:
    path_policy = json.loads(PATH_POLICY_PATH.read_text(encoding="utf-8"))
    blocked = set(path_policy["blocked_patterns"])
    for pattern in [".git/**", "*.env", ".env", "*.pem", "*.key", "secrets/**", "credentials/**"]:
        assert pattern in blocked
    assert path_policy["outside_repository"] == "blocked"
