# 16 — Approval Policy

## 1. Scopo

Questo documento definisce come Alberto o un futuro utente approvano azioni eseguite da AI Software Factory, Codex, GitHub integration, OpenAI API adapter, MCP o altri tool.

La regola base è semplice:

> Più un'azione è rischiosa o irreversibile, più l'approvazione deve essere esplicita, informata e verificabile.

---

## 2. Livelli di approvazione

| Livello | Tipo approvazione | Esempio |
|---|---|---|
| L0 | automatica | lettura documenti |
| L1 | automatica con log | generazione bozza Markdown |
| L2 | task/branch approvato | modifica codice su branch dedicato |
| L3 | approvazione esplicita | modifica CI/CD o dipendenze |
| L4 | approvazione + doppia conferma | cancellazione dati, force push, deploy produzione |

---

## 3. Formule di approvazione

### L2

Per L2 è sufficiente un'approvazione operativa collegata a task e branch:

```text
procedi con 040
```

oppure:

```text
approvo il Codex Task Packet ASF-040-...
```

### L3

Per L3 serve una frase esplicita:

```text
approvo azione L3: modifica workflow CI sul branch 050-github-workflow
```

### L4

Per L4 servono due passaggi separati:

```text
approvo azione L4: cancellazione controllata dei file indicati nel dry-run
```

poi, dopo aver letto dry-run e rollback:

```text
confermo definitivamente L4
```

Senza seconda conferma, l'azione non si esegue.

---

## 4. Approval Request obbligatoria per L3/L4

Ogni richiesta L3/L4 deve includere:

- task ID;
- livello richiesto;
- obiettivo;
- tool coinvolti;
- branch;
- file/dati coinvolti;
- motivazione;
- alternative meno rischiose;
- dry-run;
- test previsti;
- rollback plan;
- impatto se fallisce;
- criterio di stop;
- frase esatta di approvazione.

---

## 5. Azioni non approvabili nel MVP

Nel MVP personale/local-first sono bloccate di default:

- deploy produzione reale;
- modifica database reale in scrittura;
- cancellazione dati utente reali;
- rotazione credenziali reali;
- accesso automatico a sistemi aziendali non sandbox;
- uso di MCP server non fidati con tool write;
- modifiche fuori repository.

Queste azioni potranno essere trattate solo in fasi future, con sandbox, audit log, backup e procedure dedicate.

---

## 6. Revoca e stop

L'utente può fermare un'azione in qualsiasi momento usando:

```text
stop
```

oppure:

```text
annulla questo step
```

Dopo uno stop:

- nessuna ulteriore modifica deve essere proposta come già approvata;
- si deve produrre riepilogo dello stato;
- si deve indicare se esistono file modificati;
- si deve proporre rollback o conservazione delle modifiche.
