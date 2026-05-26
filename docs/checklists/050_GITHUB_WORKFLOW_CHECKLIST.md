# 050 — GitHub Workflow Checklist

## 1. Scope

Checklist per verificare che lo STEP 050 renda il workflow GitHub chiaro, tracciabile e sicuro.

---

## 2. Documentazione

- [ ] `docs/15_GITHUB_WORKFLOW.md` descrive issue policy.
- [ ] `docs/15_GITHUB_WORKFLOW.md` descrive branch naming policy.
- [ ] `docs/15_GITHUB_WORKFLOW.md` descrive commit policy.
- [ ] `docs/15_GITHUB_WORKFLOW.md` descrive PR policy.
- [ ] `docs/15_GITHUB_WORKFLOW.md` descrive merge policy.
- [ ] `docs/15_GITHUB_WORKFLOW.md` descrive branch protection checklist.
- [ ] `docs/15_GITHUB_WORKFLOW.md` descrive release/tag policy.

---

## 3. File GitHub

- [ ] `.github/pull_request_template.md` presente.
- [ ] `.github/ISSUE_TEMPLATE/feature.yml` presente.
- [ ] `.github/ISSUE_TEMPLATE/bug.yml` presente.
- [ ] `.github/ISSUE_TEMPLATE/research.yml` presente.
- [ ] `.github/ISSUE_TEMPLATE/config.yml` presente.
- [ ] `.github/workflows/ci.yml` presente.

---

## 4. Sicurezza

- [ ] Nessuna modifica automatica a branch protection.
- [ ] Nessuna modifica automatica alla CI nello STEP 050.
- [ ] Nessuna modifica a policy L0-L4.
- [ ] Nessuna modifica a `src/**`.
- [ ] Nessuna nuova dipendenza.

---

## 5. Verifica

Comandi minimi:

```powershell
python -m pytest -q
git diff --check

```

---

## 6. Criterio di completamento

STEP 050 è completato quando:

- il workflow GitHub è documentato;
- i template GitHub sono presenti;
- i test automatici verificano i file minimi;
- roadmap, changelog e TREE sono aggiornati;
- la PR verso `main` è aperta;
- il merge non è stato eseguito automaticamente.
