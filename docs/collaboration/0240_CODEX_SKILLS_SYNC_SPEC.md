# 0240 - Codex Skills Sync Specification

## Scopo

[F] Questo documento definisce come sincronizzare skills Codex comuni in modo controllato tra Alberto e Luca.

[F] Il repository `Codex_Skills` e' la fonte ufficiale proposta per le skills comuni.

[S] Skills locali di repository possono restare sotto `repo/.agents/skills` quando servono regole specifiche del progetto.

## Decisioni

- [F] Le skills comuni non vengono mantenute a mano in Dropbox.
- [F] La sync deve essere dry-run per default.
- [F] Ogni apply reale deve creare backup prima di sovrascrivere.
- [F] La sync deve produrre report testuale.
- [F] File non gestiti non devono essere cancellati senza conferma esplicita.
- [O] La lista file o hash e' sufficiente per il primo stadio; hash piu' forti possono arrivare dopo.

## Skills comuni e skills locali

| Tipo | Sorgente | Target | Uso |
|---|---|---|---|
| Comune | `Codex_Skills` | `%USERPROFILE%\.agents\skills` | Regole riusabili tra repo |
| Locale repo | Repository specifico | `repo\.agents\skills` | Regole o strumenti legati al repo |
| Sistema/plugin | Installazione Codex/plugin | Area gestita dal tool | Non modificare manualmente |

## Convenzioni naming

- [F] `as-common-...`: skill comune riusabile.
- [F] `as-asf-...`: skill specifica AI Software Factory.
- [F] `as-ai-radar-...`: skill specifica AI Release Radar.
- [F] `as-blueprint-...`: skill specifica ASF Blueprint Studio.

## Cartelle target

```text
%USERPROFILE%\.agents\skills
repo\.agents\skills
```

[F] Il target utente contiene skills personali/comuni installate localmente.

[S] Il target repo contiene skills versionate o documentate per quel repository, se il progetto lo autorizza.

## Sync sicuro

1. [F] Risolvere `SourcePath` e `TargetPath` in path assoluti.
2. [F] Verificare che `SourcePath` esista e contenga cartelle skill.
3. [F] Eseguire dry-run con lista file e azioni previste.
4. [F] Se apply reale, creare backup del target prima di overwrite.
5. [F] Copiare solo file gestiti dalla sync.
6. [F] Non cancellare file extra senza conferma esplicita.
7. [F] Generare report testuale con copied/skipped/warn/fail.

## Cosa non fare

- [F] Non usare Dropbox come sorgente primaria skills.
- [F] Non fare copia manuale non tracciata come procedura stabile.
- [F] Non sovrascrivere cieca senza backup.
- [F] Non sincronizzare segreti, token o file `.env`.
- [F] Non eseguire script di installazione esterni durante la sync.

## Regole operative

- [F] Prima apply reale: `DryRun=true` e report letto.
- [F] Apply reale solo con `-DryRun:$false` e backup attivo.
- [F] Report salvato in Bridge o cartella operativa numerata.
- [O] Dopo sync, Luca esegue un micro-step read-only per confermare comportamento.

## Rischi

| Rischio | Mitigazione |
|---|---|
| Sovrascrittura skill locale utile | Backup target prima di apply |
| Skill divergenti tra PC | Repo `Codex_Skills` come fonte comune |
| Dropbox conflicted copy | Non usare Dropbox come sorgente skills |
| Segreti nei file skill | Scan minimo e review manuale |

## Checklist

- [ ] [F] `SourcePath` verificato.
- [ ] [F] `TargetPath` verificato.
- [ ] [F] Dry-run eseguito.
- [ ] [F] Report letto.
- [ ] [F] Backup creato per apply reale.
- [ ] [F] Nessun file extra cancellato.
- [ ] [F] Nessun segreto copiato.

## Prossimo step consigliato

[O] Usare `scripts/collaboration/Sync-CodexSkillsFromRepo.ps1` solo in dry-run durante il primo onboarding Luca.