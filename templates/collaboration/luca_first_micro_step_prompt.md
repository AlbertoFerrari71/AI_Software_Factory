# Primo micro-step controllato Luca - Read-only

## Scopo

[F] Questo prompt serve a verificare che Luca possa lavorare sul repository senza modifiche operative rischiose.

[S] Il prompt e' read-only/quasi read-only: puo' creare solo un report locale o Bridge se Alberto indica il path.

[O] Usarlo prima di autorizzare micro-step con commit/PR.

## Prompt da usare

Esegui un micro-step read-only nel repository corrente.

Vincoli:

- [F] Non fare commit.
- [F] Non fare push.
- [F] Non aprire PR.
- [F] Non fare merge.
- [F] Non fare rebase, reset, clean o force-push.
- [F] Non modificare permessi GitHub, branch protection, Organization o secrets.
- [F] Non usare clipboard.
- [F] Non leggere o stampare segreti.
- [F] Non modificare file del repository, salvo un report se il path e' esplicitamente autorizzato.

Verifiche richieste:

1. [F] Verifica path repository con `git rev-parse --show-toplevel`.
2. [F] Verifica branch corrente con `git branch --show-current`.
3. [F] Verifica working tree con `git status --short`.
4. [F] Verifica presenza `AGENTS.md`.
5. [F] Verifica presenza skills locali se esiste `repo/.agents/skills`.
6. [F] Verifica presenza documenti collaboration se esistono.
7. [F] Esegui eventuale script read-only `scripts/collaboration/Test-CollaborationReadiness.ps1`, se presente.
8. [F] Produci report con PASS/WARN/FAIL e azioni non eseguite.

Report richiesto:

- [F] Step eseguito.
- [F] Repo e branch.
- [F] HEAD iniziale.
- [F] Verifiche eseguite.
- [F] Esiti PASS/WARN/FAIL.
- [F] Problemi trovati.
- [F] Azioni non eseguite.
- [O] Prossimo micro-step consigliato.

Prossimo step consigliato:

[O] Se tutto passa, proporre un micro-step L0 documentale su branch dedicato e PR draft, senza merge automatico.