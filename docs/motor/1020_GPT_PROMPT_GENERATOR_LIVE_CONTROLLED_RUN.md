# 1020 - GPT Prompt Generator Live Controlled Run

## Scopo

Questo step matura `scripts/asf_gpt_prompt_generator.py` introducendo una modalita' live controllata per generare un prompt Codex da uno step plan ASF.

La postura resta:

- `mock` default;
- live solo con `--mode live` e `--approve-live`;
- al massimo una chiamata provider per esecuzione controllata;
- nessun retry automatico live;
- nessuna esecuzione Codex reale;
- nessun publish, merge o deploy automatico.

## Quality-first operating principle

Per prompt strategici, architettura, gate, policy, automazione e strumenti che guidano sviluppo software, ASF privilegia qualita', robustezza, sicurezza e tracciabilita' rispetto a velocita' e costo.

La riduzione di costo o output e' ammessa solo dopo aver preservato:

- correttezza tecnica;
- sicurezza operativa;
- ripetibilita';
- auditabilita';
- fail-closed behavior;
- chiarezza dei gate umani.

Questa e' una decisione operativa: gli adapter che guidano sviluppo software devono favorire output verificabili, sanitizzati e human-gated anche quando un modello piu' veloce o economico sarebbe disponibile.

## Script

```text
scripts/asf_gpt_prompt_generator.py
```

CLI mock, ancora default:

```text
python scripts/asf_gpt_prompt_generator.py --plan path\to\step_plan.json --mode mock --output path\to\generated_prompt.md --json
```

CLI live controllata:

```text
python scripts/asf_gpt_prompt_generator.py --plan path\to\step_plan.json --mode live --approve-live --output path\to\generated_prompt.md --json --max-output-tokens 1200 --model gpt-5.5
```

`--allow-live` resta solo alias legacy di `--approve-live`.

## Template

```text
docs/templates/1020_GPT_LIVE_CONTROLLED_PLAN_TEMPLATE.json
docs/templates/1020_GPT_LIVE_CONTROLLED_RESULT_TEMPLATE.json
```

Il piano smoke sicuro usa lo step:

```text
1020-smoke-generate-codex-prompt
```

## Stati

Il risultato controllato distingue:

- `MOCK_SUCCESS`;
- `LIVE_SUCCESS`;
- `LIVE_SKIPPED_NO_APPROVAL`;
- `LIVE_SKIPPED_NO_API_KEY`;
- `LIVE_BLOCKED_BY_CONFIG`;
- `LIVE_BLOCKED_BY_PROVIDER`;
- `LIVE_BLOCKED_BY_QUOTA_OR_RATE_LIMIT`;
- `LIVE_FAILED_SAFE`.

Classi provider minime:

- `missing_api_key`;
- `missing_openai_package`;
- `invalid_model`;
- `authentication_error`;
- `permission_error`;
- `rate_limit`;
- `quota_exceeded`;
- `timeout`;
- `network_error`;
- `bad_request`;
- `unknown_provider_error`.

## Output

La run 1020 preferisce output Bridge sotto `codex_command`:

```text
1020-Live-Controlled-Prompt.md
1020-Live-Controlled-Result.json
1020-Live-Controlled-Result-Sanitized.md
```

Il result JSON e il Markdown sanitizzato riportano solo metadati sicuri:

- `api_key_present` booleano;
- `api_key_logged=false`;
- `raw_secret_logged=false`;
- `authorization_header_logged=false`;
- `live_call_attempted`;
- `live_call_count`;
- stato classificato;
- path output;
- next action.

Il valore della credenziale non viene stampato, salvato, serializzato o incluso negli artifact.

## Guardrail live

La live mode fallisce chiusa se manca una delle condizioni:

- `--mode live`;
- `--approve-live`;
- credenziale presente solo nell'ambiente locale;
- output path dentro repository, directory temporanea o Bridge `codex_command`;
- budget di output positivo e sotto cap;
- configurazione provider importabile.

Se una condizione manca, lo script non tenta rete e scrive un risultato esplicito, per esempio `LIVE_SKIPPED_NO_APPROVAL`, `LIVE_SKIPPED_NO_API_KEY` o `LIVE_BLOCKED_BY_CONFIG`.

Se la chiamata provider fallisce, il risultato viene redatto e classificato senza salvare request/response raw. Ogni retry richiede uno step separato e approvato.

## Test

```text
tests/unit/test_asf_gpt_prompt_generator.py
tests/unit/test_asf_gpt_prompt_generator_live_controlled.py
```

Copertura minima:

- mock mode resta default;
- live senza approval non tenta provider;
- live senza credenziale non tenta provider;
- provider error viene sanitizzato;
- quota/rate limit viene classificato;
- package provider mancante produce `LIVE_BLOCKED_BY_CONFIG`;
- success live simulato con monkeypatch scrive prompt e result;
- `live_call_count` massimo 1;
- nessuna esecuzione Codex reale.

## Prossimo step consigliato

```text
1020-A) Review and Publish Live Controlled Adapter
```
