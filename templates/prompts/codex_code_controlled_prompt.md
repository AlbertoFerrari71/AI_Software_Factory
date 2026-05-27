# Codex Controlled Code Prompt

Usa questo prompt quando Codex deve applicare modifiche controllate su branch dedicato.

## Obiettivo

Eseguire una modifica piccola, testabile e reversibile rispettando il Codex Task Packet approvato.

## Contesto

AI Software Factory consente Auto Edit solo come L2 su branch dedicato, con file consentiti, test e riepilogo. Full Auto non e' ammesso per questo flusso.

## Livello rischio L0-L4

Livello massimo: L2 - Write controlled.

Safety level: L2.

Se il task richiede CI/CD, dipendenze, auth, database schema, security policy, cancellazioni, produzione, force push o merge diretto, fermarsi in safe stop e richiedere approval L3/L4.

## File da leggere

- `README.md`
- `AGENTS.md`
- `docs/10_ROADMAP.md`
- `docs/05_SECURITY_MODEL.md`
- Codex Task Packet allegato
- file specifici indicati nel task

## File modificabili

- Solo i file elencati nel Codex Task Packet.

## File vietati / file da non toccare

- `.env`
- `.env.*`
- secret o credenziali
- file fuori repository
- file non elencati come modificabili
- `.github/workflows/**` salvo approval L3
- policy di sicurezza salvo approval L3

## Vincoli

- Lavorare sul branch indicato.
- Modificare solo i file consentiti.
- Rispettare i file da non toccare indicati nel task packet.
- Non introdurre dipendenze senza decisione registrata.
- Aggiornare documentazione se cambia comportamento.
- Eseguire i test indicati.
- Se i test falliscono, non dichiarare completato il task.

## Output atteso

1. File modificati.
2. Riepilogo diff.
3. Test eseguiti.
4. Test falliti o non eseguiti.
5. Rischi residui.
6. Rollback consigliato.
7. Prossimo passo.

## Criteri di accettazione

- Il diff resta nello scope.
- I file vietati non sono toccati.
- I test richiesti passano o il task termina in safe stop.
- La documentazione necessaria e' aggiornata.
- Il rollback e' chiaro.

## Test / verifica

Eseguire i comandi indicati nel task packet. Default:

```powershell
python -m pytest -q
```

Verificare anche:

```powershell
git status --short
git diff --check
```

## Rollback / safe stop

Rollback L2: ripristinare i file modificati o abbandonare il branch. Safe stop se il diff include file fuori scope, secret, policy/CI non approvate, test critici falliti o livello superiore a L2.

## Cosa NON fare

- Non fare commit.
- Non fare push.
- Non fare merge.
- Regola sintetica: no commit, no push, no merge.
- Non fare force push.
- Non cancellare file o dati.
- Non aggirare test o policy.
