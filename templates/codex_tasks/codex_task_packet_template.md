# Codex Task Packet

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

## Livello massimo di rischio ammesso

L0 / L1 / L2 / L3 / L4

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
- altri file specifici

## File modificabili

- ...

## File da NON toccare

- ...

## Vincoli obbligatori

- Non fare commit automatico.
- Non fare push automatico.
- Non fare merge.
- Non modificare file fuori lista.
- Non introdurre nuove dipendenze senza motivazione.
- Aggiornare documentazione se cambia comportamento.

## Step richiesti

1. ...
2. ...
3. ...

## Test da eseguire

```powershell
python -m pytest -q

```

## Criteri di accettazione

- ...
- ...

## Rischi

- ...

## Rollback

Come tornare indietro.

## Output atteso

- Riepilogo modifiche.
- File modificati.
- Test eseguiti.
- Test non eseguiti.
- Rischi residui.
- Prossimo passo consigliato.

## Cosa fare in caso di errore

Fermarsi, spiegare errore, proporre fix.
Non tentare workaround rischiosi.

## Cosa NON fare

- Non toccare branch principale.
- Non cancellare file.
- Non cambiare architettura fuori scope.
- Non modificare credenziali, secret o configurazioni sensibili.
