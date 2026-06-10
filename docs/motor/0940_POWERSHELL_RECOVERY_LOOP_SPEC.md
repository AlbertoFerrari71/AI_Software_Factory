# 0940 - PowerShell Recovery Loop Spec

## Scopo

PowerShell Recovery Loop trasforma il recovery manuale di Alberto in un workflow automatico supervisionato, senza ridurre i gate umani.

## Workflow manuale storico

1. Comando PowerShell parte.
2. Terminale si blocca o restituisce errore.
3. Alberto interrompe il comando.
4. Alberto raccoglie la schermata.
5. Alberto passa l'errore a ChatGPT.
6. ChatGPT diagnostica.
7. Alberto rilancia il comando corretto.

## Workflow ASF

1. ASF lancia comando in processo isolato.
2. Salva stdout/stderr progressivamente nel Bridge.
3. Controlla heartbeat, timeout e idle timeout.
4. Se exit code e' diverso da `0` o il processo e' bloccato:
   - ferma il processo;
   - salva pacchetto diagnostico;
   - crea semaforo `POWERSHELL_FAILED` o `POWERSHELL_HUNG`;
   - chiede diagnosi a GPT reviewer;
   - genera fix command, fix script o fix prompt Codex.
5. Rilancia solo se rischio basso e retry disponibili.
6. Altrimenti stop e richiesta Alberto.

Il gesto umano di interruzione viene sostituito da watchdog, timeout e kill processo controllato.

## Failure class

Il recovery loop deve classificare almeno:

- `POWERSHELL_PARSE_ERROR`
- `POWERSHELL_PROMPT_CONTINUATION`
- `GIT_PAGER_BLOCK`
- `GIT_SAFE_WARNING`
- `GIT_UNSAFE_ERROR`
- `FILE_LOCKED`
- `GH_NO_CHECKS_REPORTED`
- `LF_CRLF_SAFE_WARNING`
- `CREDENTIAL_PROMPT`
- `API_QUOTA_OR_RATE_LIMIT`
- `TEST_FAILURE`
- `VERIFY_FAILURE`
- `WORKFLOW_HEALTH_FAILURE`
- `UNKNOWN_FAILURE`
- `TIMEOUT`
- `IDLE_TIMEOUT`
- `POTENTIALLY_DESTRUCTIVE_COMMAND`

## GPT-discretionary bounded retry policy

GPT reviewer puo' autorizzare retry automatici da 0 a 10. `10` e' il massimo assoluto di sicurezza, non il valore automatico predefinito.

Ogni retry deve avere:

- motivazione;
- failure class;
- rischio stimato;
- comando o script corretto;
- expected effect;
- rollback/stop condition se applicabile;
- numero retry corrente;
- retry rimanenti.

## Stop immediato

Il loop deve fermarsi senza retry quando:

- rischio passa a L3 o superiore;
- il comando proposto e' distruttivo;
- serve credenziale o input umano;
- cambia lo scope;
- falliscono piu' volte gli stessi sintomi;
- il fix richiede publish, merge o deploy;
- il diff modifica file fuori scope;
- GPT non puo' motivare chiaramente perche' il retry e' sicuro.

## Output recovery

Il pacchetto diagnostico deve includere:

- envelope task originale;
- comando normalizzato;
- stdout/stderr parziali;
- exit code o motivo kill;
- timestamp;
- failure class;
- retry corrente;
- suggerimento GPT reviewer;
- decisione `FIX`, `STOP` o `ASK_ALBERTO`.

