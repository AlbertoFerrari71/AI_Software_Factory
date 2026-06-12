# 1035 - Provider Response Diagnostic Sanitized Review

## Scopo

Lo STEP 1035 chiude la criticita' aperta dallo STEP 1030:

```text
LIVE_FAILED_SAFE
Provider response did not contain prompt text.
```

L'obiettivo e' diagnosticare lo shape della risposta provider senza salvare raw request, raw response o testo provider completo.

## Implementato ora

- `scripts/asf_provider_response_diagnostic.py` produce shape sanitizzato della risposta provider.
- `sanitize_provider_response_shape()` salva solo tipo, chiavi, lunghezze, presenza valori e enum strutturali consentiti.
- `detect_candidate_text_paths()` trova path candidati come `output_text`, `output[].content[].text`, `choices[].message.content`, `message.content` e `content[].text`.
- La live diagnostic usa una sola chiamata provider, `max_retries=0`, `store=false`, sentinel pubblico e output sanitizzato.
- Il parser non e' stato patchato perche' la diagnostica ha confermato un path gia' supportato: `output[1].content[0].text`.

## File Bridge

Output attesi:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\codex_command\1035-Provider-Shape-Sanitized.json
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\codex_command\1035-Provider-Diagnostic-Sanitized.md
```

Questi file non contengono raw payload e non contengono testo provider completo.

## Risultato diagnostico

La live diagnostic ha trovato testo utile in:

```text
output[1].content[0].text
```

La shape include:

- `raw_payload_saved=false`;
- `raw_text_saved=false`;
- `candidate_text_paths_count=2`;
- `parser_extracted_text=true`;
- `parser_contains_expected_sentinel=true`;
- `automatic_retries_disabled=true`;
- `live_call_count=1`.

## Decisione per 1030

Decisione consigliata:

```text
1030_READY_FOR_PUBLISH_AFTER_REVIEW
```

Motivo: il path live corrente e' gia' gestito dal parser 1030 e i gate locali risultano PASS. Lo STEP 1030 non viene trasformato retroattivamente in PASS; il 1035 fornisce evidence sanitizzata per decidere la pubblicazione o review finale.

## Limiti

- Nessun raw provider payload e' conservato.
- Nessun retry live e' autorizzato dallo step.
- La diagnostica non e' una nuova piattaforma provider: resta un helper chirurgico per review.
