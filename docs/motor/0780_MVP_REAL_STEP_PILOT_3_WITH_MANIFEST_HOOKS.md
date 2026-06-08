# 0780 - MVP Real Step Pilot 3 with Manifest Hooks

## 1. Scopo

Lo STEP 0780 prepara un terzo pilot reale piccolo del Motore ASF, usando anche
il manifest hook-aware introdotto nello STEP 0770.

Lo scopo e' dimostrare che una modifica reale documentale puo' essere collegata
in modo auditabile a:

- state machine;
- publish config hook-aware;
- publish runner con state hooks;
- state finale;
- manifest con `runner_hooks`;
- evidence pack locale.

Codex non esegue Phase B, Phase C, commit, push, PR, merge o deploy. La
pubblicazione reale resta demandata ad Alberto/ChatGPT tramite
`scripts/asf_publish_step.ps1`.

## 2. Contesto

Lo stato verificato prima del pilot e':

- branch locale: `main`;
- working tree iniziale: pulita;
- `main` contiene `93279ba 0770 integrate runner hook evidence into manifest (#69)`;
- documento 0770 presente:
  `docs/motor/0770_RUNNER_HOOK_EVIDENCE_MANIFEST_INTEGRATION.md`.

Lo STEP 0770 permette al manifest di leggere uno state file prodotto dagli hook
del runner e di classificare la traccia come `CLOSED`, `INCOMPLETE` o
`FAIL_CLOSED` in base a final state, step atteso ed eventi richiesti.

## 3. Modifica reale scelta

La modifica reale scelta e' questo documento:

```text
docs/motor/0780_MVP_REAL_STEP_PILOT_3_WITH_MANIFEST_HOOKS.md
```

Il pilot resta documentale, piccolo e reversibile. Non cambia la logica core
del runner, della state machine, del generator o del manifest.

## 4. Differenza rispetto al pilot 0760

Il pilot 0760 validava uno step reale con:

- state file iniziale in `READY_TO_PUBLISH`;
- config hook-aware;
- validazione `Phase Plan`;
- aspettativa di eventi Phase B/C prodotti dal runner.

Il pilot 0780 aggiunge il collegamento mancante dopo la pubblicazione reale:

- il manifest deve leggere lo state file prodotto dagli hook;
- deve verificare final state `CLOSED`;
- deve verificare gli eventi runner attesi;
- deve rendere espliciti eventi mancanti e mismatch.

## 5. Hook state machine usati

La config di pubblicazione attesa deve abilitare gli hook state machine del
runner con:

```json
{
  "state_machine_enabled": true,
  "state_file": "tmp/0780_mvp_real_step_pilot_3_manifest_hooks/state_machine/0780_state.json",
  "state_step": "0780",
  "state_write_bridge": true,
  "state_bridge_root": "tmp/0780_mvp_real_step_pilot_3_manifest_hooks/state_bridge",
  "state_fail_on_hook_error": true,
  "state_expected_before_phase_b": "READY_TO_PUBLISH",
  "state_expected_before_phase_c": "PR_CREATED",
  "state_emit_main_verified": true,
  "state_close_on_phase_c_success": true
}
```

Eventi attesi:

- `phase_b_started`;
- `phase_b_passed`;
- `pr_created`;
- `phase_c_started`;
- `phase_c_passed`;
- `main_verified`;
- `close_step`.

## 6. Manifest hook-aware usato

Dopo la pubblicazione reale, il manifest deve essere generato con
`--include-runner-hooks` e deve leggere lo state file reale prodotto dal runner.

Comando atteso, da adattare ai path finali della pubblicazione:

```powershell
python scripts/asf_motor_run_manifest.py `
  --input-file tmp/0780_mvp_real_step_pilot_3_manifest_hooks/manifest_input/0780_manifest_input.json `
  --out-dir tmp/0780_mvp_real_step_pilot_3_manifest_hooks/manifest_post_publish `
  --include-runner-hooks `
  --state-file tmp/0780_mvp_real_step_pilot_3_manifest_hooks/state_machine/0780_state.json `
  --state-bridge-root tmp/0780_mvp_real_step_pilot_3_manifest_hooks/state_bridge `
  --publish-runner-output tmp/0780_mvp_real_step_pilot_3_manifest_hooks/runner_bridge `
  --publish-config tmp/0780_mvp_real_step_pilot_3_manifest_hooks/publish_config/0780_publish_config_state_hooks.json `
  --expected-step 0780 `
  --expected-final-state CLOSED `
  --expected-events phase_b_started phase_b_passed pr_created phase_c_started phase_c_passed main_verified close_step
```

Il manifest deve produrre `runner_hooks.missing_events` vuoto e decisione
coerente con `CLOSED`.

## 7. Stato iniziale richiesto

Lo stato iniziale richiesto prima di Phase B e':

```text
READY_TO_PUBLISH
```

Lo state file temporaneo del pilot viene preparato sotto:

```text
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/state_machine/0780_state.json
```

`READY_TO_PUBLISH` non equivale ad approval. Phase B resta possibile solo con
approval esplicita e config revisionata.

## 8. Config publish attesa

La config hook-aware attesa deve includere:

- `step: "0780"`;
- branch di pubblicazione dedicato;
- profilo di verifica coerente con lo scope;
- expected files limitati ai documenti e agli eventuali aggiornamenti health
  check;
- `state_machine_enabled: true`;
- state file e Bridge state machine sotto `tmp/`;
- `state_expected_before_phase_b: READY_TO_PUBLISH`;
- `state_expected_before_phase_c: PR_CREATED`;
- `state_emit_main_verified: true`;
- `state_close_on_phase_c_success: true`.

La validazione locale ammessa per Codex e' solo `Phase Plan`.

## 9. Flusso Phase B atteso

Durante Phase B, il runner deve:

1. verificare che lo state file sia in `READY_TO_PUBLISH`;
2. emettere `phase_b_started`;
3. eseguire i check previsti dal profilo;
4. creare branch/commit/PR solo nel flusso pubblicazione autorizzato da
   Alberto/ChatGPT;
5. emettere `phase_b_passed`;
6. emettere o confermare `pr_created`;
7. scrivere output Bridge runner e state machine se configurati.

Codex non esegue Phase B nello STEP 0780.

## 10. Flusso Phase C atteso

Durante Phase C, il runner deve:

1. verificare che lo state file sia in `PR_CREATED`;
2. emettere `phase_c_started`;
3. verificare PR/check secondo config e policy;
4. eseguire merge solo con approval esplicita;
5. rieseguire le verifiche finali su `main`;
6. emettere `phase_c_passed`;
7. emettere `main_verified`;
8. emettere `close_step`;
9. scrivere `LAST-State.json` e `LAST-Event.json` nel Bridge state machine se
   configurato.

Codex non esegue Phase C nello STEP 0780.

## 11. Manifest post-publish atteso

Dopo Phase B/C reali, il manifest hook-aware deve confermare:

- state file presente e JSON valido;
- `step` dello state file uguale a `0780`;
- `current_state` finale uguale a `CLOSED`;
- eventi richiesti presenti;
- `missing_events` vuoto;
- riferimenti a state file, Bridge state machine, publish config e output runner
  leggibili;
- decisione finale `CLOSED` o equivalente priva di blocker.

Se manca un evento richiesto, il manifest deve dichiarare `INCOMPLETE`. Se step
o final state non coincidono, deve dichiarare `FAIL_CLOSED`.

## 12. Evidence summary

Evidence temporanee prodotte nello STEP 0780:

```text
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/state_machine/0780_state.json
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/state_bridge/
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/publish_config/
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/publish_config/0780_publish_config.json
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/publish_config/0780_publish_config_state_hooks.json
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/publish_config/phase_plan_hook_aware.txt
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/runner_bridge/
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/manifest_input/0780_manifest_input_synthetic.json
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/manifest_synthetic/
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/manifest_synthetic/0780_closed_state.json
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/manifest_synthetic/motor_run_manifest.json
tmp/0780_mvp_real_step_pilot_3_manifest_hooks/manifest_synthetic/motor_run_summary.md
```

Strumenti usati:

- `scripts/asf_step_state_machine.py`;
- `scripts/asf_publish_config_generator.py`;
- `scripts/asf_publish_step.ps1 -Phase Plan`;
- `scripts/asf_motor_run_manifest.py --include-runner-hooks`.

Output prodotti:

- state file iniziale pronto per Phase B: `READY_TO_PUBLISH`;
- config hook-aware con campi state machine del runner;
- `Phase Plan` hook-aware: PASS, con messaggio `PLAN - config validated. No
  GitHub or publish action executed.`;
- manifest sintetico hook-aware: decisione `CLOSED`;
- `runner_hooks.final_state`: `CLOSED`;
- `runner_hooks.last_event`: `close_step`;
- `runner_hooks.missing_events`: `[]`;
- `runner_hooks.required_events_present`: `true`;
- warning accettato: la validazione completa resta post-publish reale.

## 13. Risultati

Risultato locale del pilot:

- lo STEP 0770 e' presente su `main`;
- il pilot 0780 documenta una modifica reale versionabile;
- lo state file iniziale/hook plan e' definito;
- lo state file iniziale e' stato preparato in `READY_TO_PUBLISH`;
- la config hook-aware temporanea e' stata validata in `Phase Plan`;
- il manifest hook-aware sintetico e' stato validato con decisione `CLOSED`;
- nessuna Phase B o Phase C viene eseguita da Codex;
- nessun commit, push, PR, merge o deploy viene eseguito da Codex.

## 14. Warning

Warning accettati:

- il pilot resta documentale;
- lo state file iniziale viene preparato localmente ma non usato da Codex in
  Phase B/C;
- la validazione completa del manifest richiede la pubblicazione reale;
- `LAST-State.json` e `LAST-Run_Manifest.json` vanno verificati dopo Phase C;
- il manifest reale post-publish resta da generare manualmente o tramite runner
  operativo futuro.

## 15. Decisione finale

```text
PILOT STATUS: GO WITH WARNINGS
```

Motivo: il pilot e' piccolo, in scope e predisposto per auditare runner ->
state machine -> manifest, ma la prova completa dipende dalla pubblicazione
human-gated successiva.

## 16. Lezioni apprese

- Gli hook del runner e il manifest 0770 sono coerenti per descrivere una
  pubblicazione reale piccola.
- Il punto chiave non e' solo arrivare a `READY_TO_PUBLISH`, ma correlare gli
  eventi finali fino a `CLOSED`.
- `close_step` rende il manifest piu' esplicito quando deve distinguere una
  chiusura completa da una pubblicazione non chiusa.
- La parte ancora manuale e' la generazione del manifest reale dopo merge.

## 17. Prossimo step consigliato

```text
0790) Post-MVP Roadmap and Hardening Plan
```

Motivo: dopo tre pilot reali e l'integrazione hook/manifest, il valore maggiore
e' consolidare warning, recovery drill, standard di evidence e criteri per
rendere il flusso ordinario senza aggiungere automazione pericolosa.
