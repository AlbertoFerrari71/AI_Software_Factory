# ASF Codex Invocation Design

## 1. Scopo

Questo documento definisce il design della futura invocazione Codex controllata da ASF Runner.

Gli step 370-390 hanno preparato il ponte: Human Approval Gate e dry-run pack. Il pack 400-420 aggiunge il primo prototipo read-only human-approved, result capture e safety gate. Non abilita loop automatici e non autorizza modifiche workspace-write.

---

## 2. Livelli di invocazione

| Livello | Nome | Stato |
|---:|---|---|
| Level 0 | Manual handoff | Stato storico: Alberto/ChatGPT copiano manualmente `codex_handoff.md` in Codex. |
| Level 1 | Dry-run command preview | Stato introdotto da questo step: genera preview testuale del comando. |
| Level 2 | Read-only Codex analysis | Stato introdotto dal pack 400-420: default preview, execute-readonly solo con gate GO e conferma esplicita. |
| Level 3 | Workspace-write Codex execution | Futuro: esecuzione `workspace-write` solo human-approved e su branch dedicato. |
| Level 4 | Supervised loop multi-step | Futuro avanzato: cicli multi-step con stop condition e review umana tra i passaggi. |
| Level 5 | Full automation | Non autorizzata ora. Richiederebbe policy, audit, sandbox dedicata e gate separati. |

Il livello attivo dopo il pack 400-420 e gli step 430-440 e' Level 2, limitato alla sandbox read-only e senza autorizzazione a workspace-write.

---

## 3. Codex exec

La futura invocazione potra' basarsi su `codex exec`.

Nel dry-run pack:

- `codex exec` puo' comparire solo come testo di preview;
- il comando non viene eseguito;
- lo script Python non chiama Codex tramite subprocess;
- la sintassi della preview resta verificabile prima del prototipo read-only.

Nel prototipo read-only:

- `codex exec` puo' essere eseguito solo in `execute-readonly`;
- serve conferma `YES_I_APPROVE_READONLY_CODEX_EXECUTION`;
- serve Human Approval Gate `GO`;
- serve working tree target `CLEAN`;
- stdout, stderr, exit code e report vengono salvati sotto `tmp/`.

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

Una invocazione read-only deve produrre:

- log stdout/stderr;
- exit code;
- report di invocazione;
- result capture;
- safety gate.

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
450) ASF Codex Read-Only Invocation Repeatable Trial Pack
```

Motivo: il clean target trial ha eseguito Codex read-only con exit code `0` e target `CLEAN`, ma il safety gate finale e' `WARNING_REVIEW_REQUIRED` per stderr non vuoto e output incompleto. Prima di qualunque `workspace-write`, serve rendere il trial ripetibile e chiarire il comportamento ambientale.
