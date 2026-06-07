# 0760 - MVP Real Step Pilot 2 with State Hooks

## 1. Scopo

Lo scopo dello STEP 0760 e' eseguire un secondo pilot reale piccolo del Motore
ASF, questa volta preparando la pubblicazione successiva con gli hook state
machine introdotti nello STEP 0750.

Il pilot non pubblica nulla da Codex. Serve a verificare che uno step reale,
basso rischio e documentale possa arrivare a `READY_TO_PUBLISH` con una config
hook-aware pronta per `scripts/asf_publish_step.ps1`.

## 2. Contesto

Verifica iniziale eseguita nello STEP 0760:

- branch corrente: `main`;
- working tree iniziale: pulita;
- commit HEAD verificato: `d2be7af 0750 add state machine publish runner hooks (#67)`;
- `main` contiene lo STEP 0750;
- gli hook runner/state machine sono presenti nel runner, nei test e nel
  documento `docs/motor/0750_STATE_MACHINE_PUBLISH_RUNNER_EVENT_HOOKS.md`.

Il Motore ASF MVP resta formalmente chiuso come `GO WITH WARNINGS`. Lo STEP
0760 non cambia questo stato: riduce una frizione operativa e prepara una
validazione reale degli hook durante la pubblicazione successiva.

## 3. Modifica reale scelta

La modifica reale scelta e' il documento:

```text
docs/motor/0760_MVP_REAL_STEP_PILOT_2_WITH_STATE_HOOKS.md
```

Aggiornamenti collegati minimi:

- README;
- changelog;
- roadmap generale;
- decision log;
- Project Workflow Index;
- Workflow Health Check;
- roadmap Motore;
- documenti 0740 e 0750;
- test del Workflow Health Check.

La modifica e' utile per il progetto ma resta a basso rischio: documenta un
pilot operativo e non cambia la logica core del runner.

## 4. Differenza rispetto al pilot 0740

Lo STEP 0740 ha validato la baseline MVP su uno step reale piccolo, ma il
passaggio verso Phase B e Phase C restava manuale rispetto alla state machine.

Lo STEP 0760 aggiunge un elemento in piu':

- stato iniziale preparato a `READY_TO_PUBLISH`;
- config publish temporanea con `state_machine_enabled=true`;
- `Phase Plan` hook-aware validata senza publish;
- aspettativa esplicita sugli eventi che Phase B e Phase C emetteranno durante
  la pubblicazione reale.

Phase B e Phase C non sono state eseguite da Codex.

## 5. Hook state machine usati

La config hook-aware del pilot abilita:

```text
state_machine_enabled: true
state_file: tmp/0760_mvp_real_step_pilot_2_state_hooks/state_machine/0760_state.json
state_write_bridge: true
state_bridge_root: tmp/0760_mvp_real_step_pilot_2_state_hooks/state_bridge
state_expected_before_phase_b: READY_TO_PUBLISH
state_expected_before_phase_c: PR_CREATED
state_emit_main_verified: true
state_close_on_phase_c_success: false
```

Durante la pubblicazione reale, Alberto/ChatGPT potranno sostituire
`state_bridge_root` temporaneo con il Bridge operativo `state_machine`, se
coerente con la config finale. I test e le evidence Codex restano sotto `tmp/`.

Eventi attesi:

- Phase B: `phase_b_started`, `phase_b_passed`, `pr_created`;
- Phase C: `phase_c_started`, `phase_c_passed`, `main_verified`;
- opzionale futuro: `close_step`, solo se la config abilita
  `state_close_on_phase_c_success=true`.

## 6. Stato iniziale richiesto

Lo stato richiesto prima di Phase B e':

```text
READY_TO_PUBLISH
```

State file preparato:

```text
tmp/0760_mvp_real_step_pilot_2_state_hooks/state_machine/0760_state.json
```

Sequenza locale usata per prepararlo:

```text
prompt_saved -> codex_started -> codex_completed -> local_checks_passed -> publish_config_generated
```

Stato finale della preparazione:

```text
current_state: READY_TO_PUBLISH
last_event: publish_config_generated
fail_closed: false
```

`READY_TO_PUBLISH` non equivale ad approval. Phase B richiede comunque
`-ApprovePublish`.

## 7. Config publish attesa

La config hook-aware temporanea e':

```text
tmp/0760_mvp_real_step_pilot_2_state_hooks/publish_config/0760_publish_config_state_hooks.json
```

Campi principali:

```json
{
  "step": "0760",
  "name": "MVP_Real_Step_Pilot_2_With_State_Hooks",
  "branch": "step-0760-mvp-real-step-pilot-2-state-hooks",
  "verification_profile": "motor-core",
  "state_machine_enabled": true,
  "state_file": "tmp/0760_mvp_real_step_pilot_2_state_hooks/state_machine/0760_state.json",
  "state_step": "0760",
  "state_write_bridge": true,
  "state_bridge_root": "tmp/0760_mvp_real_step_pilot_2_state_hooks/state_bridge",
  "state_fail_on_hook_error": true,
  "state_expected_before_phase_b": "READY_TO_PUBLISH",
  "state_expected_before_phase_c": "PR_CREATED",
  "state_emit_main_verified": true,
  "state_close_on_phase_c_success": false
}
```

Il selector ha raccomandato `motor-core` perche' lo step aggiorna anche
`scripts/check_workflow_health.py` e il test associato. Questa scelta mantiene
le verifiche conservative.

## 8. Flusso Phase B atteso

Durante la pubblicazione reale con:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config <config> -Phase B -ApprovePublish
```

il runner deve:

1. verificare che lo state file sia in `READY_TO_PUBLISH`;
2. emettere `phase_b_started`;
3. rieseguire le verifiche locali previste dalla config;
4. creare branch, commit, push e PR solo per i file attesi;
5. emettere `phase_b_passed`;
6. emettere `pr_created`;
7. lasciare lo stato atteso per Phase C in `PR_CREATED`.

Se lo stato iniziale non e' `READY_TO_PUBLISH`, il runner deve fallire chiuso
prima della pubblicazione.

## 9. Flusso Phase C atteso

Durante la pubblicazione reale con:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\asf_publish_step.ps1 -Config <config> -Phase C -PrNumber <PR_NUMBER> -ApproveMerge
```

il runner deve:

1. verificare che lo state file sia in `PR_CREATED`;
2. emettere `phase_c_started`;
3. verificare i check GitHub/PR secondo config e policy;
4. eseguire merge solo con approval esplicita;
5. rieseguire le verifiche finali su `main`;
6. emettere `phase_c_passed`;
7. emettere `main_verified`;
8. scrivere `LAST-State.json` e `LAST-Event.json` se il Bridge state machine e'
   abilitato.

`close_step` resta opzionale e non e' abilitato nella config temporanea del
pilot.

## 10. Evidence summary

Evidence temporanee prodotte:

```text
tmp/0760_mvp_real_step_pilot_2_state_hooks/state_machine/0760_state.json
tmp/0760_mvp_real_step_pilot_2_state_hooks/publish_config/0760_publish_config.json
tmp/0760_mvp_real_step_pilot_2_state_hooks/publish_config/0760_publish_config_state_hooks.json
tmp/0760_mvp_real_step_pilot_2_state_hooks/publish_config/generator_result.json
tmp/0760_mvp_real_step_pilot_2_state_hooks/publish_config/phase_plan_state_hooks.txt
tmp/0760_mvp_real_step_pilot_2_state_hooks/runner_bridge/
```

Strumenti usati:

- `scripts/asf_step_state_machine.py`;
- `scripts/asf_publish_config_generator.py`;
- `scripts/asf_publish_step.ps1 -Phase Plan`;
- `scripts/asf_verification_profile_selector.py` invocato dal runner in Plan.

Output principali:

- state file iniziale pronto per Phase B: `READY_TO_PUBLISH`;
- config generator base: `0760_publish_config.json`;
- config hook-aware: `0760_publish_config_state_hooks.json`;
- Phase Plan hook-aware: PASS, con messaggio `PLAN - config validated. No
  GitHub or publish action executed.`;
- profilo di verifica: `motor-core`;
- warning accettato: validazione completa degli hook rimandata alla
  pubblicazione reale.

Check passati nello STEP 0760:

- `python scripts/check_workflow_health.py`: PASS;
- `python -m pytest tests/unit/test_workflow_health_check.py -q`: PASS;
- `python -m pytest -q`: PASS;
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1`: PASS;
- `git --no-pager diff --check`: PASS;
- `git status --short --untracked-files=all`: solo file attesi dello STEP 0760.

## 11. Risultati

Risultato del pilot locale:

- lo STEP 0750 e' presente su `main`;
- gli hook del runner sono documentati e disponibili;
- lo stato 0760 e' stato portato a `READY_TO_PUBLISH`;
- la config hook-aware temporanea e' stata validata in `Phase Plan`;
- nessuna Phase B o Phase C e' stata eseguita da Codex;
- nessun commit, push, PR, merge o deploy e' stato eseguito da Codex.

## 12. Warning

Warning accettati:

- il pilot resta documentale e di basso rischio;
- gli hook completi saranno validati solo nella pubblicazione reale;
- lo state file iniziale e' preparato, ma non usato da Codex in Phase B/C;
- `LAST-State.json` andra' verificato dopo la pubblicazione reale;
- il mapping hook -> manifest/evidence pack non e' ancora integrato.

## 13. Decisione finale

```text
PILOT STATUS: GO WITH WARNINGS
```

Motivo: la preparazione locale e la validazione `Phase Plan` sono coerenti, ma
la prova completa degli hook richiede la pubblicazione reale human-gated tramite
runner.

## 14. Lezioni apprese

- Gli hook 0750 sono sufficientemente espressivi per descrivere il ciclo Phase
  B/Phase C di uno step reale.
- Il profilo `motor-core` e' appropriato appena lo step tocca workflow health o
  test di workflow.
- La config hook-aware e' leggibile, ma richiede ancora un passaggio manuale per
  collegare config, state file, Bridge e manifest.
- `READY_TO_PUBLISH` resta uno stato operativo, non una autorizzazione.

## 15. Prossimo step consigliato

```text
0770) Runner Hook Evidence Manifest Integration
```

Motivo: dopo avere preparato un pilot reale con hook, il prossimo valore e'
collegare gli eventi Phase B/C al manifest/evidence pack, cosi' l'output del
runner e la state machine diventano piu' facili da auditare dopo la
pubblicazione reale.
