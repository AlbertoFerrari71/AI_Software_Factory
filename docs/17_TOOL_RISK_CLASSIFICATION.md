# 17 — Tool Risk Classification

## 1. Scopo

Questo documento classifica i tool che AI Software Factory potrà usare direttamente o indirettamente.

La classificazione è conservativa: in caso di dubbio si sale di livello.

---

## 2. Matrice tool

| Tool | Azione | Livello default | Controllo |
|---|---|---:|---|
| ChatGPT | ragionamento, piano, template | L0-L1 | nessuna modifica esterna |
| File reader | leggere file repo | L0 | log |
| File writer | creare nuovo Markdown in `docs/` | L1 | path policy |
| File writer | modificare codice in `src/` | L2 | branch + test |
| File writer | cancellare file | L4 | dry-run + doppia conferma |
| Codex CLI ASK | analisi repository | L0 | no edit |
| Codex CLI Auto Edit | patch controllata | L2 | branch + test + diff |
| Codex CLI Full Auto | task sandbox | L1 | solo sandbox, no dati reali |
| Codex Cloud/Web | modifica branch e PR | L2 | PR + CI + review |
| GitHub API | leggere issue/PR/status | L0 | log |
| GitHub API | creare issue draft | L1 | template |
| GitHub API | creare branch/PR | L2 | issue/task collegato |
| GitHub API | configurare branch protection | L3 | approval |
| GitHub API | merge diretto | L4 | vietato salvo doppia conferma |
| GitHub API | force push/delete branch remoto | L4 | vietato salvo emergenza documentata |
| GitHub Actions | eseguire CI | L0-L2 | automatico su PR |
| GitHub Actions | modificare workflow | L3 | approval |
| OpenAI Responses API | generare JSON strutturato | L0-L1 | schema + validazione |
| OpenAI Responses API | tool/function calling read-only | L0-L1 | allowlist |
| OpenAI Responses API | tool write | L2-L4 | dipende da tool |
| MCP ufficiale read-only | leggere documentazione/dati | L0-L1 | approval se passa dati utente |
| MCP terzo read-only | leggere dati | L2-L3 | fiducia server da valutare |
| MCP write | modificare servizi esterni | L3-L4 | approval obbligatoria |
| Database locale sandbox | leggere | L1-L2 | dati non sensibili |
| Database reale | leggere | L3 | approvazione e scopo |
| Database reale | scrivere/modificare | L4 | fuori automazione MVP |
| Browser/web | cercare documentazione | L0 | citare fonti |
| Shell locale | comandi read-only | L0-L1 | path limitato |
| Shell locale | test/lint/build | L2 | branch/worktree |
| Shell locale | rm/delete/move distruttivo | L4 | dry-run + backup |

---

## 3. Escalation automatica

Un'azione sale automaticamente a L3 se:

- modifica CI/CD;
- modifica dipendenze;
- modifica auth;
- modifica security policy;
- modifica schema database;
- usa tool remoto non ufficiale;
- legge dati sensibili;
- non è chiaro l'impatto.

Un'azione sale automaticamente a L4 se:

- cancella dati;
- modifica produzione;
- fa force push;
- fa merge diretto su branch principale;
- ruota credenziali;
- modifica database reale;
- cambia permessi o ruoli di accesso.

---

## 4. Regola per nuovi tool

Ogni nuovo tool deve essere registrato prima dell'uso con:

- nome;
- scopo;
- operazioni disponibili;
- dati accessibili;
- livello massimo;
- modalità approval;
- log richiesti;
- rollback possibile;
- owner umano.

Se un tool non è registrato, il suo uso operativo è bloccato o trattato come L3.
