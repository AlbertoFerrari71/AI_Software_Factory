# 1010 - Final End-to-End Smoke Test

## Scopo

Questo step introduce uno smoke test locale end-to-end per il supervised loop ASF.

Lo smoke resta completamente mock/dry-run. Non esegue provider live, non esegue Codex reale, non pubblica, non fa merge e non fa deploy.

## Script

```text
scripts/asf_supervised_loop_smoke.py
```

CLI minima:

```text
python scripts/asf_supervised_loop_smoke.py --root tmp\asf_supervised_loop_smoke --json
```

## Scenario positivo

Lo scenario sintetico usa:

```text
1010-smoke-docs-step
```

Il flusso attraversa stati protocollo 0950 o equivalenti:

- `IDLE`;
- `PLAN_REQUESTED`;
- `GPT_PLANNING`;
- `GPT_PLAN_READY`;
- `CODEX_READY`;
- `CODEX_DONE` con reason `CODEX_DRY_RUN_DONE`;
- `REVIEW_REQUESTED`;
- `REVIEW_PASS`;
- `VERIFY_RUNNING`;
- `VERIFY_PASS`;
- `COMPLETED`.

## Componenti usati

Lo smoke usa in modo mock/dry-run:

- `scripts/asf_gpt_prompt_generator.py`;
- `scripts/asf_codex_exec_adapter.py`;
- `scripts/asf_verification_profile_selector.py`;
- `scripts/asf_powershell_task_runner.py`;
- `scripts/asf_powershell_recovery_classifier.py`;
- `scripts/asf_step_decision_policy.py`;
- `state.json` temporaneo;
- event log JSONL temporaneo.

## Scenari controllati

Oltre al positivo `COMPLETED`, lo smoke produce decisioni:

- `ASK_ALBERTO` per richiesta publish;
- `FIX` per failure recuperabile;
- `STOP` per forbidden action.

## Output

Template:

```text
docs/templates/1010_SUPERVISED_LOOP_SMOKE_STATE_TEMPLATE.json
```

Lo script scrive sotto la root temporanea:

- `1010-smoke-step-plan.json`;
- prompt simulato sotto `bridge_simulated/codex_command/`;
- `codex_exec_envelope.json`;
- `codex_exec_report.md`;
- `state.json`;
- `events.jsonl`;
- `smoke_result.json`.

## Guardrail

- no chiamate live;
- no Codex reale;
- no pubblicazione Git;
- no merge;
- no deploy;
- no OS appunti;
- nessuna scrittura fuori dalla root smoke.

## Test

```text
tests/unit/test_asf_supervised_loop_smoke.py
```

Copertura minima:

- scenario positivo `COMPLETED`;
- scenario `ASK_ALBERTO`;
- scenario `FIX`;
- scenario `STOP`;
- `state.json` aggiornato;
- event log scritto;
- artifact sotto root temporanea.
