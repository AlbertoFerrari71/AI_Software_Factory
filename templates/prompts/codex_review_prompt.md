# Codex Review Prompt

Lavora in modalità review.

## Obiettivo

Analizza il diff o la pull request e valuta:

- correttezza;
- semplicità;
- testabilità;
- sicurezza;
- documentazione;
- rischi;
- rollback.

## Vincoli

- Non modificare file.
- Non fare commit.
- Non fare push.
- Non fare merge.

## Output richiesto

1. Sintesi della modifica.
2. Punti corretti.
3. Problemi trovati.
4. Rischi.
5. Test mancanti.
6. Suggerimenti minimi per migliorare.
7. Verdetto:
   - Approva
   - Richiede modifiche
   - Blocca
