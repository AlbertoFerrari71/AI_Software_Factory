# 0620 - Verification Balance Notes

## 1. Scopo

Questa nota registra una prima analisi tecnica delle verifiche attuali.

Non implementa ancora un selettore automatico. Serve a preparare uno step futuro piu' mirato sui profili di verifica.

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

## 5. Step successivo consigliato

```text
0630) Verification Profile Selector + Test Cost Policy
```

Deliverable proposto:

- profili codificati in un documento operativo o config leggera;
- CLI read-only che suggerisce il profilo in base a file modificati e rischio;
- nessuna esecuzione automatica di publish;
- nessuna riduzione dei gate per `motor-core`, `publish` o `high-risk` senza review umana.
