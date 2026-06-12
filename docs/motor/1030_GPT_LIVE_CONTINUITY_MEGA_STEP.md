# 1030 - ASF GPT Live Continuity Mega-Step

## Scopo

Lo STEP 1030 porta il GPT Prompt Generator e il loop manuale/semi-automatico ASF da live quasi funzionante a continuita' operativa piu' robusta tra ChatGPT, Codex, PowerShell, Bridge e nuova chat.

Il focus e':

- Responses API output extraction hardening;
- Responses parser normalization with explicit statuses;
- Bridge report discovery foundation;
- Done trigger spec per "Codex fatto" e "Pwsh fatto";
- Automated Handoff Pack Generator;
- Prompt Length Advisor leggero;
- smoke end-to-end locale senza automazione pericolosa.

## Implementato ora

- `scripts/asf_gpt_prompt_generator.py` estrae testo da `response.output_text`, dict `output_text`, oggetti SDK-like con `model_dump`, `to_dict` o `dict`, e da `output[].content[].text`.
- `scripts/asf_responses_parser.py` normalizza payload JSON/dict Responses-style in stati espliciti: `success`, `empty`, `partial`, `malformed`, `provider_error`, `rate_limited`, `quota_exceeded`, `missing_credentials` e `unknown_schema`.
- Il parser cerca tutti gli item compatibili e non si ferma su reasoning, tool o altri item non testuali.
- Le refusal non sono trattate come prompt validi.
- Il client live OpenAI viene creato con `max_retries=0`; se questa garanzia non e' disponibile, la live viene bloccata fail-closed.
- `scripts/asf_bridge_report_discovery.py` cerca report Codex, output PowerShell, state e handoff recenti nel Bridge producendo JSON stabile.
- La discovery preferisce `*-Report_Codex.json` quando disponibile, produce un riepilogo compatto e indica cosa incollare se il Bridge non e' accessibile.
- `scripts/asf_handoff_pack_generator.py` genera Markdown, JSON e prompt di ripartenza nuova chat.
- `scripts/asf_prompt_length_advisor.py` classifica la lunghezza prompt senza bloccare e senza splitter.

## Prompt length advisor

Il prompt monolitico da 20-30k caratteri resta il default ASF/Codex. L'advisor e' un guardrail leggero, non una packetizzazione obbligatoria.

Soglie operative:

- fino a 20000 caratteri: `ok`;
- 20001-30000 caratteri: `operational_attention`;
- 30001-60000 caratteri: `warning`;
- oltre 60000 caratteri: `manual_split_recommended`.

La decisione finale resta umana. Nessuno splitter automatico viene attivato.

## Convenzione operativa

ChatGPT resta il planner/reviewer del ciclo. Quando Alberto segnala completamento con trigger brevi, ChatGPT deve cercare il report nel Bridge se ha accesso, classificarlo e proporre il prossimo step senza inventare stati.

Il Bridge resta storage operativo. Git e file versionati restano la fonte autorevole.

## Non implementato

- loop automatico unattended;
- Codex exec reale;
- publish automatico;
- merge automatico;
- scheduler;
- polling continuo del Bridge.

## Smoke sicuro

Lo smoke 1030 simula:

```text
GPT prompt generator mock
-> report Codex fittizio
-> output Pwsh fittizio
-> bridge report discovery
-> handoff pack
-> prompt length advisor
-> next chat prompt
```

Lo smoke non esegue Codex reale, non fa commit, push, PR, merge, deploy, retry live, splitter automatici o loop unattended.

## Prossimo step

Se parser, discovery, handoff, test, workflow health, diff check e live one-call passano:

```text
1040) Publish GPT Live Continuity Mega-Step
```

Se la live fallisce safe ma i gate locali passano:

```text
1035) Provider Response Diagnostic Sanitized Review
```
