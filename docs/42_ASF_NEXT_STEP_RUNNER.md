# ASF Next Step Runner

## 1. Scopo

ASF Next Step Runner velocizza la preparazione dello step successivo del workflow AI Software Factory.

Il runner non sostituisce ChatGPT, Codex, test, review umana, PR, merge o Step Closure Report. Serve a preparare un handoff locale piu' ordinato mantenendo FASE 1 / FASE 2, Human gate, Git e controllo umano.

---

## 2. Perche' serve

Il workflow manuale ChatGPT -> Codex -> Git -> PR -> merge richiede molti passaggi ripetitivi:

- leggere lo stato Git del progetto target;
- copiare step, titolo, branch e obiettivo;
- creare un task packet;
- validarlo in Lite e Strict;
- preparare un handoff chiaro per Codex;
- ricordare i vincoli no commit, no push, no PR e no merge.

Il runner riduce copia/incolla e dimenticanze, ma non salta i gate umani. Il task packet generato resta una bozza da rivedere.

---

## 3. Livelli di automazione

| Livello | Nome | Stato |
|---|---|---|
| 1 | Workflow manuale guidato | Documenti, template, checklist e comandi manuali. |
| 2 | prepare runner | STEP 300: prepara task packet, handoff e report senza modificare il repo target. |
| 3 | Codex-assisted runner futuro | Possibile evoluzione con handoff piu' ricco, sempre con Human gate. |
| 4 | Automazione completa | automazione completa non autorizzata ora. |

Il livello attuale e' il Livello 2, chiamato `prepare mode`.

---

## 4. Cosa fa ora

In `prepare mode`, `scripts/asf_next_step.py`:

- controlla che il repo target esista e contenga `.git`;
- legge il repo target con soli comandi Git read-only;
- rileva branch corrente;
- rileva working tree `CLEAN` o `DIRTY/WARNING`;
- legge gli ultimi commit;
- genera `task_packet.md`;
- genera `codex_handoff.md`;
- genera `runner_report.md`;
- valida il task packet in Lite Mode;
- valida il task packet in Strict Mode quando `--strict-ready` e' attivo;
- indica il prossimo comando consigliato.

Gli output predefiniti sono sotto:

```text
tmp/asf_next_step/<project-name>/step_<step>/
```

`tmp/` e' ignorato da Git.

---

## 5. Cosa non fa ora

Il runner non:

- invoca Codex;
- modifica il repository target;
- crea branch nel repository target;
- fa commit;
- fa push;
- crea PR;
- fa merge;
- modifica GitHub;
- crea GitHub Release;
- installa hook Git;
- modifica `core.hooksPath`;
- modifica CI;
- integra nuovi check in CI.

Se la working tree target e' sporca, il runner non fallisce automaticamente. Registra `DIRTY/WARNING` e richiede decisione umana.

---

## 6. Esempio Family Photo Organizer

Esempio PowerShell:

```powershell
python scripts/asf_next_step.py --mode prepare --project-name Family_Photo_Organizer --repo-path "C:\Users\alberto.ferrari\source\repos\Family_Photo_Organizer" --main-branch main --step 580 --title "Sandbox Import Static Simulation Prototype Decision Gate" --branch 580-sandbox-import-static-simulation-prototype-decision-gate --objective "Prepare the decision gate for a static sandbox import simulation prototype." --strict-ready
```

Parametri principali:

- project-name: `Family_Photo_Organizer`;
- repo-path: `C:\Users\alberto.ferrari\source\repos\Family_Photo_Organizer`;
- step: `580`;
- title: `Sandbox Import Static Simulation Prototype Decision Gate`;
- branch: `580-sandbox-import-static-simulation-prototype-decision-gate`.

---

## 7. Interpretazione output

- `CLEAN`: `git status --short` non ha restituito righe.
- `DIRTY/WARNING`: il repository target ha modifiche locali o file non tracciati; Alberto deve decidere se proseguire.
- `task_packet.md`: task packet generato e validato.
- `codex_handoff.md`: testo pronto da copiare manualmente in Codex.
- `runner_report.md`: report operativo del runner.
- `Lite PASS`: il task packet passa `scripts/validate_task_packet.py`.
- `Strict PASS`: il task packet passa `scripts/validate_task_packet.py --strict`.

Un PASS tecnico non sostituisce review ChatGPT/Alberto.

---

## 8. Limiti attuali

Il runner:

- non capisce automaticamente tutta la roadmap;
- non sceglie da solo lo step;
- non invoca Codex;
- non integra CI;
- non fa cross-repo writes;
- non garantisce correttezza semantica del task packet senza review ChatGPT/Alberto;
- non decide se un `DIRTY/WARNING` e' accettabile;
- non sostituisce Step Closure Report.

---

## 9. Uso essenziale

Mostrare help:

```powershell
python scripts/asf_next_step.py --help
```

Prova locale sul repository AI Software Factory:

```powershell
python scripts/asf_next_step.py --mode prepare --project-name AI_Software_Factory --repo-path . --main-branch main --step 310 --title "ASF Next Step Runner Project Profiles" --branch step-310-asf-next-step-runner-project-profiles --objective "Add project profiles for ASF Next Step Runner." --strict-ready
```

Aprire il report:

```powershell
Get-Content -Raw .\tmp\asf_next_step\AI_Software_Factory\step_310\runner_report.md
```

---

## 10. Prossimi sviluppi

Possibili step futuri:

- 310. ASF Next Step Runner Project Profiles;
- 320. ASF Runner Codex Handoff Improvements;
- 330. ASF Runner Verification Pack.

