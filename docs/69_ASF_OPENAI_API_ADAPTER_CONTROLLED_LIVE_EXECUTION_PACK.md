# ASF OpenAI API Adapter Controlled Live Execution Pack

## 1. Scopo

STEP 540 prepara un pack operativo separato per una futura esecuzione live controllata dell'OpenAI API Adapter.

Il pack usa `scripts/asf_openai_controlled_live_execution_pack.py` e produce artifact JSON/Markdown sotto `tmp/` con postura fail-closed.

Il default e' dry-run:

- nessuna chiamata OpenAI API;
- nessun SDK OpenAI;
- nessuna rete in dry-run;
- credenziale indicata solo come booleano `credential_present`;
- classificazione stabile compatibile con STEP 530;
- prossimo passo operativo esplicito.

Questo documento non autorizza una chiamata live reale. Codex non deve eseguire live call.

---

## 2. Cosa fa

Il controlled live execution pack:

- prepara preflight e artifact operatore;
- applica dry-run come comportamento default;
- richiede doppio consenso per live reale futuro;
- vincola gli artifact a `tmp/`;
- mantiene prompt tiny e non sensibile;
- usa modello in allowlist controllata;
- impone `store: false`;
- impone output massimo basso;
- impone timeout basso;
- prevede al massimo una chiamata live;
- non usa retry automatici, loop live o chiamate parallele.

---

## 3. Cosa non fa

Il pack non:

- autorizza automaticamente una chiamata live;
- considera `OPENAI_API_KEY` come consenso;
- stampa, salva, hash, tronca, maschera parzialmente o serializza la API key;
- registra lunghezza, prefisso, suffisso o fingerprint della chiave;
- usa network in dry-run;
- usa rete nei test automatici;
- fa commit, push, PR, merge o deploy.

Regola:

```text
API key presente != autorizzazione a chiamare OpenAI
```

---

## 4. Comando dry-run default

Il comando senza flag live produce artifact safe e non chiama rete:

```powershell
python scripts/asf_openai_controlled_live_execution_pack.py
```

Output previsti:

```text
tmp/asf_openai_controlled_live_execution_pack/asf_openai_controlled_live_execution_pack.json
tmp/asf_openai_controlled_live_execution_pack/asf_openai_controlled_live_execution_pack.md
```

Lo schema contiene almeno:

```json
{
  "status": "skipped",
  "classification": "disabled",
  "provider": "openai",
  "model": "gpt-5.5",
  "live_enabled": false,
  "credential_present": false,
  "dry_run": true,
  "network_call_count": 0,
  "duration_ms": 0,
  "timestamp": "ISO-8601 timestamp"
}
```

---

## 5. Condizioni per live reale futuro

Una futura esecuzione live reale richiede almeno:

```text
--execution-mode live
ASF_OPENAI_LIVE_ENABLED=1
--confirm-live-openai
OPENAI_API_KEY presente solo nell'ambiente locale
artifact JSON/Markdown sotto tmp/
```

Esempio concettuale sicuro:

```powershell
$env:OPENAI_API_KEY = "<set in environment, never printed>"
$env:ASF_OPENAI_LIVE_ENABLED = "1"
python scripts/asf_openai_controlled_live_execution_pack.py --execution-mode live --confirm-live-openai
```

Questo esempio e' per un futuro step autorizzato. Codex non deve eseguirlo.

---

## 6. Mock provider

Il mock provider valida gates, schema e artifact senza rete:

```powershell
$env:OPENAI_API_KEY = "<set in environment, never printed>"
$env:ASF_OPENAI_LIVE_ENABLED = "1"
python scripts/asf_openai_controlled_live_execution_pack.py --execution-mode mock --confirm-live-openai
```

Nel mock:

- `network_call_count` resta `0`;
- `mock_provider_call_count` indica la chiamata finta;
- nessun endpoint OpenAI viene contattato.

---

## 7. Classificazioni

| Classification | Significato |
|---|---|
| `not_configured` | Configurazione live incompleta, env flag assente o modello/prompt non conforme. |
| `disabled` | Dry-run o live esplicitamente non abilitato. |
| `credential_missing` | `OPENAI_API_KEY` assente quando live/mock live-gated e' richiesto. |
| `live_not_allowed` | Conferma live o artifact runtime obbligatorio mancante. |
| `success` | Mock o live futuro soddisfa il contratto. |
| `provider_error` | Provider restituisce errore non auth/rate-limit. |
| `network_error` | Timeout, rete o connessione fallita. |
| `rate_limited` | Provider limita la richiesta. |
| `auth_error` | Provider rifiuta autenticazione/autorizzazione. |
| `schema_error` | Risposta non conforme o JSON non valido. |
| `unknown_error` | Fallback controllato per errore locale inatteso. |

---

## 8. Gestione errori operatore

| Errore | Azione |
|---|---|
| `auth_error` | Tornare fail-closed, verificare credenziale localmente senza stamparla, non riusare artifact sospetti. |
| `rate_limited` | Non fare retry aggressivi; attendere e pianificare un nuovo step autorizzato. |
| `network_error` | Verificare connettivita' locale senza esporre segreti; mantenere `ASF_OPENAI_LIVE_ENABLED` disabilitato dopo la diagnosi. |
| `schema_error` | Ispezionare solo artifact redatti, aggiornare parser/test mockati prima di qualunque nuovo live. |

---

## 9. Verifica artifact senza stampare segreti

Verifica boolean safe:

```powershell
$ArtifactRoot = "tmp/asf_openai_controlled_live_execution_pack"
$Forbidden = @("sk-", "Bearer ", "api_key_length", "credential_length", "api_key_sha", "credential_sha", "fingerprint")
$HasForbidden = Select-String -Path (Join-Path $ArtifactRoot "*") -Pattern $Forbidden -Quiet
if ($HasForbidden) {
    Write-Host "Possible secret marker found. Stop and inspect offline without sharing output."
} else {
    Write-Host "No forbidden marker detected in controlled live artifacts."
}
```

Il comando usa `-Quiet` per non stampare eventuali righe sensibili.

---

## 10. Tornare a stato sicuro

Dopo una prova operativa:

```powershell
Remove-Item Env:\ASF_OPENAI_LIVE_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:\OPENAI_API_KEY -ErrorAction SilentlyContinue
python scripts/asf_openai_controlled_live_execution_pack.py
```

Il nuovo dry-run deve riportare `dry_run: true`, `network_call_count: 0` e `live_enabled: false`.

---

## 11. Template PowerShell operatore

Template safe bootstrap:

```text
templates/pwsh_command_pack/step_540_openai_controlled_live_execution_pack_template.ps1
```

Il template segue STEP 536:

- bootstrap corto;
- script `.ps1` generato;
- parse-check con `[scriptblock]::Create(...)`;
- esecuzione via `pwsh -NoProfile -ExecutionPolicy Bypass -File`;
- output numerati e `LAST`;
- DOCX best-effort/non bloccante;
- `git --no-pager`;
- nessuna pubblicazione Git;
- se una pubblicazione futura serve, branch + PR resta il default.

---

## 12. Verifiche consigliate

Test focalizzati:

```powershell
python -m pytest tests/unit/test_asf_openai_controlled_live_execution_pack.py
```

Verifiche complete:

```powershell
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
```

I test devono restare mock/dry-run, senza rete e senza credenziali reali.

---

## 13. Prossimo step

```text
550) OpenAI API Adapter First Authorized Live Run
```
