# 0690 - State Machine Integration with Publish Config Generator

## 1. Scopo

Lo STEP 0690 collega il Publish Config Generator alla Step Execution State Machine.

Il generator resta un componente locale e dichiarativo: prepara config JSON e output Bridge, ma non esegue Phase B, Phase C, commit, push, PR, merge o deploy.

L'integrazione e' opzionale. Senza opzioni state machine, il comportamento 0650/0660 resta invariato.

## 2. Problema risolto

Prima dello STEP 0690 il generator poteva creare `LAST-Publish_Config.json` senza consultare lo stato dello step.

Ora, quando l'integrazione e' attiva, il generator:

- legge uno state file esistente o `<state-bridge-root>/LAST-State.json`;
- verifica che lo step e lo stato siano coerenti;
- applica l'evento state machine dichiarato solo se `--update-state` e' attivo;
- scrive riferimenti incrociati tra output generator e output state machine;
- fallisce chiuso se lo stato e' mancante, corrotto, incoerente o non aggiornabile.

## 3. CLI

Esempio legacy, invariato:

```powershell
python scripts/asf_publish_config_generator.py --input-file examples/publish_config_generator/sample_motor_core_input.json --out-dir tmp/publish_config --json
```

Esempio con stato richiesto ma non aggiornato:

```powershell
python scripts/asf_publish_config_generator.py --input-file examples/publish_config_generator/sample_state_machine_integration_input.json --state-file examples/state_machine/sample_local_verified_state.json --require-state --out-dir tmp/publish_config --json
```

Esempio con update state e output Bridge temporanei:

```powershell
python scripts/asf_publish_config_generator.py --input-file examples/publish_config_generator/sample_state_machine_integration_input.json --write-bridge --bridge-root tmp/publish_config_bridge --state-file examples/state_machine/sample_local_verified_state.json --state-event publish_config_generated --update-state --write-state-bridge --state-bridge-root tmp/state_machine_bridge --out-dir tmp/publish_config --json
```

## 4. Opzioni state machine

- `--state-file`: file JSON state machine da leggere o aggiornare.
- `--state-bridge-root`: root Bridge state machine; se `--state-file` manca, legge `LAST-State.json`.
- `--require-state`: richiede stato presente e coerente.
- `--state-expected-current`: stato corrente atteso prima della generazione.
- `--state-event`: evento da applicare con `--update-state`; default operativo `publish_config_generated`.
- `--update-state`: applica l'evento tramite `scripts/asf_step_state_machine.py`.
- `--state-target-after`: stato atteso dopo evento; default `READY_TO_PUBLISH` con `--update-state`.
- `--write-state-bridge`: scrive `LAST-State.json`, `LAST-Event.json`, output compatto e completo state machine.
- `--state-allow-recovery`: abilita esplicitamente contesti recovery o step combinati.

## 5. Stati ammessi

Per una config pronta alla pubblicazione il generator accetta in modo prudente:

- `LOCAL_VERIFIED`;
- `READY_TO_PUBLISH`, solo per consultazione o rigenerazione senza avanzare lo stesso evento;
- `RECOVERY_REQUIRED`, solo con `--state-allow-recovery` e warning esplicito.

`IMPLEMENTED` non e' sufficiente per produrre una config pronta: prima servono check locali e `local_checks_passed`.

## 6. Evento standard

Quando la config e' valida e `--update-state` e' attivo, il generator applica:

```text
publish_config_generated
```

La transizione standard e':

```text
LOCAL_VERIFIED -> READY_TO_PUBLISH
```

Se la state machine non ammette la transizione, il generator fallisce chiuso e non scrive una config pronta.

## 7. Output Bridge incrociato

Con `--write-bridge`, il riepilogo compatto del generator include:

- state file usato;
- stato prima;
- evento applicato;
- stato dopo;
- path `LAST-State.json`;
- path `LAST-Publish_Config.json`;
- warning;
- prossima azione consigliata dalla state machine.

Con `--write-state-bridge`, la state machine mantiene il formato 0680:

- `LAST-State.json`;
- `LAST-Event.json`;
- `LAST-Output_Compatto.md`;
- `LAST-Output_Completo.txt`;
- file progressivi dello step.

I test usano solo directory temporanee e non richiedono Dropbox reale.

## 8. Fail-closed

Il generator blocca la config quando:

- lo state file richiesto manca;
- lo state file e' JSON corrotto;
- `current_state` non e' ammesso;
- lo step input e lo step state non coincidono;
- uno step combinato/recovery non e' dichiarato con `--state-allow-recovery`;
- l'evento non e' ammesso dalla state machine;
- lo stato dopo evento non coincide con `--state-target-after`;
- `--write-state-bridge` non riesce a scrivere quando richiesto.

## 9. Limiti intenzionali

Lo STEP 0690 non aggiunge hook automatici al publish runner.

Restano manuali:

- revisione della config;
- lancio Phase B con approvazione esplicita;
- lancio Phase C con approvazione esplicita;
- verifica finale su `main`;
- commit, push, PR, merge e deploy.

## 10. Prossimo step consigliato

0700) End-to-End MVP Smoke Scenario

Motivo: ora generator e state machine dialogano senza pubblicare. Il passo piu' utile e' validare un percorso end-to-end locale e smoke, con Bridge temporaneo, senza ancora aggiungere hook automatici al runner.
