# 1030 - Manual and Semi-Automatic Loop Runbook

## Obiettivo

Questo runbook descrive il loop manuale/semi-automatico dopo lo STEP 1030.

Il loop target e':

```text
ChatGPT prepara prompt/comando
-> Codex o PowerShell eseguono
-> Bridge riceve report/output
-> ASF scopre e interpreta lo stato
-> ASF genera handoff/ripartenza
-> nuova chat riparte senza perdita di contesto
```

## Procedura operativa

1. ChatGPT prepara un prompt Codex pulito oppure un comando PowerShell separato.
2. Alberto esegue Codex o PowerShell in modo controllato.
3. L'esecutore scrive report/output nel Bridge.
4. Alberto puo' scrivere `Codex fatto`, `Pwsh fatto`, `CF`, `PF` o variante equivalente.
5. ChatGPT cerca il report/output nel Bridge se ha accesso.
6. Se il Bridge non e' accessibile, ChatGPT chiede ad Alberto di incollare solo il report/output rilevante.
7. ASF classifica lo stato e propone il prossimo step.
8. Il generatore handoff produce Markdown, JSON e prompt di ripartenza.
9. L'advisor lunghezza prompt puo' essere usato come guardrail leggero prima di incollare un nuovo prompt Codex.

## Discovery report

Esempio Codex:

```powershell
python scripts/asf_bridge_report_discovery.py `
  --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory" `
  --expected-step 1030 `
  --kind codex `
  --json
```

La discovery restituisce anche:

- `searched`: pattern cercati;
- `summary`: riepilogo compatto;
- `manual_paste_instruction`: cosa incollare se il Bridge non e' accessibile.

Esempio PowerShell:

```powershell
python scripts/asf_bridge_report_discovery.py `
  --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory" `
  --expected-step 1030 `
  --kind pwsh `
  --json
```

## Handoff pack

```powershell
python scripts/asf_handoff_pack_generator.py `
  --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory" `
  --repo-root "C:\Users\alberto.ferrari\source\repos\AI_Software_Factory" `
  --step 1030 `
  --title "ASF GPT Live Continuity Mega-Step" `
  --status PARTIAL_PASS `
  --json
```

## Smoke sicuro 1030-H

Lo smoke deve usare directory temporanee o Bridge controllato e deve simulare:

- generazione prompt mock;
- report Codex fittizio;
- output PowerShell fittizio;
- discovery Bridge;
- handoff pack;
- prompt length advisor leggero;
- prompt nuova chat.

Lo smoke non deve:

- eseguire Codex reale;
- fare commit, push, PR, merge o deploy;
- fare retry live;
- attivare splitter automatici;
- creare loop unattended.

## Classificazione stati

- `PASS`: tutti i gate richiesti sono passati e la live one-call ha avuto successo.
- `LIVE_FAILED_SAFE`: gate locali passati, live eseguita una volta e fallita in modo sicuro.
- `PARTIAL_PASS`: feature locali e test passati, ma live non riuscita o non eseguita per vincolo motivato.
- `BLOCKED`: precondizione bloccante, per esempio impossibile garantire no retry.
- `FAIL`: test o gate richiesto fallito.

## Prompt length advisor leggero

```powershell
python scripts/asf_prompt_length_advisor.py `
  --prompt-file "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\codex_command\1030-Prompt_Codex.md" `
  --json
```

Il prompt monolitico da 20-30k caratteri resta il default ASF/Codex. L'advisor e' un guardrail leggero, non una packetizzazione obbligatoria.

## Limiti

Il runbook non sostituisce il publish runner, non autorizza pubblicazione e non rende automatico il merge. Ogni pubblicazione resta uno step separato human-gated.
