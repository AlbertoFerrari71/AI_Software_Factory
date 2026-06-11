# 0980 - GPT Prompt Generator API Adapter

## Scopo

Questo step introduce la foundation per generare prompt Codex da uno step plan ASF.

Il comportamento attivo e' solo mock:

- `mock` e' il default;
- `live` e' presente solo come confine futuro e fallisce chiuso;
- nessuna chiamata provider viene eseguita;
- nessun segreto viene letto o salvato;
- nessuna azione Git/GitHub viene eseguita.

## Script

```text
scripts/asf_gpt_prompt_generator.py
```

CLI minima:

```text
python scripts/asf_gpt_prompt_generator.py --plan path\to\step_plan.json --mode mock --output path\to\generated_prompt.md --json
```

## Input

Lo script legge uno step plan JSON o Markdown.

Campi JSON consigliati:

- `step_id`;
- `title`;
- `objective`;
- `risk_level`;
- `phase`;
- `allowed_paths`;
- `forbidden_actions`.

Template:

```text
docs/templates/0980_GPT_PROMPT_REQUEST_TEMPLATE.json
```

## Output

In mock mode lo script scrive un prompt Markdown deterministico e stampa JSON con:

- `step_id`;
- `mode`;
- `selected_model`;
- `provider`;
- `live_enabled`;
- `prompt_path`;
- `risk_level`;
- `requires_alberto`;
- `status`;
- `next_action`.

Lo stato positivo e':

```text
PROMPT_READY
```

Il prossimo step operativo simulato e':

```text
CODEX_DRY_RUN_READY
```

## Live mode

`--mode live` non e' implementato in questo step. Anche con il flag futuro `--allow-live`, lo script risponde fail-closed.

La modalita' live richiede uno step separato, gate umano, verifica credenziali fuori repository e test dedicati.

## Guardrail

- no chiamate live;
- no lettura segreti;
- no rete;
- no pubblicazione Git;
- no merge;
- no deploy;
- no invocazione Codex;
- no OS appunti.

## Test

```text
tests/unit/test_asf_gpt_prompt_generator.py
```

Copertura minima:

- prompt deterministico in mock mode;
- live mode disabilitata;
- nessun segreto richiesto in mock mode;
- output JSON con campi obbligatori;
- path prompt valido;
- assenza pattern OS appunti nel sorgente.
