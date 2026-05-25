# Codex Repair Prompt

## Contesto

Un task precedente ha prodotto errore, test falliti o comportamento non conforme.

## Obiettivo

Correggere il problema minimo necessario senza cambiare architettura fuori scope.

## Regole

- Prima spiegare la causa probabile.
- Modificare solo i file necessari.
- Non introdurre nuove dipendenze salvo necessità motivata.
- Eseguire i test falliti.
- Non cancellare codice senza spiegazione.
- Non fare commit/push/merge.

## Output richiesto

1. Causa probabile.
2. Fix applicato.
3. File modificati.
4. Test eseguiti.
5. Esito.
6. Rischi residui.
