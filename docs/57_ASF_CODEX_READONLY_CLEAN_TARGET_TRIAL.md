# ASF Codex Read-Only Clean Target Trial

## 1. Scopo

Questo documento definisce il trial Codex read-only su target pulito per lo STEP 440.

Il trial verifica che la pipeline possa passare da preview-only a `execute-readonly` quando esistono:

- repo temporanea pulita;
- Human Approval Gate `GO`;
- working tree `CLEAN`;
- comando `codex` disponibile;
- conferma esplicita dello script;
- sandbox read-only.

Il trial resta local-first e non autorizza workspace-write.

---

## 2. Perche' serve un target pulito

Lo STEP 430 ha dimostrato che il flusso preview-only e' corretto quando il gate e' `HOLD` o il target e' dirty.

Lo STEP 440 serve a provare il caso pulito:

- branch target coerente;
- working tree `CLEAN`;
- evidenze sintetiche complete;
- approval gate GO;
- output catturabili dopo una invocazione read-only.

Un target pulito riduce ambiguita' e permette di distinguere un errore Codex da una modifica locale gia' presente.

---

## 3. Perche' usare una repo temporanea sotto tmp/

Il target preferito e':

```text
tmp/asf_clean_target_trial/step_440/clean_repo
```

Questa repo temporanea contiene solo file sintetici:

- `README.md`;
- `docs/NOTES.md`.

La repo temporanea e' ignorata da Git del repository ASF tramite `tmp/`. Non contiene dati reali, non e' un repository esterno e non richiede GitHub.

E' ammesso creare un commit iniziale e un branch locale dentro questa repo temporanea solo per renderla una repo Git valida e pulita. Non fare push.

---

## 4. Prerequisiti

Prima del trial:

- STEP 430 deve essere su `main`;
- branch ASF di lavoro: `step-440-asf-codex-readonly-invocation-clean-target-trial`;
- script 400-420 presenti;
- repo temporanea sotto `tmp/`;
- `tmp/` ignorato da Git;
- nessun target reale esterno coinvolto.

Comandi prerequisito:

```powershell
git switch main
git pull origin main
git --no-pager log --oneline --max-count=15
```

---

## 5. Passaggi del trial

1. Creare repo temporanea sotto `tmp/asf_clean_target_trial/step_440/clean_repo`.
2. Aggiungere solo file sintetici.
3. Creare commit iniziale e branch locale temporaneo, ad esempio `step-440-clean-target-trial`.
4. Creare handoff temporaneo con richiesta esclusivamente read-only.
5. Creare evidenze sintetiche pulite sotto `tmp/`.
6. Generare Human Approval Gate.
7. Procedere solo se approval gate GO.
8. Generare preview con `scripts/asf_codex_readonly_invoke.py --mode preview`.
9. Tentare `execute-readonly` solo se tutte le condizioni sono soddisfatte.
10. Eseguire result capture.
11. Eseguire safety gate.
12. Documentare risultato, rischi e prossimo step.

---

## 6. Condizioni per execute-readonly

Tentare `execute-readonly` solo se:

- `codex` e' disponibile;
- Human Approval Gate e' `GO`;
- approval gate GO e' letto correttamente dallo script;
- repo temporanea e working tree sono `CLEAN`;
- branch target e' coerente;
- `--confirm-readonly-execution YES_I_APPROVE_READONLY_CODEX_EXECUTION` e' presente;
- sandbox resta `read-only`;
- workspace-write non autorizzato;
- danger-full-access non autorizzato;
- nessun commit/push/PR/merge automatico;
- target esterni non modificati.

Se una condizione manca, non forzare. Restare in preview o usare output simulati dichiarati.

---

## 7. Se codex non e' disponibile

Se il comando `codex` non e' disponibile:

- non e' fallimento del trial;
- documentare ambiente non disponibile;
- non simulare una esecuzione reale;
- usare result capture simulato solo se dichiarato;
- riprovare in uno step futuro con CLI disponibile.

---

## 8. Cosa verificare dopo Codex

Dopo `execute-readonly` verificare:

- exit code;
- stdout;
- stderr;
- working tree target dopo l'esecuzione;
- assenza di modifiche file;
- result capture;
- safety gate.

Un exit code `0` non basta per autorizzare step successivi: se stderr e' non vuoto o Codex non riesce a completare l'analisi, il safety gate deve richiedere review.

---

## 9. Perche' workspace-write resta non autorizzato

Questo trial non autorizza workspace-write.

`GO_TO_WORKSPACE_WRITE_DESIGN` autorizzerebbe al massimo la progettazione di uno step futuro separato. In nessun caso questo trial permette modifiche target, commit, push, PR, merge, GitHub API, CI, dipendenze, hook o configurazioni sensibili.

---

## 10. Relazione con STEP 430

STEP 430 ha validato il flusso preview-only quando il gate non era `GO`.

STEP 440 valida il caso clean target: repo temporanea pulita, gate `GO`, preview e tentativo `execute-readonly`. Se l'esecuzione reale non completa l'analisi, lo step resta utile per evidenziare il limite ambientale e bloccare avanzamenti non giustificati.
