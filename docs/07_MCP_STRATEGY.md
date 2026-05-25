# 07 — MCP Strategy

## 1. Stato

MCP non viene implementato nello STEP 030.

Viene considerato un layer di estensione futuro, subordinato alla policy L0-L4 e ad approval esplicita per tool sensibili.

---

## 2. Ruolo di MCP nel framework

MCP potrà collegare il framework a:

- filesystem;
- GitHub;
- database;
- browser;
- documenti;
- sistemi aziendali;
- strumenti di sviluppo;
- servizi esterni.

---

## 3. Regola fondamentale

Nessun tool MCP deve essere disponibile senza:

- classificazione L0-L4;
- descrizione permessi;
- allowlist;
- log;
- approval policy;
- fallback manuale;
- disabilitazione rapida.

---

## 4. Strategia iniziale

Ordine consigliato:

1. tool read-only;
2. tool write-safe;
3. tool write-controlled su branch o sandbox;
4. tool risky solo con approvazione;
5. tool destructive preferibilmente esclusi o disabilitati di default.

---

## 5. Rischi principali

- prompt injection da contenuti esterni;
- tool poisoning;
- privilege escalation;
- token/secret exposure;
- operazioni non reversibili;
- fiducia eccessiva nei risultati del tool.
