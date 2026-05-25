# 14 — Repository Genesis

## 1. Obiettivo STEP 020

Creare una struttura repository ordinata, testabile e leggibile da agenti AI e collaboratori umani.

---

## 2. Contenuto creato

- documentazione estesa;
- package Python skeleton;
- test smoke;
- template GitHub;
- template Codex;
- CI minima;
- file ambiente e ignore;
- license placeholder.

---

## 3. Criteri di successo

| Criterio | Stato atteso |
|---|---|
| Repository navigabile | Sì |
| Cartelle principali presenti | Sì |
| CI minima presente | Sì |
| Test smoke presente | Sì |
| Documentazione aggiornata | Sì |
| Logica applicativa reale | No |
| API/database/integrations | No |

---

## 4. Verifica locale

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q

```

---

## 5. Rollback

Lo STEP 020 è reversibile eliminando i file aggiunti o tornando allo ZIP STEP 010.

Nessun dato esterno, repository remoto o servizio è stato modificato.
