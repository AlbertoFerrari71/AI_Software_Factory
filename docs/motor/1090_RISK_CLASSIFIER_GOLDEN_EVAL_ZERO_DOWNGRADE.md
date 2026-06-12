# 1090 - Risk Classifier Golden Eval and Zero-Downgrade Gate

## Purpose

Protect the ASF decision core from safety regressions.

## Dataset

Golden dataset:

```text
examples/eval/risk_classifier/golden.jsonl
```

It covers docs-only changes, tests, CI, PowerShell runner changes,
publication, secrets, path traversal, raw provider payloads, destructive
commands, branch/PR ambiguity, no checks reported, live provider calls,
prompt injection, state machine changes, handoff/report only and Bridge
incoherence.

## Runner

```powershell
python scripts/asf_risk_classifier_eval.py
```

Policy:

- zero downgrade is mandatory;
- L3 to L2 is FAIL;
- L4 to L3 is FAIL;
- more conservative classification is allowed as warning;
- average accuracy is not the main metric.

## Error Learning Ledger 0930

No local or tracked remote branch for 0930 was found during this step. Existing
0930 references remain document-level pointers to External Repo Push Pattern
Generalization. Recovery of an Error Learning Ledger remains a future step if
Alberto confirms the source branch or artifact.

## Acceptance

- Golden JSONL is versioned.
- Eval runner exits nonzero on downgrade.
- `verify.ps1` and CI run the eval.
