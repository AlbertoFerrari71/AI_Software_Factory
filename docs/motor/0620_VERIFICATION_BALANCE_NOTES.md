# 0620 - Verification Balance Notes

## 1. Scopo

Questa nota registra una prima analisi tecnica delle verifiche attuali.

Lo STEP 0630 ha trasformato questa matrice iniziale in un selettore locale dedicato:

```text
scripts/asf_verification_profile_selector.py
docs/motor/0630_VERIFICATION_PROFILE_SELECTOR_TEST_COST_POLICY.md
```

La nota resta come contesto storico e come riferimento sulle ridondanze osservate nello STEP 0620.

---

## 2. Ridondanze osservate

Nel flusso attuale esistono sovrapposizioni intenzionali:

- test mirati: rapidi e utili durante sviluppo di script o policy specifiche;
- `python -m pytest`: copre regressioni generali ma ripete i test mirati gia' eseguiti;
- `scripts/check_workflow_health.py`: controlla presenza file, riferimenti nell'indice e safety scan sugli script;
- `scripts/verify.ps1`: riesegue `python -m pytest`, `git diff --check` e `git status --short`;
- `git --no-pager diff --check`: spesso eseguito sia a mano sia dentro `verify.ps1`;
- runner 0590 Phase A: esegue i check configurati e `diff --check`;
- runner 0590 Phase B: riesegue Phase A prima di publish;
- runner 0590 Phase C: esegue controlli finali dopo merge.

La ridondanza e' utile prima di publish o merge, ma puo' essere costosa durante iterazioni locali su un singolo script.

---

## 3. Matrice profili proposta

| Profilo | Quando usarlo | Check minimi | Check completi |
|---|---|---|---|
| docs-only | Solo documentazione, changelog, roadmap o decision log | `git --no-pager diff --check` + workflow health leggero | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1` |
| code-unit | Codice/test mirati senza superfici workflow sensibili | test mirati + `git --no-pager diff --check` | `python -m pytest -q` + `verify.ps1` |
| motor-core | Runner, gate, risk classifier o decision packet | test mirati + full pytest + workflow health | `verify.ps1` |
| publish | Prima di commit/PR | runner Phase B, che include Phase A | Phase C finale dopo PR/checks |
| high-risk | L4 o side effect esterni | tutto + review manuale | tutto + approvazione elevata |

---

## 4. Proposta prudente

Ridurre tempi non significa saltare gate critici.

Proposta:

- durante sviluppo locale, usare profilo minimo coerente con lo scope;
- prima del report Codex finale su codice motore, usare profilo `motor-core`;
- prima di pubblicare, usare sempre il runner 0590 Phase B, che riesegue Phase A;
- dopo merge, usare Phase C finale;
- per L4, non introdurre shortcut.

---

## 5. Aggiornamento dopo STEP 0630

Il selector 0630 implementa i profili `docs-only`, `code-unit`, `motor-core`, `publish`, `final-main` e `high-risk`.

Riduzioni ammesse:

- `docs-only`: evita full pytest ordinario quando non serve;
- `code-unit`: privilegia test mirati e diff check;
- `publish`: evita Phase A separata quando Phase B la riesegue.

Riduzioni non ammesse:

- `motor-core`: mantiene full pytest, workflow health e verify gate nel percorso raccomandato;
- `final-main`: resta il gate compensativo finale;
- `high-risk`: resta fail-closed e manuale.

---

## 6. Aggiornamento dopo STEP 0640

Il publish runner 0590 ora puo' validare un profilo dichiarato usando il selector 0630.

La riduzione resta prudente:

- config legacy senza profilo restano valide;
- mismatch piu' leggero del profilo raccomandato blocca;
- `allow_profile_check_reduction` default `false`;
- Phase C resta robusta e non ridotta nello STEP 0640.

---

## 7. Aggiornamento dopo STEP 0650

Il generator 0650 produce bozze config publish usando il selector 0630 e i campi supportati dal runner 0640.

La riduzione resta limitata alla preparazione della config:

- i check Phase A sono scelti dal profilo e dai test mirati dedotti;
- Phase C resta completa con full pytest, workflow health e verify gate;
- input mancanti, selector fail-closed, `high-risk`, `final-main` e L4 non producono config ordinaria;
- il generator non esegue il runner e non sostituisce approval umana.

## 8. Step successivo consigliato

```text
0660) Publish Config Generator Bridge Output Integration
```

Deliverable proposto:

- salvare output generator e riepiloghi in Bridge con audit trail dedicato;
- mantenere separati config draft, review umana e publish runner;
- evitare di introdurre una state machine operativa prima di aver chiuso l'evidenza del generator.

---

## 8. Aggiornamento dopo STEP 0660

Il generator ora puo' scrivere un pacchetto Bridge dedicato sotto `publish_config`, incluso `LAST-Publish_Config.json`.

La riduzione riguarda il copia/incolla e la recuperabilita' dell'input runner, non i gate:

- Phase B resta manuale con `-ApprovePublish`;
- Phase C resta manuale con `-ApproveMerge`;
- `--validate-plan` esegue solo Phase Plan;
- la state machine resta lo step successivo, non un comportamento implicito del generator.
