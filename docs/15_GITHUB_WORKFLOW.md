# 15 — GitHub Workflow

## 1. Obiettivo dello STEP 050

Lo STEP 050 standardizza il modo in cui AI Software Factory usa GitHub per trasformare ogni lavoro in una sequenza tracciabile, verificabile e reversibile.

Il workflow GitHub non deve essere solo una convenzione informale: deve diventare un gate operativo tra idea, task, modifica, test, review e merge.

Principio guida:

```text
Nessuna modifica rilevante deve arrivare su main senza branch, test, PR e review umana.
```

---

## 2. Workflow standard

```text
Issue / Step
  ↓
Branch dedicato
  ↓
Modifica piccola e isolata
  ↓
Test locali
  ↓
Commit
  ↓
Push branch
  ↓
Pull Request verso main
  ↓
GitHub Actions
  ↓
Review umana
  ↓
Merge
  ↓
Pull locale su main
  ↓
Test locale finale
  ↓
Changelog / Roadmap / Decision log
```

Ogni passaggio deve lasciare una traccia leggibile.

---

## 3. Issue policy

### Quando creare una issue

Creare una issue per:

- ogni step numerato della roadmap;
- bug o regressioni;
- ricerche tecniche prima di una decisione;
- modifiche che toccano più file;
- modifiche L2 o superiori.

Non è obbligatoria per micro-correzioni L0/L1 senza impatto sul progetto.

### Issue minima

Ogni issue deve indicare:

- step collegato;
- obiettivo;
- scope incluso;
- scope escluso;
- livello massimo di rischio L0-L4;
- file probabilmente coinvolti;
- criteri di accettazione;
- test richiesti;
- rollback o safe stop.

---

## 4. Branch naming policy

Formato consigliato:

```text
NNN-nome-breve-kebab-case
```

Esempi:

```text
040-prompt-packet-generator
050-github-workflow
060-codex-workflow
```

Regole:

- usare il numero step quando esiste;
- evitare branch generici tipo `fix`, `test`, `update`;
- un branch deve contenere un solo obiettivo principale;
- non lavorare direttamente su `main` dopo il bootstrap;
- eliminare o archiviare branch completati dopo il merge, se non servono più.

---

## 5. Commit policy

Un commit deve essere:

- leggibile;
- coerente con lo step;
- abbastanza piccolo da essere revisionabile;
- accompagnato da test o motivazione se i test non sono disponibili.

Formato consigliato:

```text
Add STEP 050 GitHub workflow policy
Fix STEP 040 prompt template smoke tests
Update safety checklist wording
```

Evitare messaggi vaghi:

```text
update
changes
fix stuff
primo
```

---

## 6. Pull Request policy

La PR è il punto di controllo umano prima del merge.

Ogni PR deve contenere:

- cosa cambia;
- perché;
- step o issue collegata;
- file modificati;
- safety level L0-L4;
- test eseguiti;
- test non eseguiti;
- documentazione aggiornata;
- rischi residui;
- rollback.

### Regola operativa

```text
Aprire PR prima del merge.
Non mergiare finché test e review non sono stati verificati.
```

Eccezione: solo bootstrap iniziali o emergenze documentate.

---

## 7. GitHub Actions e status check

La CI minima deve almeno eseguire:

```powershell
python -m pytest -q

```

Per gli step futuri, la CI potrà essere estesa con:

- lint;
- type check;
- security scan;
- markdown check;
- verifica template;
- verifica policy.

Nello STEP 050 non vengono modificate le GitHub Actions. Lo STEP 070 sarà il punto corretto per ampliare il Verification Gate.

---

## 8. Branch protection checklist

Da valutare manualmente su GitHub quando la CI è stabile:

- [ ] require pull request before merging;
- [ ] require approvals;
- [ ] require status checks to pass;
- [ ] require branches to be up to date before merging;
- [ ] require conversation resolution;
- [ ] disallow force push;
- [ ] disallow branch deletion;
- [ ] restrict direct pushes to `main`.

Queste impostazioni sono L3 se applicate automaticamente da tool, perché modificano regole del repository. In questo step sono solo documentate.

---

## 9. Merge policy

Merge ammesso solo quando:

- branch dedicato presente;
- PR aperta;
- diff revisionato;
- test locali passati o motivazione documentata;
- CI GitHub verificata quando disponibile;
- documentazione aggiornata;
- rollback chiaro;
- Alberto approva il merge.

Dopo il merge:

```powershell
git checkout main
git pull origin main
python -m pytest -q
git status

```

---

## 10. Release e tag policy

Per ora non creare tag ad ogni step.

Creare tag solo per milestone stabili, per esempio:

```text
v0.1-method-baseline
v0.2-local-orchestrator-mvp
v1.0-public-method
```

Ogni release/tag deve avere:

- changelog;
- stato test;
- contenuto incluso;
- rischi noti;
- rollback o restore point.

---

## 11. Regole anti-errore

Non fare:

- merge prima di avere test verdi;
- commit diretto su `main` dopo il bootstrap;
- force push;
- PR troppo grandi;
- modifiche miste non correlate;
- cambi CI/CD insieme a logica applicativa;
- aggiornamenti dipendenze dentro step non dedicati;
- merge se non è chiaro il rollback.

---

## 12. Decisioni STEP 050

### DEC-024 — PR come Human Approval Gate

La Pull Request è il gate standard prima del merge su `main`.

Conseguenza: ogni step L2 o superiore deve passare da PR salvo eccezione documentata.

### DEC-025 — Branch naming per step

I branch operativi seguono il formato `NNN-nome-breve-kebab-case`.

Conseguenza: branch e roadmap restano leggibili e collegabili.

### DEC-026 — Branch protection documentata, non applicata automaticamente

Le branch protection rule vengono documentate nello STEP 050, ma non applicate automaticamente.

Conseguenza: l'applicazione automatica resta un'azione L3 da approvare in uno step futuro.

---

## 13. Stato STEP 050

STEP 050 è completato quando:

- questo documento è presente e aggiornato;
- la checklist 050 è presente;
- issue/PR/branch policy sono descritte;
- i test verificano la struttura GitHub minima;
- roadmap, changelog e TREE sono aggiornati;
- la PR viene aperta verso `main`, senza merge automatico.
