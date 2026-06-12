from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "asf_risk_classifier_eval.py"
DATASET = ROOT / "examples" / "eval" / "risk_classifier" / "golden.jsonl"


def load_module():
    spec = importlib.util.spec_from_file_location("asf_risk_classifier_eval", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    scripts_path = str(ROOT / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_golden_dataset_has_at_least_30_records() -> None:
    module = load_module()
    records = module.load_records(DATASET)

    assert len(records) >= 30


def test_golden_eval_zero_downgrade_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--dataset", str(DATASET)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "status: PASS" in result.stdout


def test_eval_detects_safety_downgrade() -> None:
    module = load_module()
    records = [
        {
            "id": "forced-downgrade",
            "input_text": "Update README documentation only.",
            "expected_risk_level": "L3",
            "expected_required_gate": "explicit_publish_approval",
        }
    ]

    payload = module.evaluate_records(records)

    assert payload["status"] == "FAIL"
    assert payload["failures"][0]["reason"] == "risk downgrade"
