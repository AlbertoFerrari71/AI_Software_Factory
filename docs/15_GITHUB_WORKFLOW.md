# 15 — GitHub Workflow

## 1. Workflow consigliato

```text
Issue
  ↓
Branch dedicato
  ↓
Modifica piccola
  ↓
Test locali
  ↓
Commit
  ↓
Push
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

---

## 2. Branch naming

Esempi:

```text
020-repo-genesis
030-safety-model
040-prompt-packet-generator
```

---

## 3. Pull request

Ogni PR deve indicare:

- cosa cambia;
- perché;
- step collegato;
- file modificati;
- test eseguiti;
- rischi;
- rollback;
- documentazione aggiornata.

---

## 4. Branch protection

Da attivare dopo verifica della CI:

- require pull request before merging;
- require status checks;
- require conversation resolution;
- disallow force push;
- disallow deletion.

Non configurare automaticamente queste regole nello STEP 020.
