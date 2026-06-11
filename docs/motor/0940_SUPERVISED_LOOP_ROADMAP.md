# 0940 - Supervised Loop Roadmap

## Scopo

Questa roadmap trasforma l'architettura 0940 in step piccoli. Non anticipa ASF V2 e non abilita pubblicazione automatica.

| Step | Tipo | Obiettivo | Output atteso | Gate | Rischio | Criterio di successo |
|---:|---|---|---|---|---|---|
| 0950 | Documentale/protocollo | Definire Bridge State and Semaphore Protocol | Schema `state.json`, naming flag, directory, lock policy, report minimi | `python -m pytest`, workflow health, verify, diff check | Basso | Protocollo Bridge verificabile senza esecuzione live |
| 0960 | Implementativo leggero | Creare PowerShell Fast Task Runner | Runner locale deterministico per envelope autorizzati | Test unitari, fake commands, timeout, no destructive commands | Medio | Esegue solo task allowlisted e salva report Bridge |
| 0970 | Implementativo leggero | Creare PowerShell Error Recovery Loop | Watchdog, timeout, failure class, retry envelope, stop policy | Test fake-hang, fake-stderr, fake-timeout, workflow health | Medio | Classifica errori e ferma/rilancia solo nei casi sicuri |
| 0980 | Implementativo controllato | Creare GPT Prompt Generator API Adapter | Adapter dry-run/mock per planner/reviewer, nessuna live call default | Test mock, no secret, no network by default | Medio | Produce prompt/review JSON senza eseguire tool |
| 0990 | Implementativo controllato | Creare Codex Exec Runner Adapter | Adapter preview/default e invocazione controllata futura | Safety gate, repo dirty check, sandbox policy | Medio-alto | Prepara o esegue solo quando lo step lo autorizza |
| 1000 | Documentale/implementativo | Definire Auto Review and Step Decision Policy | Policy PASS/FIX/STOP/ASK_ALBERTO e scoring evidence | Test decision matrix, esempi failure | Medio | Decisioni ripetibili e fail-closed |
| 1010 | Smoke test | Final End-to-End Smoke Test | Run sintetica supervised loop completa su tmp/ | Full pytest, workflow health, verify, diff check | Medio | Loop dimostra plan -> lane -> review -> verify -> stop/pass senza publish automatico |

## Sequenza consigliata

La sequenza piu' logica dopo 0940 e':

```text
0950) Bridge State and Semaphore Protocol
0960) PowerShell Fast Task Runner
0970) PowerShell Error Recovery Loop
0980) GPT Prompt Generator API Adapter
0990) Codex Exec Runner Adapter
1000) Auto Review and Step Decision Policy
1010) Final End-to-End Smoke Test
```

Il primo passo deve essere 0950 per rendere stabile il contratto `state.json`/flag/report prima di implementare runner o adapter.

## Stato dopo 0980-1010

Il batch 0980-1010 ha implementato la versione mock/dry-run di:

- `0980) GPT Prompt Generator API Adapter`;
- `0990) Codex Exec Runner Adapter`;
- `1000) Auto Review and Step Decision Policy`;
- `1010) Final End-to-End Smoke Test`.

Il prossimo passo consigliato e':

```text
1020) GPT Prompt Generator Live Controlled Run
```
