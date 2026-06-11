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

Ogni classe deve avere segnali, esempio, azione consigliata, retry ammesso e criterio di stop.

| Failure class | Segnali tipici ed esempi | Azione consigliata | Retry ammesso | Quando fermarsi o chiedere Alberto |
|---|---|---|---|---|
| `POWERSHELL_PARSE_ERROR` | Parser error, blocchi `finally` fuori contesto, parentesi o here-string non chiusi | Salvare log, chiedere diagnosi GPT, rigenerare script `.ps1` validabile | Si, solo con script corretto e differente | Stop se il fix resta ambiguo o ripete lo stesso parse error |
| `POWERSHELL_PROMPT_CONTINUATION` | Prompt multilinea `>>`, comando incollato incompleto | Kill sessione/processo, salvare log, rilanciare script `.ps1` salvato | Si, se il comando viene convertito in file script | Stop se serve input umano o il terminale resta interattivo |
| `GIT_PAGER_BLOCK` | Git mostra pager tipo `(END)` o processo senza output utile | Kill processo, rigenerare comando con `git --no-pager` | Si, una volta con comando no-pager | Stop se Git chiede credenziali o input interattivo |
| `GIT_SAFE_WARNING` | Stderr Git informativo con exit code `0`, ad esempio `Already up to date.` | Registrare warning e continuare se i gate passano | Non serve retry | Chiedere Alberto se il warning cambia baseline o remote atteso |
| `GIT_UNSAFE_ERROR` | Stderr Git inatteso, exit code nonzero, branch remoto incoerente | Stop fail-closed e pacchetto diagnostico | No, salvo fix chiaro e read-only | Stop immediato se potrebbe alterare branch, history o remote |
| `FILE_LOCKED` | Bridge file locked, sharing violation, write parziale | Usare output progressivo, nuovo file numerato, no `LAST-*`, retry controllato | Si, con backoff e file target coerente | Stop se lock persiste o rischia overwrite non autorizzato |
| `GH_NO_CHECKS_REPORTED` | `gh pr checks` restituisce `no checks reported` | Warning sicuro solo se altri gate locali passano e lo step non richiede CI | Non serve retry cieco | Chiedere Alberto se mancano checks richiesti per publish |
| `LF_CRLF_SAFE_WARNING` | `LF will be replaced by CRLF` o `CRLF will be replaced by LF` con exit code `0` | Trattare come warning se diff check, test, verify e health passano | Non serve retry | Stop se `git diff --check` fallisce o richiede normalizzazione line endings |
| `CREDENTIAL_PROMPT` | Prompt login, token, password, browser auth o input umano | Stop immediato e `NEEDS_ALBERTO_APPROVAL` | No | Chiedere Alberto sempre |
| `API_QUOTA_OR_RATE_LIMIT` | 429, quota exceeded, rate limit, budget exhausted | Salvare diagnostica e proporre retry differito o stop | Solo se budget e policy lo consentono | Stop se serve credenziale, budget non approvato o retry non giustificato |
| `TEST_FAILURE` | `pytest` o test mirato fallisce | Diagnosi GPT/Codex, fix dentro scope, rerun test mirato e gate | Si, se causa chiara e fix locale | Stop se causa fuori scope o test falliscono ripetutamente |
| `VERIFY_FAILURE` | `scripts/verify.ps1` fallisce | Leggere report, correggere solo cause chiare nello scope | Si, se fix e' locale e basso rischio | Stop se verify richiede publish, merge, deploy o refactor ampio |
| `WORKFLOW_HEALTH_FAILURE` | `python scripts/check_workflow_health.py` fallisce | Sincronizzare docs/index/test/script coerenti | Si, se gap documentale chiaro | Stop se richiede cambiare policy o rimuovere controlli |
| `UNKNOWN_FAILURE` | Sintomi non classificabili o output incompleto | Stop fail-closed, chiedere review GPT e Alberto se serve | No retry automatico | Stop sempre finche' non esiste diagnosi chiara |
| `TIMEOUT` | Processo supera timeout assoluto | Kill controllato, log completo, classificazione rischio | Si, solo con timeout/command change motivato | Stop se il comando puo' essere distruttivo o resta bloccato |
| `IDLE_TIMEOUT` | Nessun output/heartbeat entro soglia | Kill controllato, salvare stdout/stderr parziali | Si, se si aggiunge heartbeat o comando piu' minimo | Stop se idle indica prompt interattivo o deadlock non chiaro |
| `POTENTIALLY_DESTRUCTIVE_COMMAND` | reset, clean, rebase, checkout distruttivo, delete ampia, deploy | Stop immediato, nessuna esecuzione | No | Chiedere Alberto solo per una nuova approvazione esplicita e separata |

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
- differenza rispetto al tentativo precedente;
- criterio per non ripetere lo stesso errore.

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
- il retry genererebbe solo una ripetizione cieca;
- il costo/token/budget diventa non giustificato.

La policy non autorizza retry illimitati, publish automatico, merge automatico, deploy automatico, comandi distruttivi o bypass dei gate.

## Casi operativi concreti

| Caso | Classificazione | Azione |
|---|---|---|
| PowerShell resta nel prompt multilinea `>>` | `POWERSHELL_PROMPT_CONTINUATION` | Kill processo/sessione, salvare log, rilanciare solo uno script `.ps1` salvato e validato. |
| Git apre pager tipo `(END)` | `GIT_PAGER_BLOCK` | Kill processo, rigenerare comando con `git --no-pager`. |
| Errore `finally` incollato fuori contesto | `POWERSHELL_PARSE_ERROR` | Chiedere diagnosi GPT, generare script corretto, evitare mega-blocco incollato. |
| File Bridge bloccato | `FILE_LOCKED` | Scrittura progressiva o nuovo file numerato, evitare `LAST-*`, retry con backoff. |
| `gh pr checks` restituisce `no checks reported` | `GH_NO_CHECKS_REPORTED` | Warning sicuro solo se gli altri gate richiesti passano. |
| Warning LF/CRLF Git Windows | `LF_CRLF_SAFE_WARNING` | Non bloccare se diff check, test, verify e workflow health passano. |
| Prompt credenziali o input umano | `CREDENTIAL_PROMPT` | Stop immediato e `NEEDS_ALBERTO_APPROVAL`. |
| Comando distruttivo proposto | `POTENTIALLY_DESTRUCTIVE_COMMAND` | Stop immediato, nessun retry automatico. |

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
