# 0750 - State Machine Publish Runner Event Hooks

## 1. Scopo

Lo STEP 0750 collega in modo prudente `scripts/asf_publish_step.ps1`
alla Step Execution State Machine.

Il runner puo' ora emettere eventi state machine durante Phase B e Phase C,
ma solo quando la config lo richiede esplicitamente.

Il runner resta human-gated:

- Phase B richiede ancora `-ApprovePublish`;
- Phase C richiede ancora `-ApproveMerge`;
- Codex non deve usare questo step per fare commit, push, PR, merge o deploy;
- gli hook non autorizzano nuove azioni operative.

## 2. Problema risolto

Dopo STEP 0740 il flusso MVP era usabile, ma il collegamento tra:

- state machine;
- publish config generator;
- manifest/evidence;
- publish runner Phase B/Phase C;

restava manuale.

Gli operatori dovevano registrare manualmente eventi come:

- `phase_b_started`;
- `phase_b_passed`;
- `pr_created`;
- `phase_c_started`;
- `phase_c_passed`;
- `main_verified`;
- eventi di failure e recovery.

Lo STEP 0750 riduce questa frizione senza trasformare il runner in automazione
autonoma.

## 3. Campi config supportati

I campi sono opzionali e retrocompatibili.
Le config legacy senza `state_machine_enabled` continuano a comportarsi come
prima.

| Campo | Default | Significato |
|---|---|---|
| `state_machine_enabled` | `false` | Abilita gli hook state machine. |
| `state_file` | `tmp/state_machine/<step>_state.json` o `LAST-State.json` se Bridge state attivo | File JSON di stato da aggiornare. |
| `state_bridge_root` | richiesto se `state_write_bridge=true` | Root Bridge state machine. Nei test usare sempre `tmp/`. |
| `state_write_bridge` | `false` | Passa `--write-bridge` alla state machine. |
| `state_step` | `step` della config | Step atteso dalla state machine. |
| `state_fail_on_hook_error` | `true` se hook abilitati | Fallisce il runner quando un hook fallisce. |
| `state_expected_before_phase_b` | `READY_TO_PUBLISH` | Stato richiesto prima di Phase B. |
| `state_expected_before_phase_c` | `PR_CREATED` | Stato richiesto prima di Phase C. |
| `state_emit_main_verified` | `true` | Emette `main_verified` dopo Phase C riuscita. |
| `state_close_on_phase_c_success` | `false` | Emette anche `close_step` dopo Phase C riuscita. |

## 4. Eventi emessi

### Phase B

Con hook abilitati:

1. prima delle operazioni operative:
   - `phase_b_started`;
2. dopo commit/push/PR completati:
   - `phase_b_passed`;
   - `pr_created`;
3. in caso di failure operativa dopo `phase_b_started`:
   - `phase_b_failed`.

### Phase C

Con hook abilitati:

1. prima delle operazioni di merge:
   - `phase_c_started`;
2. dopo merge e verifiche finali riuscite:
   - `phase_c_passed`;
   - `main_verified`, salvo `state_emit_main_verified=false`;
   - `close_step`, solo se `state_close_on_phase_c_success=true`;
3. in caso di failure operativa dopo `phase_c_started`:
   - `phase_c_failed`.

Gli eventi di successo non vengono emessi se la fase fallisce.

## 5. Failure handling

La state machine resta la fonte autorevole per transizioni e recovery.
Il runner la invoca tramite argv, senza shell execution.

Comportamento:

- se Phase B non parte da `READY_TO_PUBLISH`, il runner fallisce prima di
  commit/push/PR;
- se Phase C non parte da `PR_CREATED`, il runner fallisce prima del merge;
- se Phase B fallisce dopo `phase_b_started`, il runner tenta
  `phase_b_failed`;
- se Phase C fallisce dopo `phase_c_started`, il runner tenta
  `phase_c_failed`;
- se anche l'hook di failure fallisce, il runner fallisce e segnala recovery
  manuale;
- se una fase operativa riesce ma un hook di successo fallisce, il runner non
  dichiara successo pieno e richiede controllo manuale dello stato.

In particolare, `PHASE C completed` viene scritto solo dopo merge, verifiche e
hook di successo completati.

## 6. Bridge output

L'output compatto del publish runner include una sezione sintetica:

- state machine enabled;
- state file;
- state bridge root;
- last state event emitted;
- final state;
- hook warnings/errors;
- close step emitted.

Se `state_write_bridge=true`, la state machine scrive anche i propri artifact
nel root indicato:

- `LAST-State.json`;
- `LAST-Event.json`;
- `LAST-Output_Compatto.md`;
- file progressivi per step.

I test usano solo directory temporanee e non richiedono Dropbox reale.

## 7. Esempi

Esempi minimali:

```text
examples/publish_step/0750_publish_config_state_hooks.example.json
examples/publish_step/0750_publish_config_state_hooks_close_step.example.json
examples/publish_step/0750_publish_config_state_hooks_mismatch_fail_closed.example.json
```

Gli esempi usano `tmp/` per stato e Bridge state machine.

## 8. Limiti residui

Gli hook non integrano ancora direttamente il manifest 0710.
Il mapping eventi -> evidence resta nel report runner e nei file state machine.

Restano manuali:

- approvazione Phase B;
- approvazione Phase C;
- verifica del PR number quando necessario;
- pubblicazione tramite runner standard;
- decisione finale Alberto/ChatGPT.

## 9. Prossimo step consigliato

```text
0770) Runner Hook Evidence Manifest Integration
```

Motivo: lo STEP 0760 ha preparato un secondo pilot reale con state file
`READY_TO_PUBLISH` e config hook-aware validata in `Phase Plan`. Ora serve
collegare eventi runner/state machine a manifest ed evidence pack.

## 10. Aggiornamento STEP 0760

Lo STEP 0760 ha introdotto:

```text
0760) MVP Real Step Pilot 2 with State Hooks
docs/motor/0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md
```

Il pilot conferma che una config con `state_machine_enabled=true` puo' essere
preparata e validata in `Phase Plan` su uno step reale piccolo. La validazione
completa resta demandata alla pubblicazione reale con `-ApprovePublish` e
`-ApproveMerge`.
