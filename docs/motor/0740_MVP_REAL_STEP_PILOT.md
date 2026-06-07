# 0740 - MVP Real Step Pilot

## 1. Scopo

Questo documento registra il primo pilot reale post-MVP del Motore ASF.

Lo scopo e' applicare la baseline chiusa nello STEP 0730 a una modifica reale
piccola, locale, reversibile e verificabile, senza eseguire commit, push, PR,
merge o deploy da Codex.

Il pilot non prova una readiness produttiva completa. Serve a capire se
runbook, state machine, manifest, generator e verifiche locali sono usabili su
uno step non puramente sintetico.

## 2. Contesto

Verifica iniziale eseguita nello STEP 0740:

- branch corrente: `main`;
- working tree iniziale osservata da Codex: gia' modificata con file nello
  scope dello STEP 0740, senza file sporchi fuori scope rilevati;
- commit HEAD verificato: `2274ae2 0730 add end-to-end MVP closure pack (#65)`;
- `main` contiene lo STEP 0730;
- stato MVP dichiarato nello STEP 0730: `MVP STATUS: GO WITH WARNINGS`;
- prompt dello step salvato nel Bridge `codex_command`; durante il salvataggio
  e' comparso un warning non bloccante su `New-Item -LiteralPath`, ma i file
  richiesti risultano scritti.

Il riferimento operativo principale e' il runbook:

```text
docs/motor/0720_MVP_USAGE_RUNBOOK.md
```

## 3. Modifica reale scelta

Il pilot scelto e' `MVP Pilot Notes`.

La modifica reale consiste nel creare questo documento operativo e aggiornare
in modo minimo gli indici gia' usati dal progetto:

- `README.md`;
- `CHANGELOG.md`;
- `docs/10_ROADMAP.md`;
- `docs/11_DECISIONS.md`;
- `docs/34_PROJECT_WORKFLOW_INDEX.md`;
- `docs/35_WORKFLOW_HEALTH_CHECK.md`;
- `docs/motor/0570_MVP_MOTOR_ROADMAP.md`;
- `docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md`;
- `scripts/check_workflow_health.py`;
- `tests/unit/test_workflow_health_check.py`.

La modifica resta documentale/strumentale: non introduce nuove automazioni
operative, non modifica il publish runner e non cambia logica applicativa core.

## 4. Flusso MVP applicato

Percorso seguito:

1. prompt salvato nel Bridge `codex_command`;
2. repo verificata su `main` con working tree iniziale gia' modificata solo
   nello scope 0740;
3. STEP 0730 verificato su `HEAD`;
4. runbook 0720 usato come riferimento operativo;
5. state machine locale usata sotto `tmp/0740_mvp_real_step_pilot/`;
6. modifiche locali applicate senza pubblicazione;
7. verifiche locali obbligatorie eseguite;
8. publish config generator usato solo per produrre config/evidence locale;
9. manifest locale prodotto come riepilogo documentale del pilot;
10. decisione finale classificata come `PILOT STATUS: GO WITH WARNINGS`.

Phase B e Phase C non sono state eseguite. Restano compito successivo di
Alberto/ChatGPT tramite `scripts/asf_publish_step.ps1`.

## 5. Componenti usati

Componenti MVP usati direttamente:

- `docs/motor/0720_MVP_USAGE_RUNBOOK.md`;
- `scripts/asf_step_state_machine.py`;
- `scripts/asf_publish_config_generator.py`;
- `scripts/asf_motor_run_manifest.py`;
- `scripts/check_workflow_health.py`;
- `scripts/verify.ps1`.

Componenti usati come riferimento:

- `docs/motor/0730_END_TO_END_MVP_CLOSURE_PACK.md`;
- `scripts/asf_e2e_mvp_smoke.py`;
- `scripts/asf_publish_step.ps1`.

Lo smoke 0700 non e' stato rieseguito come prova principale del pilot: il pilot
ha privilegiato uno step reale piccolo. Lo smoke resta un confronto sintetico
disponibile, non una prova sostitutiva.

## 6. Evidence summary

Evidence temporanea locale sotto `tmp/0740_mvp_real_step_pilot/`:

- state machine locale: `tmp/0740_mvp_real_step_pilot/state_machine/0740_state.json`;
- publish config generator: `tmp/0740_mvp_real_step_pilot/publish_config/0740_publish_config.json`;
- publish config summary: `tmp/0740_mvp_real_step_pilot/publish_config/0740_publish_config_summary.md`;
- manifest input: `tmp/0740_mvp_real_step_pilot/0740_manifest_input.json`;
- manifest output: `tmp/0740_mvp_real_step_pilot/manifest/motor_run_manifest.json`;
- manifest summary: `tmp/0740_mvp_real_step_pilot/manifest/motor_run_summary.md`;
- prompt Bridge salvato in `codex_command` prima delle modifiche repository.

Strumenti usati:

- `scripts/asf_step_state_machine.py` per registrare avanzamento step;
- `scripts/asf_publish_config_generator.py` per generare config pronta per
  review senza eseguire il runner;
- `scripts/asf_motor_run_manifest.py` per normalizzare la run in manifest
  documentale;
- `scripts/check_workflow_health.py`, `python -m pytest -q`, `scripts/verify.ps1`
  e `git --no-pager diff --check` per i gate locali.

Check eseguiti a chiusura step:

- `python scripts/check_workflow_health.py`: PASS;
- `python -m pytest -q`: PASS;
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1`: PASS,
  con `577 passed`;
- `git --no-pager diff --check`: PASS;
- `scripts/asf_step_state_machine.py`: PASS, stato locale finale
  `READY_TO_PUBLISH`;
- `scripts/asf_publish_config_generator.py`: PASS, profilo generato
  `motor-core`;
- `scripts/asf_motor_run_manifest.py`: PASS, decisione manifest
  `READY_TO_PUBLISH`, `fail_closed: false`.

Warning accettati:

- il pilot resta piccolo e in larga parte documentale;
- state machine e generator richiedono comandi manuali;
- il primo tentativo del generator ha mostrato una frizione CLI:
  `--intent` accetta un valore compatto, non piu' argomenti liberi;
- manifest e publish config non autorizzano pubblicazione;
- Phase B e Phase C non vengono eseguite da Codex;
- gli artifact sotto `tmp/` sono evidence operative, non fonte autorevole.

Decisione finale:

```text
PILOT STATUS: GO WITH WARNINGS
```

## 7. Risultati

Risultati ottenuti:

- la baseline MVP 0730 e' stata usata su una modifica reale e versionabile;
- il runbook 0720 e' risultato sufficiente per orientare il lavoro;
- la state machine ha reso visibile il passaggio dello step;
- il generator ha prodotto una config locale `motor-core` senza pubblicare;
- il manifest ha consolidato la run come evidence documentale con decisione
  `READY_TO_PUBLISH` e warning dichiarati;
- il workflow health riconosce il nuovo documento 0740.

La decisione non e' `PILOT STATUS: GO` pieno perche' il pilot non copre ancora
un cambio applicativo operativo ne' l'esecuzione pubblicazione B -> C.

## 8. Warning

Warning residui:

- il flusso richiede ancora piu' comandi manuali di quanti siano comodi;
- i passaggi state machine restano manuali e non agganciati al runner;
- alcuni argomenti CLI del generator sono poco ergonomici per comandi manuali
  lunghi;
- il manifest e' utile, ma per step documentali resta piu' un audit summary
  che una prova semantica forte;
- `READY_TO_PUBLISH` non equivale ad approval;
- il Bridge resta storage operativo e puo' contenere alias `LAST-*` stale;
- Phase B/C devono restare human-gated e fuori da Codex in questo step.

## 9. Decisione finale

Decisione prudente:

```text
PILOT STATUS: GO WITH WARNINGS
```

Motivazione:

- la modifica e' reale, piccola e in scope;
- il flusso MVP ha prodotto stato, config, manifest e verifiche locali;
- nessuna pubblicazione e' stata eseguita;
- restano frizioni manuali coerenti con i warning del MVP.

## 10. Lezioni apprese

Lezioni operative:

- il runbook 0720 e' abbastanza chiaro per guidare uno step reale piccolo;
- la separazione tra prompt Bridge, repo versionata, tmp evidence e publish
  runner e' utile per non confondere i livelli;
- la state machine aiuta a evitare handoff impliciti, ma richiede troppi
  comandi manuali;
- il generator e' utile come prova di readiness, ma va letto come config draft;
- il manifest funziona meglio quando ha evidence strutturata; sugli step
  documentali deve dichiarare esplicitamente il suo limite.

## 11. Prossimo step consigliato

Prossimo step consigliato:

```text
0750) State Machine Publish Runner Event Hooks
```

Motivo: il primo pilot reale conferma che il punto piu' scomodo non e' la
mancanza di documenti, ma la necessita' di aggiornare stato e readiness con
passaggi manuali separati. Il prossimo hardening dovrebbe aggiungere hook
prudenziali e human-gated tra publish runner e state machine, senza ridurre i
gate Phase B/Phase C.
