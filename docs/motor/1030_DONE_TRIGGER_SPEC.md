# 1030 - Done Trigger Spec

## Scopo

Questa specifica formalizza i trigger brevi che Alberto puo' usare per dire a ChatGPT che un'esecuzione Codex o PowerShell e' terminata.

## Trigger Codex

Frasi riconosciute come completamento Codex:

- Codex fatto
- Codex ok
- Codex eseguito
- Codex finito
- CF
- COK
- varianti equivalenti riconducibili al completamento Codex

## Trigger PowerShell

Frasi riconosciute come completamento PowerShell:

- Pwsh fatto
- Pwsh ok
- Pwsh eseguito
- Pwsh finito
- PF
- POK
- PowerShell fatto
- varianti equivalenti riconducibili al completamento PowerShell

## Comportamento operativo atteso in ChatGPT

Quando Alberto usa questi trigger, ChatGPT deve:

1. dedurre lo step atteso dal contesto;
2. cercare automaticamente il report/output nel Bridge, se ha accesso;
3. leggere il file se accessibile;
4. chiedere ad Alberto di incollare solo se il Bridge non e' accessibile, il file non esiste o e' incoerente;
5. classificare lo stato `PASS`, `FAIL`, `BLOCKED`, `LIVE_FAILED_SAFE` o `PARTIAL_PASS`;
6. proporre il prossimo step;
7. non inventare nulla.

## Implementato ora

- `scripts/asf_bridge_report_discovery.py` fornisce la base locale per trovare report/output Bridge in JSON.
- `scripts/asf_handoff_pack_generator.py` puo' includere report Bridge e stato Git nel pacchetto di ripartenza.
- `scripts/asf_prompt_length_advisor.py` puo' valutare un nuovo prompt come guardrail leggero, senza bloccare e senza splitter automatico.

## Convenzione, non automazione completa

La comprensione del trigger dentro ChatGPT e' una convenzione operativa: dipende dall'ambiente in cui ChatGPT puo' o non puo' accedere al Bridge.

Se ChatGPT non vede il filesystem locale o il Bridge Dropbox, deve chiedere ad Alberto di incollare il report/output pertinente.

## Automazioni future

Una futura automazione potra':

- mappare trigger a step corrente leggendo `state.json`;
- scegliere automaticamente `kind=codex` o `kind=pwsh`;
- leggere il file selezionato;
- avviare un intake report controllato.

Questa automazione futura non deve eseguire commit, push, PR, merge, deploy o Codex exec reale senza step separato e approvazione esplicita.

## Limiti

- Nessun polling continuo e' previsto nello STEP 1030.
- Nessun trigger autorizza pubblicazione o merge.
- In caso di ambiguita' tra piu' report, il sistema deve selezionare deterministicamente e segnalare `AMBIGUOUS`.
