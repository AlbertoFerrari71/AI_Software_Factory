# Step Closure Report

## 1. Scopo

Lo Step Closure Report e' il report finale ufficiale per chiudere uno step operativo di AI Software Factory.

Serve a distinguere lo stato locale prodotto da Codex dalla chiusura reale dello step su Git, GitHub PR e `main`.

---

## 2. Perche' serve

Nel workflow operativo uno step puo' essere completato localmente da Codex, ma non essere ancora:

- committato sul branch;
- pushato;
- collegato a una PR;
- verificato dai check PR;
- mergiato su `main`;
- verificato dopo `git pull origin main`.

Lo Step Closure Report evita di trattare un lavoro locale come step chiuso. Uno step e' chiuso solo quando `main` contiene il merge o commit dello step e i controlli finali sono passati.

---

## 3. Stati ammessi

Usare uno di questi stati:

- Non iniziato: lo step non e' ancora partito.
- Bloccato da prerequisito: manca il merge o commit richiesto su `main`.
- Completato localmente: Codex ha prodotto modifiche e report sul branch, ma non esiste ancora commit dello step.
- Committato su branch: il lavoro e' stato committato localmente sul branch dedicato.
- Pushato: il branch e' stato pushato su `origin`.
- PR creata: la pull request esiste.
- In attesa check: la PR esiste ma i check non sono ancora conclusi o verificati.
- Mergiato su main: la PR e' stata mergiata, ma manca ancora verifica locale finale su `main`.
- Chiuso e verificato su main: `main` locale e' aggiornato, test finali, Verification Gate e Workflow Health Check sono passati, working tree pulita.
- Non completato: lo step non soddisfa i criteri di chiusura o richiede correzioni.

---

## 4. Report Codex e chiusura reale

Il report Codex non equivale a merge su main.

Il report Codex descrive il lavoro locale svolto sul branch dedicato: file creati, file modificati, test eseguiti, rischi e prossimo step consigliato.

La chiusura reale richiede anche:

- commit dello step;
- push del branch;
- PR creata;
- check PR verificati;
- merge su `main`;
- pull locale di `main`;
- test finali;
- Verification Gate;
- Workflow Health Check;
- `git status --short` pulito;
- log finale di `main`.

Codex non deve fare commit, push, PR o merge. Queste azioni restano di Alberto.

---

## 5. Campi obbligatori del report

Uno Step Closure Report deve includere almeno:

- step eseguito;
- stato;
- branch finale;
- commit step;
- PR;
- merge commit;
- test eseguiti;
- Workflow Health Check;
- Verification Gate;
- `git status --short`;
- ultimo log main;
- file creati/modificati;
- rischi/note;
- vincoli rispettati;
- prossimo step consigliato.

Se un campo non e' ancora disponibile, scrivere `non disponibile` o `non eseguito` e indicare il motivo.

---

## 6. Checks PR non disponibili

Il comando:

```powershell
gh pr checks --watch
```

puo' restituire:

```text
no checks reported on the branch
```

con exit code non zero.

Questo caso va trattato come attenzione da verificare, non come prova automatica di fallimento del codice.

Se i check PR non sono disponibili:

- verificare manualmente la PR su GitHub oppure con altri comandi `gh` read-only;
- proseguire solo se i controlli locali obbligatori sono passati e il contesto del progetto lo consente;
- registrare nel report finale che i check PR non erano disponibili;
- indicare quali verifiche locali hanno compensato l'assenza del dato automatico.

Non ignorare il problema e non dichiarare "check verdi" senza evidenza.

---

## 7. Esempio report finale breve

Esempio per STEP 240:

```text
Step: 240) Workflow Quick Reference
Stato: Chiuso e verificato su main
Branch: step-240-workflow-quick-reference
Commit step: a52c6e8
PR: #23
Merge commit: 8ccdd0e
Main aggiornato: si
Test: python -m pytest PASSED
Workflow Health Check: PASSED
Verification Gate: PASSED
Working tree: git status --short pulito
Ultimo log main: 8ccdd0e Merge pull request #23 ...
Rischi/note: warning CRLF/LF non bloccanti se exit code 0
Prossimo step: 250) Step Closure Report
Frase finale: Step 240 chiuso e verificato su main.
```

---

## 8. Relazione con Lifecycle Checklist

La Prompt Packet Lifecycle Checklist descrive l'intero percorso operativo dallo step al merge:

```text
docs/32_PROMPT_PACKET_LIFECYCLE_CHECKLIST.md
```

Lo Step Closure Report e' il riepilogo finale della parte di chiusura: branch, commit, PR, merge, `main`, test e prossimo step.

---

## 9. Relazione con Workflow Quick Reference

La Workflow Quick Reference contiene i comandi rapidi per eseguire verifiche e handoff:

```text
docs/36_WORKFLOW_QUICK_REFERENCE.md
```

Usarla per recuperare i comandi. Usare questo documento per capire quale stato assegnare allo step e quali evidenze registrare.

Per scenari operativi piu' specifici, inclusi check PR non disponibili, branch remoto assente, working tree sporca su `main` e warning CRLF/LF, usare anche:

```text
docs/38_WORKFLOW_COMMAND_COOKBOOK.md
```

---

## 10. Relazione con Release Readiness

Release Readiness usa Step Closure Report come evidenza quando si valuta se il workflow e' abbastanza controllato per un pilot interno:

```text
docs/40_RELEASE_READINESS.md
```

La readiness non sostituisce la chiusura dello step. Conferma solo se il metodo e' adatto a partire su un progetto pilota con criteri GO, WARNING o NO-GO.

---

## 11. Anti-pattern

- Dichiarare chiuso uno step solo perche' Codex ha finito.
- Ignorare `git status --short`.
- Non verificare `main` dopo merge.
- Non registrare PR, check o merge commit.
- Confondere warning CRLF/LF con fallimento se exit code e' 0.
- Saltare Workflow Health Check.
- Saltare Verification Gate.
- Dichiarare check PR positivi quando `gh pr checks --watch` ha restituito `no checks reported`.
- Avviare lo step successivo senza verificare il log di `main`.
