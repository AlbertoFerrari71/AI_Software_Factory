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

- puo' usare `--profile` da `config/asf_project_profiles.json`;
- controlla che il repo target esista e contenga `.git`;
- legge il repo target con soli comandi Git read-only;
- rileva branch corrente;
- rileva working tree `CLEAN` o `DIRTY/WARNING`;
- legge gli ultimi commit;
- genera `task_packet.md`;
- genera `codex_handoff.md`;
- genera `runner_report.md`;
- genera `verification_pack.md`;
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
- `codex_handoff.md`: testo pronto da rivedere e copiare manualmente in Codex, con FASE 1 / FASE 2, stato Git, prerequisito, scope, vincoli e note safety.
- `runner_report.md`: report operativo del runner.
- `verification_pack.md`: checklist read-only hardened con controlli prima di Codex, dopo Codex, prima di commit/push/PR/merge manuali e dopo il pull finale di `main`.
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
- non legge automaticamente il report Codex;
- non genera closure pack automaticamente;
- non sostituisce Step Closure Report.

---

## 9. Uso essenziale

Mostrare help:

```powershell
python scripts/asf_next_step.py --help
```

Uso con profilo sul repository AI Software Factory:

```powershell
python scripts/asf_next_step.py --mode prepare --profile AI_Software_Factory --step 340 --title "ASF Runner Verification Pack Hardening" --branch step-340-asf-runner-verification-pack-hardening --objective "Harden verification pack generation for the ASF runner."
```

Aprire il report:

```powershell
Get-Content -Raw .\tmp\asf_next_step\AI_Software_Factory\step_340\runner_report.md
```

---

## 10. Documenti upgrade runner

- `docs/43_ASF_RUNNER_PROJECT_PROFILES.md`
- `docs/44_ASF_RUNNER_CODEX_HANDOFF_IMPROVEMENTS.md`
- `docs/45_ASF_RUNNER_VERIFICATION_PACK.md`
- `docs/46_ASF_RUNNER_VERIFICATION_PACK_HARDENING.md`
- `docs/47_ASF_CODEX_REPORT_INTAKE.md`
- `docs/48_ASF_HUMAN_GATED_CLOSURE_PACK.md`

---

## 11. Prossimi sviluppi

Possibili step futuri:

- 370. ASF Runner Human Approval Gate;
- OpenAI API Adapter in uno step successivo separato.
