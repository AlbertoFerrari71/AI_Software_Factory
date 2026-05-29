# ASF Runner Project Profiles

## 1. Scopo

I project profiles riducono gli argomenti ripetitivi di `scripts/asf_next_step.py`.

Un profilo descrive un progetto target con nome, cartella locale, branch principale, comando test, note safety e file consigliati da ispezionare. Il runner resta local-first, standard library only e read-only verso il repository target.

---

## 2. Configurazione

Il file dei profili e':

```text
config/asf_project_profiles.json
```

La struttura e' JSON standard:

```json
{
  "profiles": {
    "AI_Software_Factory": {
      "project_name": "AI_Software_Factory",
      "repo_path": "C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory",
      "main_branch": "main",
      "test_command": "python -m pytest",
      "health_command": "python scripts/check_workflow_health.py",
      "notes": [
        "Local-first framework repository.",
        "Do not bypass human gate."
      ]
    }
  }
}
```

Il runner carica il file solo quando viene passato `--profile`.

---

## 3. Profili inclusi

Profili iniziali:

- `AI_Software_Factory`: repository del framework, con test `python -m pytest` e health check locale.
- `Family_Photo_Organizer`: progetto pilota safety-first, con note per evitare operazioni fisiche su archivi reali.

Il profilo Family Photo Organizer include anche file consigliati per ispezione, come README, roadmap, decisioni e policy safety del progetto.

---

## 4. Uso base

Esempio:

```powershell
python scripts/asf_next_step.py --mode prepare --profile Family_Photo_Organizer --step 590 --title "Sandbox Import Static Simulation Prototype" --branch 590-sandbox-import-static-simulation-prototype --objective "Prepare a static/demo sandbox import simulation prototype."
```

Il profilo fornisce:

- project-name;
- repo-path;
- main-branch;
- test command;
- note safety;
- file consigliati da ispezionare.

---

## 5. Override manuale

Gli argomenti espliciti sovrascrivono i valori del profilo quando e' utile:

```powershell
python scripts/asf_next_step.py --mode prepare --profile AI_Software_Factory --repo-path . --step 340 --title "ASF Runner Verification Pack Hardening" --branch step-340-asf-runner-verification-pack-hardening --objective "Harden verification pack generation for the ASF runner."
```

Questo permette di usare un profilo stabile ma correggere temporaneamente path o branch principale senza modificare il JSON.

---

## 6. Errori gestiti

Il runner fallisce con messaggio chiaro quando:

- il profilo non esiste;
- `config/asf_project_profiles.json` manca;
- il JSON e' malformato;
- il profilo non contiene `project_name` o `repo_path`;
- `repo-path` non esiste o non contiene `.git`.

---

## 7. Sicurezza

I profili non autorizzano azioni aggiuntive.

Il runner continua a non:

- invocare Codex;
- modificare repository target;
- creare branch nel repository target;
- fare commit, push, PR o merge;
- modificare GitHub;
- modificare CI, dipendenze, secret o `.env`.

Le note safety dei profili vengono riportate nel task packet e nell'handoff, ma non sostituiscono review Alberto/ChatGPT.

---

## 8. Limiti

Limiti attuali:

- nessun discovery automatico di tutti i progetti;
- nessuna scelta automatica dello step;
- nessuna validazione semantica profonda del profilo;
- nessuna scrittura cross-repository;
- nessuna integrazione con GitHub API.

