# 0940 - Supervised Loop Operator Runbook

## Scopo

Guida pratica per usare ASF V1 come ciclo supervisionato. Questo runbook non autorizza publish, merge o deploy automatici.

## Cosa fa Alberto

- Definisce milestone e obiettivo dello step.
- Approva o blocca publish, merge, deploy e milestone strategiche.
- Decide quando una failure richiede cambio scope.
- Controlla `NEEDS_ALBERTO_APPROVAL` prima di qualunque azione L3/L4.

## Cosa fa GPT

- Pianifica step e lane.
- Rivede report, diff, stdout/stderr e failure class.
- Decide `PASS`, `FIX`, `STOP` o `ASK_ALBERTO`.
- Puo' autorizzare retry solo con motivazione e dentro il budget.
- Non esegue PowerShell direttamente.

## Cosa fa Codex

- Esegue modifiche locali a codice, test o documentazione.
- Produce report Bridge deterministico.
- Non committa, non pusha, non apre PR, non mergea e non deploya.

## Cosa fa PowerShell Fast Lane

- Esegue task meccanici autorizzati.
- Usa processi non interattivi, timeout e output strutturati.
- Salva stdout, stderr, exit code e report.
- Non usa AI per controlli ripetibili.

## Cosa fa PowerShell Recovery Loop

- Rileva timeout, idle timeout, prompt sospesi, stderr inattesi e failure note.
- Ferma processi bloccati in modo controllato.
- Classifica la failure.
- Chiede diagnosi a GPT reviewer.
- Rilancia solo se rischio, scope e retry policy lo consentono.

## Cosa fa il Bridge

- Conserva prompt, report, log, semafori e `state.json`.
- Permette a planner, executor, reviewer e runner di scambiarsi stato.
- Non sostituisce Git e file versionati come fonte autorevole.

## Prima di autorizzare milestone, publish o merge

Controllare:

- stato Git coerente;
- diff limitato allo scope;
- report Codex presente;
- review GPT/Alberto chiara;
- `python -m pytest` passato;
- `python scripts/check_workflow_health.py` passato;
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1` passato;
- `git --no-pager diff --check` passato;
- warning classificati come informativi o bloccanti;
- nessuna approval implicita.

## Se il loop si ferma

1. Leggere `state.json`.
2. Leggere ultimo report Bridge.
3. Controllare failure class.
4. Verificare retry corrente e retry rimanenti.
5. Se lo stato e' `NEEDS_ALBERTO_APPROVAL`, decidere manualmente.
6. Se lo stato e' `STOPPED`, non forzare retry senza nuova diagnosi.

## NEEDS_ALBERTO_APPROVAL

Significa che il loop ha bisogno di una decisione umana prima di proseguire. Casi tipici:

- publish;
- merge;
- deploy;
- cambio milestone;
- rischio L3 o L4;
- credenziali o input umano;
- scope ambiguo;
- ripetizione dello stesso errore.

## Warning informativo o errore bloccante

Warning informativo:

- exit code `0`;
- pattern stderr noto e sicuro;
- gate obbligatori passati;
- nessun diff fuori scope.

Errore bloccante:

- exit code nonzero;
- stderr inatteso;
- test, workflow health, verify o diff check falliti;
- comando rischioso;
- credenziale o prompt interattivo;
- diff fuori scope.

## Limite massimo 10 retry

Policy: GPT-discretionary bounded retry policy.

GPT reviewer puo' autorizzare retry automatici da 0 a 10. `10` e' il massimo assoluto di sicurezza, non il default.

Ogni retry deve dichiarare:

- motivazione;
- failure class;
- rischio stimato;
- comando o script corretto;
- expected effect;
- stop condition;
- retry corrente;
- retry rimanenti.

Stop immediato se rischio, scope o sicurezza non sono accettabili.

## Terminale incoerente

Se i gate danno risultati incoerenti:

1. chiudere il terminale;
2. aprire nuova sessione pwsh -NoProfile;
3. rilanciare comando minimo;
4. solo dopo diagnosticare il codice.

