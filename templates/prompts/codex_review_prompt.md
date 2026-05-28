# Codex Review Prompt

Usa questo prompt quando Codex deve fare review di un diff o di una pull request.

## Obiettivo

Valutare correttezza, semplicita', testabilita', sicurezza, documentazione, rischi e rollback senza modificare file.

## Contesto

AI Software Factory richiede review umana e verifiche prima del merge. La review deve privilegiare bug, regressioni, rischi e test mancanti.

La review deve controllare anche il rispetto di `docs/25_PROMPT_PACKET_HARDENING.md`: allowed scope, forbidden scope, forbidden actions, Verification Gate, Documentation Sync e report finale Codex.

## Livello rischio L0-L4

Livello massimo: L0 - Read only.

Safety level: L0.

Se la review richiede patch, commit, push, merge, modifica CI/CD o cancellazioni, fermarsi in safe stop e chiedere un task L2/L3/L4 separato.

## File da leggere

- diff o pull request da revisionare;
- Codex Task Packet collegato, se presente;
- `AGENTS.md`;
- `docs/05_SECURITY_MODEL.md`;
- test e documentazione collegati alla modifica.

## File modificabili

- Nessuno.

## File vietati / file da non toccare

- `.env`
- `.env.*`
- secret o credenziali
- file fuori repository
- qualunque file non necessario alla review

## Vincoli

- Non modificare file.
- Non fare commit.
- Non fare push.
- Non fare merge.
- Regola sintetica: no commit, no push, no merge.
- Ordinare i finding per severita'.
- Citare file e linee quando disponibili.
- Distinguere problemi bloccanti da suggerimenti.

## Output atteso

1. Findings principali.
2. Domande aperte o assunzioni.
3. Test mancanti o non verificati.
4. Rischi residui.
5. Verdetto: Approva, Richiede modifiche o Blocca.
6. Eventuali violazioni di scope, forbidden actions o report finale.

## Criteri di accettazione

- La review e' read-only.
- I problemi sono concreti e collegati al diff.
- I test mancanti sono esplicitati.
- Il verdetto e' coerente con i rischi.

## Test / verifica

- Verificare il diff.
- Verificare lo stato dei test riportati.
- Se possibile, leggere output CI o test locali senza modificarli.

## Rollback / safe stop

Rollback non necessario per L0. Safe stop se emergono secret, azioni distruttive, modifiche fuori scope, test critici falliti o richiesta di eseguire merge/push.

## Cosa NON fare

## Forbidden actions

- Non applicare fix durante la review.
- Non riscrivere il diff.
- Non approvare se mancano verifiche critiche.
- Non ignorare policy L3/L4.
- Non usare Full Auto.
- Non installare hook Git.
- Non modificare git config core.hooksPath.
- Non usare ASF_ALLOW_MAIN_BYPASS.
