# 0700 - End-to-End MVP Smoke Scenario

## 1. Scopo

Lo STEP 0700 introduce uno smoke end-to-end locale del Motore ASF.

Lo script dedicato e':

```text
scripts/asf_e2e_mvp_smoke.py
```

Lo smoke dimostra che i componenti principali lavorano insieme senza eseguire pubblicazione reale.

Componenti attraversati:

- Step Execution State Machine;
- Risk Classifier;
- Dry-run Loop Runner;
- Gate Decision Report;
- Verification Profile Selector;
- Publish Config Generator.

## 2. Scenario positivo

Scenario CLI:

```powershell
python scripts/asf_e2e_mvp_smoke.py --scenario code-unit-to-ready-to-publish --out-dir tmp/e2e_mvp_smoke --json
```

Input simulato:

- step: `0700-smoke`;
- tipo: `code-unit`;
- rischio dichiarato: `L2`;
- file simulati: `scripts/example_component.py`, `tests/unit/test_example_component.py`;
- gate dichiarato: `local_verification`.

Flusso:

1. inizializza stato da `PLANNED`;
2. applica `prompt_saved`;
3. applica `codex_completed`;
4. applica `local_checks_passed`;
5. classifica rischio con `asf_risk_classifier`;
6. costruisce evidence compatibile con `asf_dry_run_loop_runner`;
7. genera `gate_decision_packet.json`;
8. seleziona il profilo di verifica;
9. invoca il Publish Config Generator con state integration;
10. applica `publish_config_generated`;
11. arriva a `READY_TO_PUBLISH`;
12. scrive un evidence pack locale.

## 3. Scenario negativo fail-closed

Scenario CLI:

```powershell
python scripts/asf_e2e_mvp_smoke.py --scenario invalid-state-to-publish-config --out-dir tmp/e2e_mvp_smoke_negative --json
```

Input simulato:

- stato corrente: `IMPLEMENTED`;
- generator invocato con `--require-state`;
- evento richiesto: `publish_config_generated`.

Risultato atteso:

- stato non avanzato a `READY_TO_PUBLISH`;
- nessuna `publish_config.json` pronta prodotta;
- output `negative_fail_closed.json` con blocker espliciti;
- codice CLI dello smoke pari a 0 solo se il blocco fail-closed e' stato osservato.

## 4. Evidence pack

Percorso locale consigliato:

```text
tmp/e2e_mvp_smoke
```

File principali:

- `input_step.json`;
- `risk_report.json`;
- `dry_run_report.json`;
- `gate_decision_packet.json`;
- `verification_profile.json`;
- `publish_config.json` solo nello scenario positivo;
- `state_before.json`;
- `state_after.json`;
- `evidence_summary.md`;
- `evidence_summary.json`;
- `evidence_pack.json`;
- `negative_fail_closed.json` nello scenario negativo.

## 5. Output Bridge opzionale

Lo smoke puo' scrivere output Bridge solo se richiesto:

```powershell
python scripts/asf_e2e_mvp_smoke.py --scenario code-unit-to-ready-to-publish --write-bridge --bridge-root tmp/e2e_smoke_bridge --markdown
```

Nei test si usa sempre una directory temporanea. Dropbox reale non e' richiesto.

Output Bridge:

- `0700-II-Evidence_Summary_<scenario>.md`;
- `0700-II-Evidence_Pack_<scenario>.json`;
- `LAST-Evidence_Summary.md`;
- `LAST-Evidence_Pack.json`.

## 6. Guardrail

Lo smoke non esegue:

- Phase B;
- Phase C;
- commit;
- push;
- pull request;
- merge;
- deploy;
- operazioni GitHub;
- chiamate OpenAI/API esterne.

Il Publish Config Generator viene invocato solo per produrre config e aggiornare lo state file locale tramite `publish_config_generated`.

## 7. Limiti intenzionali

Restano simulati:

- file applicativi `scripts/example_component.py` e test dedicato;
- esito dei check locali nello scenario smoke;
- review umana finale della config;
- lancio del runner di pubblicazione.

Restano human-gated:

- review della config generata;
- Phase B;
- Phase C;
- commit, push, PR, merge e verifica finale su `main`.

## 8. Test

Test dedicato:

```powershell
python -m pytest tests/unit/test_asf_e2e_mvp_smoke.py -q
```

Il test verifica scenario positivo, scenario negativo, output JSON/Markdown, Bridge temporaneo e guardrail no-publish.

## 9. Stato MVP

Dopo STEP 0700 il Motore ASF dimostra un percorso locale end-to-end fino a `READY_TO_PUBLISH`.

Non basta ancora per dichiarare completo il MVP Motore perche' manca un manifest run/evidence stabile che colleghi ogni artifact del percorso a un singolo record operativo riusabile dal runner e dal report finale.

## 10. Prossimo step consigliato

0710) Motor Run Manifest and Evidence Pack

Motivo: lo smoke 0700 produce gia' evidence locali, ma il prossimo avanzamento utile e' normalizzare un manifest unico del run e dell'evidence pack prima di aggiungere hook automatici al publish runner.
