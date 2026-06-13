# 1200 - State Card Schema

## Purpose

The State Card is the compact continuity artifact for the next model turn. It
summarizes only the state needed to decide the next safe action.

## Required Fields

| Field | Meaning |
|---|---|
| state_card_version | Schema contract version. |
| project | Project name. |
| last_completed_step | Last milestone completed and verified. |
| current_branch | Current branch from Git evidence. |
| head_commit | Current HEAD commit or short hash. |
| repo_clean | Whether the working tree is clean. |
| last_gate_status | Last deterministic gate status. |
| last_ci_status | Last CI status if available. |
| capabilities_now_available | New capabilities that can be used safely. |
| open_warnings | Known warnings that should not be forgotten. |
| do_not_forget | Critical constraints for the next step. |
| next_recommended_step | Next roadmap step. |
| human_decision_required | Whether Alberto must decide before progress. |

## Rules

- The State Card is not a full report.
- It must not contain secrets or raw provider output.
- It must prefer evidence paths over copied evidence.
- It must be regenerated after every completed or blocked milestone.
- It must not authorize publish, merge or deploy by itself.

## Machine Contract

The JSON Schema is:

```text
schemas/asf_automation/state_card.schema.json
```

The offline example is:

```text
examples/asf_automation/state_card_example.json
```
