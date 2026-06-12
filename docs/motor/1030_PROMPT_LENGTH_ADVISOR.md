# 1030 - Prompt Length Advisor leggero

## Scopo

Lo STEP 1030 introduce un advisor leggero per valutare la lunghezza dei prompt Codex senza cambiare il workflow ASF.

Regola operativa:

```text
Il prompt monolitico da 20-30k caratteri resta il default ASF/Codex.
L'advisor e' un guardrail leggero, non una packetizzazione obbligatoria.
```

## Script

```text
scripts/asf_prompt_length_advisor.py
```

Esempio:

```powershell
python scripts/asf_prompt_length_advisor.py `
  --prompt-file "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\codex_command\1030-Prompt_Codex.md" `
  --json
```

## Soglie

| Range | Classificazione | Effetto |
| --- | --- | --- |
| 0-20000 caratteri | `ok` | Nessun warning operativo |
| 20001-30000 caratteri | `operational_attention` | OK operativo con attenzione leggera |
| 30001-60000 caratteri | `warning` | Valutare accorciamento manuale se perde leggibilita' |
| oltre 60000 caratteri | `manual_split_recommended` | Consigliare suddivisione manuale |

## Guardrail

- Nessun blocco automatico.
- Nessuno splitter automatico.
- Nessuna packetizzazione obbligatoria.
- I Mega-Step possono restare monolitici se leggibili.
- La decisione finale resta umana.

## Test

Il comportamento e' coperto da:

```text
tests/unit/test_asf_prompt_length_advisor.py
```
