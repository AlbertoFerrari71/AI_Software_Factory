# AGENTS.md — AI Software Factory

Questo file definisce le regole operative per ChatGPT, Codex CLI, Codex Cloud/Web e futuri agenti software che lavoreranno su questo repository.

---

## 1. Principi generali

- Preferire semplicità, leggibilità e manutenibilità.
- Non generare codice fragile o eccessivamente sofisticato.
- Ogni modifica deve essere piccola, testabile e reversibile.
- Ogni decisione importante deve essere documentata.
- Ogni step deve avere numero progressivo: 010, 020, 030...
- Non saltare direttamente al codice quando mancano obiettivi, vincoli e rischi.
- Distinguere sempre:
  - fatti verificati;
  - ipotesi;
  - stime;
  - rischi;
  - decisioni;
  - punti da validare.

---

## 2. Protocollo FASE 1 / FASE 2

Per richieste complesse usare sempre questo protocollo.

### FASE 1 — Allineamento

Produrre solo:

A) Sintesi dell'obiettivo  
B) Assunzioni numerate da `[100]` in avanti  
C) Domande chiuse A/B/C/D con default A  
D) Criticità, rischi e ottimizzazioni  

Fermarsi.

### FASE 2 — Esecuzione

Procedere solo dopo conferma esplicita di Alberto, per esempio:

- `siamo allineati`
- `via`
- `procedi`
- `ok vai`

---

## 3. Livelli di sicurezza delle azioni

Ogni azione deve essere classificata.

| Livello | Nome | Esempi | Regola |
|---|---|---|---|
| L0 | Read only | Leggere file, leggere repo, leggere log | Può essere automatico |
| L1 | Write safe | Creare bozze, documenti, file temporanei | Può essere automatico con log |
| L2 | Write controlled | Modificare codice su branch dedicato, creare PR | Richiede branch, test e riepilogo |
| L3 | Risky | CI/CD, dipendenze, auth, database, config sensibili | Richiede approvazione esplicita |
| L4 | Destructive | Cancellare dati, force push, merge diretto, deploy prod | Richiede approvazione, dry-run, backup/rollback, conferma doppia |

---

## 4. Regole repository

- Lo stato STEP 020 contiene solo scheletro e documentazione.
- Non introdurre logica applicativa reale prima dello STEP 110, salvo decisione esplicita.
- Non introdurre integrazioni OpenAI API/MCP prima degli step dedicati.
- Non aggiungere dipendenze runtime senza decisione registrata.
- Ogni nuovo modulo deve avere uno scopo chiaro e testabile.

---

## 5. Regole per Codex

Codex deve:

- leggere prima `README.md`, `AGENTS.md`, `docs/10_ROADMAP.md`, `docs/05_SECURITY_MODEL.md` se presente, e il task packet;
- lavorare su branch dedicato;
- modificare solo i file indicati come modificabili;
- dichiarare sempre file modificati, test eseguiti, test non eseguiti e rischi residui;
- fermarsi davanti ad ambiguità che possono causare danni;
- aggiornare la documentazione se cambia comportamento.

Codex non deve:

- fare commit automatico salvo richiesta esplicita;
- fare push automatico salvo richiesta esplicita;
- fare merge;
- fare force push;
- cancellare file o dati senza istruzione esplicita;
- toccare credenziali, secret, configurazioni produzione o database reali;
- introdurre dipendenze senza motivazione;
- risolvere problemi aggirando test o policy.

---

## 6. Regole per GitHub

Workflow standard:

```text
Issue
  ↓
Branch dedicato
  ↓
Modifica piccola
  ↓
Test
  ↓
Commit
  ↓
Pull Request
  ↓
GitHub Actions
  ↓
Review umana
  ↓
Merge
  ↓
Changelog / Roadmap / Decision log
```

Regole:

- Nessun lavoro rilevante senza issue o step.
- Nessuna modifica rilevante direttamente su `main` o `master` dopo il bootstrap.
- Ogni PR deve spiegare cosa cambia, perché, test, rischi e rollback.
- I test falliti bloccano l'avanzamento salvo decisione esplicita documentata.
- Le branch protection rules vanno attivate solo dopo che la CI minima è stabile.

---

## 7. Testing

Ogni task deve indicare:

- test automatici richiesti;
- test manuali se gli automatici non sono disponibili;
- criteri di accettazione;
- cosa significa "completato";
- come fare rollback.

Non dichiarare completato un task non verificato.

Nel repository STEP 020 è presente un test smoke minimale:

```powershell
python -m pytest -q

```

---

## 8. Documentazione viva

Aggiornare la documentazione quando cambia:

- comportamento;
- architettura;
- workflow;
- sicurezza;
- dipendenze;
- API;
- regole Codex/GitHub;
- decisioni operative.

File principali:

- `README.md`
- `AGENTS.md`
- `docs/10_ROADMAP.md`
- `docs/11_DECISIONS.md`
- `CHANGELOG.md`

---

## 9. Stile codice futuro

Quando verrà introdotto codice:

- preferire funzioni piccole;
- nomi chiari;
- moduli separati per responsabilità;
- test vicini al comportamento;
- configurazioni esplicite;
- nessuna magia inutile;
- errori gestiti in modo leggibile.

---

## 10. Anti-obiettivi

Il progetto non deve diventare:

- un generatore incontrollato di codice;
- una piattaforma SaaS prematura;
- una raccolta caotica di prompt;
- un agente con permessi eccessivi;
- un sistema che modifica repository o dati senza controllo umano.
