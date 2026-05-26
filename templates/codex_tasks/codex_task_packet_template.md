# Codex Task Packet Template

## Task ID

ASF-XXX

## Titolo

Titolo breve e preciso.

## Obiettivo

Cosa deve ottenere il task.

## Contesto

Perché serve questo task.
Stato attuale del progetto.
Decisioni già prese.

## Branch consigliato

xxx-nome-breve-task

## Livello rischio L0-L4

Livello massimo ammesso: L0 / L1 / L2 / L3 / L4.

Safety level: indicare il livello massimo approvato e il motivo.

Motivazione della classificazione:

- ...

## Modalità Codex consigliata

A) Ask only  
B) Suggest  
C) Auto Edit  
D) Full Auto sandboxed  

Default: B

## File da leggere prima

- `README.md`
- `AGENTS.md`
- `docs/10_ROADMAP.md`
- `docs/05_SECURITY_MODEL.md`
- altri file specifici

## File modificabili

- ...

## File vietati

File da non toccare:

- `.env`
- `.env.*`
- secret o credenziali
- file fuori repository
- ...

## Vincoli obbligatori

- Non fare commit automatico.
- Non fare push automatico.
- Non fare merge.
- Regola sintetica: no commit, no push, no merge.
- Non modificare file fuori lista.
- Non introdurre nuove dipendenze senza motivazione.
- Aggiornare documentazione se cambia comportamento.
- Fermarsi se il task richiede un livello superiore a quello approvato.

## Step richiesti

010. ...
020. ...
030. ...

## Output atteso

- Riepilogo modifiche.
- File modificati.
- Test eseguiti.
- Test non eseguiti.
- Rischi residui.
- Rollback consigliato.
- Prossimo passo consigliato.

## Criteri di accettazione

- ...
- ...

## Test / verifica

```powershell
python -m pytest -q

```

## Rischi

- ...

## Rollback / safe stop

Come tornare indietro.

Safe stop se:

- compaiono file fuori scope;
- compaiono secret;
- falliscono test critici;
- serve L3/L4 non approvato;
- il rollback non e' chiaro.

## Cosa fare in caso di errore

Fermarsi, spiegare errore, proporre fix.
Non tentare workaround rischiosi.

## Cosa NON fare

- Non toccare branch principale.
- Non cancellare file.
- Non cambiare architettura fuori scope.
- Non modificare credenziali, secret o configurazioni sensibili.
- Non modificare CI/CD, dipendenze, auth, database o security policy senza approval L3.
