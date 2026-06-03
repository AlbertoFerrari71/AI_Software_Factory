# ASF Codex Invocation Design

## 1. Scopo

Questo documento definisce il design della futura invocazione Codex controllata da ASF Runner.

Lo step corrente prepara solo il ponte: Human Approval Gate e dry-run pack. Non invoca Codex, non abilita loop automatici e non modifica repository target.

---

## 2. Livelli di invocazione

| Livello | Nome | Stato |
|---:|---|---|
| Level 0 | Manual handoff | Stato storico: Alberto/ChatGPT copiano manualmente `codex_handoff.md` in Codex. |
| Level 1 | Dry-run command preview | Stato introdotto da questo step: genera preview testuale del comando. |
| Level 2 | Read-only Codex analysis | Prototipo futuro: Codex analizza in sandbox read-only e produce report. |
| Level 3 | Workspace-write Codex execution | Futuro: esecuzione `workspace-write` solo human-approved e su branch dedicato. |
| Level 4 | Supervised loop multi-step | Futuro avanzato: cicli multi-step con stop condition e review umana tra i passaggi. |
| Level 5 | Full automation | Non autorizzata ora. Richiederebbe policy, audit, sandbox dedicata e gate separati. |

Il livello attivo dopo questo step e' Level 1.

---

## 3. Codex exec

La futura invocazione potra' basarsi su `codex exec`.

In questo step:

- `codex exec` puo' comparire solo come testo di preview;
- il comando non viene eseguito;
- lo script Python non chiama Codex tramite subprocess;
- la sintassi della preview resta da verificare manualmente nel prossimo prototipo read-only.

---

## 4. Sandbox modes

Regole previste:

- `read-only`: default per analisi e prototipo iniziale.
- `workspace-write`: solo in futuro, con Human Approval Gate favorevole, branch coerente, working tree compresa e scope stretto.
- `danger-full-access`: vietato salvo ambiente isolato futuro e gate separato.

Lo script dry-run accetta solo:

- `read-only`;
- `workspace-write-preview`.

`workspace-write-preview` e' un nome prudente per indicare che il comando futuro userebbe `workspace-write`, ma in questo step resta preview non eseguita.

---

## 5. Input futuri

Una futura invocazione controllata deve usare:

- `codex_handoff.md`;
- `task_packet.md`;
- `verification_pack.md`;
- profilo progetto;
- `human_approval_gate.md`;
- stato Git target letto in modo read-only.

Questi input devono essere revisionati da Alberto/ChatGPT prima dell'esecuzione.

---

## 6. Output futuri

Una futura invocazione dovra' produrre:

- Codex report;
- eventuali file modificati nel repo target, solo se autorizzati dal livello scelto;
- log stdout/stderr;
- exit code;
- structured result futuro, se disponibile.

Gli output devono restare verificabili e collegati allo Step Closure Report.

---

## 7. Stop conditions

Bloccare o non eseguire Codex se:

- Human Approval Gate e' `HOLD` o `NO-GO`;
- repo target dirty non ammessa;
- branch non coerente;
- task packet non e' Strict PASS;
- scope troppo ampio;
- file sensibili, secret o `.env` sono coinvolti;
- profilo progetto mancante;
- comando Codex non verificato;
- serve un livello L3/L4 non approvato;
- rollback non chiaro.

---

## 8. Non autorizzazioni

Questo step non:

- invoca Codex;
- crea loop automatico;
- abilita commit, push, PR o merge automatici;
- cambia permessi;
- modifica repository target;
- modifica GitHub;
- modifica CI;
- installa hook;
- modifica `core.hooksPath`;
- modifica dipendenze.

---

## 9. Prossimo step futuro

Prossimo step consigliato:

```text
400) ASF Codex Invocation Read-Only Prototype
```

Motivo: prima di qualunque `workspace-write`, il primo prototipo deve dimostrare che ASF Runner puo' preparare ed eventualmente lanciare solo analisi read-only, registrando comando, log, exit code e report senza modificare il repository target.
