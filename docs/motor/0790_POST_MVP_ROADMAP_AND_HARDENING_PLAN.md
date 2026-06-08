# 0790 - Post-MVP Roadmap and Hardening Plan

## 1. Scopo dello step

Lo STEP 0790 ferma l'espansione del Motore ASF dopo la chiusura MVP e i tre
pilot reali, e consolida la fase successiva prima di aggiungere altra
automazione.

Obiettivo operativo:

- registrare cosa e' gia' stabile;
- raccogliere warning, debiti e frizioni emersi tra STEP 0560 e STEP 0780;
- trasformare le lezioni apprese in criteri pratici;
- decidere cosa automatizzare e cosa lasciare human-gated;
- proporre una roadmap post-MVP ordinata, con hardening prima di automazione
  piu' spinta.

Questo step non implementa nuove automazioni, non pubblica, non apre PR e non
modifica il publish runner.

## 2. Stato attuale post-MVP

Il Motore ASF MVP e' formalmente chiuso come:

```text
MVP STATUS: GO WITH WARNINGS
```

Stato consolidato:

- il flusso end-to-end e' stato dimostrato in locale;
- il manifest/evidence pack e' disponibile;
- tre pilot reali post-MVP sono stati eseguiti;
- runner, state machine, publish config generator, Bridge e manifest sono
  collegati in modo significativo;
- gli hook runner/state machine funzionano quando abilitati;
- il manifest puo' includere evidenza dei runner hooks;
- il sistema resta human-gated;
- lo stato non e' ancora "fire-and-forget".

Decisione post-MVP:

```text
POST-MVP DECISION: HARDENING FIRST
```

Il Motore ASF e' usabile come baseline locale verificabile, ma non deve ancora
essere trattato come automazione autonoma ordinaria.

## 3. Componenti gia' disponibili

Componenti principali gia' versionati:

- dry-run loop runner;
- stable PowerShell publish runner;
- risk classifier e gate policy;
- gate decision report e approval packet umano;
- verification profile selector;
- publish config generator;
- output Bridge del publish config generator;
- step execution state machine;
- output Bridge della state machine;
- integrazione state machine nel generator;
- end-to-end MVP smoke scenario;
- motor run manifest and evidence pack;
- MVP usage runbook;
- closure pack MVP;
- publish runner state machine event hooks;
- manifest hook-aware con sezione `runner_hooks`;
- pilot reali 0740, 0760 e 0780.

Questi componenti coprono preparazione, evidence, review, configurazione,
state tracking e pubblicazione human-gated. Non coprono ancora esecuzione
autonoma senza review.

## 4. Lezioni apprese dagli STEP 0560-0780

Lezioni operative principali:

- i runner devono essere fail-closed;
- i `LAST-*` sono utili come alias operativi, ma non sono fonte autorevole
  unica;
- Git, file versionati, branch, PR e config devono combaciare;
- Phase B contiene la verifica equivalente alla Phase A, quindi una Phase A
  separata e' spesso ridondante per step ordinari;
- Phase C resta obbligatoria per verifica finale su `main`;
- gli hook aiutano l'audit trail, ma non sostituiscono review umana;
- recovery combinati devono essere dichiarati esplicitamente;
- smoke sintetico e pilot reale non sono la stessa cosa;
- PowerShell richiede controllo esplicito di `$LASTEXITCODE` dopo comandi
  nativi come `git`, `gh`, `python` e `pwsh`;
- gli argomenti vuoti nei wrapper PowerShell sono pericolosi;
- i recovery delicati devono essere racchiusi in blocchi `& { ... }`;
- `COMPLETATO` va stampato solo dopo tutti i gate/check con exit code 0;
- un file Bridge recente non prova da solo che branch, PR e main siano nello
  stato corretto;
- una config pronta non equivale ad approval per publish o merge.

## 5. Warning residui

Warning residui da mantenere espliciti:

- il Motore ASF e' ancora human-gated;
- il publish runner e' potente e deve restare vincolato da approval esplicite;
- `LAST-*` puo' diventare stale o riferirsi a step/branch diversi;
- le evidenze Bridge sono operative, non autorevoli rispetto a Git e file
  versionati;
- il manifest post-publish hook-aware va generato/verificato dopo Phase B/C
  reali;
- la recovery richiede ancora review e diagnosi manuale;
- il costo dei profili di verifica puo' essere migliorato, ma non a scapito
  del fail-closed;
- LF/CRLF puo' produrre warning non bloccanti, ma non deve mascherare errori
  reali;
- la skill `as-common-pwsh-command-pack` deve recepire le lezioni sui comandi
  nativi PowerShell.

## 6. Problemi emersi nei recovery

I recovery hanno mostrato frizioni concrete:

- `$ErrorActionPreference = "Stop"` non basta per fermare errori di comandi
  nativi;
- senza controllo di `$LASTEXITCODE`, un wrapper puo' proseguire dopo un
  errore;
- argomenti vuoti passati a `git`, `gh`, `python` o `pwsh` possono produrre
  comportamenti ambigui;
- flussi lunghi possono stampare `COMPLETATO` anche se un gate precedente e'
  fallito;
- recovery combinati possono confondere cosa e' stato corretto, pubblicato o
  verificato;
- branch, PR, config e Bridge possono divergere se non vengono validati insieme;
- evidence post-publish e state machine vanno riconciliate con il risultato
  reale su `main`, non solo con artifact temporanei.

## 7. Priorita' hardening

Priorita' consigliate:

1. PowerShell command safety hardening.
2. Publish runner recovery UX.
3. No-false-completed guard nei wrapper e nei command pack.
4. State machine / manifest evidence integration post-publish.
5. Bridge output consistency e validazione dei riferimenti `LAST-*`.
6. Verification profile tuning.
7. Real pilot playbook per step piccoli ma piu' operativi.
8. Line ending / LF/CRLF cleanup opzionale, solo se non distrae dai gate.
9. Skill update per `as-common-pwsh-command-pack`.

## 8. Cosa automatizzare

Automazioni sensate nella fase post-MVP:

- validazione fail-closed degli argomenti PowerShell prima di invocare comandi
  nativi;
- wrapper comuni per eseguire comandi nativi con controllo exit code;
- controlli di coerenza tra step, branch, PR, config e artifact Bridge;
- generazione di summary recovery chiari;
- validazione che `LAST-*` punti allo step atteso o venga degradato a warning;
- manifest post-publish con runner hooks e state file reali;
- check locali read-only per evidence mancanti o stale;
- suggerimento del verification profile, senza ridurre gate obbligatori.

## 9. Cosa lasciare human-gated

Non automatizzare ancora:

- merge senza `-ApproveMerge`;
- publish senza `-ApprovePublish`;
- deploy;
- recovery complessa senza review;
- modifiche high-risk;
- pilot reali troppo grandi;
- sostituzione della review umana con decisione automatica;
- bypass di Phase C per velocita';
- decisione GO piena quando warning operativi restano aperti.

## 10. Roadmap post-MVP proposta

Roadmap consigliata:

```text
0800) PowerShell Native Command Guardrail Hardening
0810) Publish Runner Recovery UX and No-False-Completed Guard
0820) Bridge Output Consistency and LAST Validation
0830) MVP Real Step Pilot 4 - Slightly More Operational
0840) Runner Hook Evidence Manifest Post-Publish Pack
0850) Verification Profile Cost Tuning
0860) Post-MVP Hardening Closure
```

Sequenza motivata:

- 0800 riduce il rischio piu' concreto emerso nei recovery: comandi nativi
  PowerShell non fermati correttamente;
- 0810 migliora la UX dei recovery senza aumentare autonomia;
- 0820 rende piu' robusta la lettura degli output Bridge;
- 0830 prova il flusso su un pilot reale leggermente piu' operativo;
- 0840 completa la catena post-publish runner -> state machine -> manifest;
- 0850 ottimizza il costo test solo dopo aver reso sicuri wrapper e recovery;
- 0860 chiude il blocco hardening con decisione GO/WARNING/NO-GO.

## 11. Criteri per nuovi pilot reali

Un nuovo pilot reale post-MVP deve rispettare questi criteri:

- scope piccolo e versionabile;
- nessun deploy;
- nessun segreto o dato privato in artifact;
- rischio L0-L2, salvo approvazione esplicita;
- file attesi e branch dichiarati;
- config publish verificata prima di Phase B;
- Phase B con `-ApprovePublish`;
- Phase C con `-ApproveMerge`;
- manifest/evidence post-publish generabile;
- warning dichiarati, non nascosti;
- rollback o recovery manuale descritta se applicabile.

Un pilot piu' grande va spezzato prima di entrare nel Motore.

## 12. Criteri per introdurre nuove automazioni

Una nuova automazione puo' entrare nella roadmap solo se:

- preserva i gate umani;
- fallisce chiusa su input incoerenti;
- non legge segreti e non richiede Dropbox/GitHub reali nei test unitari;
- usa artifact temporanei sotto `tmp/` nei test;
- distingue output operativo da fonte autorevole;
- ha test mirati;
- documenta recovery e stop condition;
- non riduce Phase C;
- non trasforma warning residui in successo pieno.

## 13. Raccomandazione finale

Raccomandazione:

```text
NEXT STEP: 0800) PowerShell Native Command Guardrail Hardening
```

Motivo: la lezione piu' urgente emersa nel recovery 0780 e' che la sicurezza
PowerShell dei comandi nativi deve essere standardizzata prima di migliorare UX,
Bridge consistency o pilot piu' operativi. Se i wrapper non bloccano exit code,
argomenti vuoti e falsi `COMPLETATO`, ogni automazione successiva eredita un
rischio operativo troppo alto.

Il Motore ASF puo' proseguire, ma la fase corretta e' hardening controllato,
non aumento immediato dell'autonomia.

## 13.1 Aggiornamento dopo STEP 0800

Lo STEP 0800 ha consolidato lo standard PowerShell per comandi nativi nel
publish runner e nei template command-pack repository-local in:

```text
docs/motor/0800_POWERSHELL_NATIVE_COMMAND_GUARDRAIL_HARDENING.md
```

Il prossimo step consigliato dopo il guardrail hardening e':

```text
0810) Publish Runner Recovery UX and No-False-Completed Guard
```
