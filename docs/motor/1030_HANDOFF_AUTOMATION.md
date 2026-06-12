# 1030 - Handoff Automation

## Scopo

Lo STEP 1030 introduce un generatore locale di handoff per ridurre perdita di contesto tra una chat e la successiva.

Script:

```text
scripts/asf_handoff_pack_generator.py
```

## Output

Per lo step 1030, gli output attesi nel Bridge sono:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\handoff\1030-Handoff.md
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\handoff\1030-Handoff.json
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\handoff\1030-Start_Next_Chat_Prompt.md
```

Il report finale Codex dello step puo' anche salvare un handoff pronto nella cartella operativa `codex_command`:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory\codex_command\1030-Handoff_Nuova_Chat.md
```

Se il Bridge non e' accessibile, lo script ripiega su `tmp/asf_handoff/<step>` nel repository.

## Comando base

```powershell
python scripts/asf_handoff_pack_generator.py `
  --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Software_Factory" `
  --repo-root "C:\Users\alberto.ferrari\source\repos\AI_Software_Factory" `
  --step 1030 `
  --title "ASF GPT Live Continuity Mega-Step" `
  --status PARTIAL_PASS `
  --json
```

## Fonti usate

Il generatore usa fonti fail-soft:

- stato Git read-only;
- log Git recente;
- report/output Bridge tramite discovery;
- `state.json` se presente;
- live result JSON se presente;
- `gh pr list` read-only se disponibile e non disabilitato.

La discovery Bridge preferisce report JSON strutturati quando sono presenti sia Markdown sia JSON, ma mantiene il Markdown come testo umano leggibile. Se manca il report, l'output indica i pattern cercati e cosa Alberto deve incollare manualmente.

## Sicurezza

Il generatore:

- non salva API key;
- non salva Authorization header;
- non salva bearer token;
- redige pattern sensibili;
- non fa commit, push, PR, merge o deploy;
- non esegue Codex.

## JSON stabile

Il JSON include:

```json
{
  "step": "1030",
  "title": "ASF GPT Live Continuity Mega-Step",
  "status": "PARTIAL_PASS",
  "repo": {},
  "bridge": {},
  "checks": [],
  "live_run": {},
  "next_step": "1040) Publish GPT Live Continuity Mega-Step",
  "risks": []
}
```

## Stato futuro

Lo STEP 1030 non introduce un orchestratore. Il pacchetto handoff resta un artifact operativo da revisionare prima di qualunque pubblicazione.
