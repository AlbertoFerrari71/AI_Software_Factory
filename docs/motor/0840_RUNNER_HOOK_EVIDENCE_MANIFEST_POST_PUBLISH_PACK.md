# STEP 0840 - Runner Hook Evidence Manifest Post-Publish Pack

## 1. Scopo

Lo STEP 0840 definisce un post-publish evidence pack per consolidare le
evidenze prodotte o raccolte dopo una pubblicazione ASF riuscita.

Il pack serve a rendere verificabile, in un solo punto, quale step e' stato
pubblicato, quale PR e' stata mergiata, quale commit finale e' arrivato su
`main`, quali check finali sono passati, quali output Bridge e `LAST-*` sono
stati aggiornati, quali warning sono stati accettati e quale prossimo step e'
consigliato.

Questo step non aggiunge pubblicazione automatica. Il flusso resta local-first,
human-gated e fail-closed.

## 2. Contesto 0800-0830

Gli step 0800-0830 hanno consolidato il runner di pubblicazione ASF:

- 0800: guardrail PowerShell per comandi nativi, exit code, `PrNumber` e scope;
- 0805: skill/template PowerShell allineati al flusso config JSON + runner;
- 0810: `PrepareConfig`, scope discovery, recovery out-of-scope e no-false
  `COMPLETATO`;
- 0820: retry/fallback Bridge, compatto Markdown obbligatorio e LAST
  validation;
- 0830: pilot operativo reale, con manifest esempio e validazione prudente
  post-hardening.

Dopo questi step, manca un formato pratico per leggere le evidenze
post-publish come un pacchetto coerente invece che come frammenti separati tra
chat, Bridge, Git, PR e manifest.

## 3. Definizione

Per post-publish evidence pack intendiamo un pacchetto leggibile e auditabile,
preparato dopo una pubblicazione riuscita, che raccoglie:

- step pubblicato e titolo;
- numero PR e stato merge;
- merge commit finale su `main`;
- branch e remote finale verificati;
- check finali passati;
- output Bridge generati;
- `LAST-*` aggiornati o warning sul loro fallback;
- warning accettati e motivo;
- manifest/evidence JSON disponibili;
- prossimo step consigliato.
- next step esplicito per il handoff operativo.

Il pack puo' essere un documento Markdown, un JSON esempio, un manifest
generato da strumenti futuri o una combinazione di questi. In questo step viene
versionato un documento operativo e un JSON esempio non live.

## 4. Evidenze da conservare

Dopo una pubblicazione ASF riuscita, conservare almeno:

- identificativo step, titolo e stato finale;
- PR number, link o riferimento PR, e risultato merge;
- merge commit o short SHA finale su `main`;
- branch locale e remote atteso;
- esito di `python -m pytest`;
- esito di `python scripts/check_workflow_health.py`;
- esito di `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1`;
- esito di `git --no-pager diff --check`;
- esito finale di `git --no-pager status --short`;
- output Bridge completo e compatto;
- `LAST-Output_Completo.txt` e `LAST-Output_Compatto.md`, se aggiornati;
- eventuali fallback Bridge o LAST;
- warning accettati, con causa e criterio di accettazione;
- manifest o evidence JSON collegati;
- prossimo step consigliato.

## 5. Gate, warning, output accessori ed evidence

### Gate bloccanti

Sono gate bloccanti:

- branch o commit finale non coerenti con la pubblicazione attesa;
- PR non mergiata o merge commit mancante;
- test, Workflow Health Check, Verification Gate o diff check falliti;
- working tree finale sporco in modo non spiegato;
- PR checks falliti o non classificati;
- compatto Markdown mancante sia nel path primario sia nel fallback.

Un gate bloccante lascia lo step `BLOCCATO`. Non va convertito in warning.

### Warning accettati

Sono warning accettabili solo se i gate veri passano:

- warning LF/CRLF non accompagnati da errori di `git --no-pager diff --check`;
- `gh pr checks` con "no checks reported" se la config lo consente
  esplicitamente;
- output Bridge o LAST primario bloccato, se fallback e report compatto sono
  disponibili;
- DOCX o output accessori falliti dopo TXT/Markdown validi.

Ogni warning accettato deve indicare perche' non invalida il publish.

### Output accessori

Sono output accessori:

- DOCX;
- wrapper log separati;
- file fallback timestampati;
- screenshot o note manuali;
- artifact temporanei sotto `tmp/`.

Gli output accessori aiutano la diagnosi, ma non sostituiscono i gate.

### Evidence post-publish

L'evidence post-publish e' il pacchetto finale di prova. Non e' una nuova
autorizzazione operativa. Non deve eseguire commit, push, PR, merge, deploy o tag.

## 6. Relazione con Bridge output

Il Bridge e' storage operativo per recuperare rapidamente output completi e
compatti. Dopo STEP 0820 il runner possiede i propri output standard e gestisce
retry/fallback.

Nel post-publish evidence pack, i riferimenti Bridge devono indicare:

- output completo;
- output compatto;
- eventuale DOCX o marker `.failed.txt`;
- fallback usato, se presente;
- se il compatto e' stato copiato negli appunti.

Il Bridge non diventa fonte autorevole. Git, PR mergiata, commit finale e file
versionati restano le fonti primarie.

## 7. Relazione con LAST files

I `LAST-*` del publish runner sono compatibilita' operativa per handoff rapido.
Nel pack vanno riportati come:

- aggiornati sul path primario;
- aggiornati tramite fallback;
- non aggiornati con warning esplicito;
- non applicabili.

Un `LAST-*` aggiornato non prova da solo che la pubblicazione sia chiusa. Serve
sempre l'incrocio con PR, merge commit e verifiche finali.

## 8. Relazione con manifest/evidence JSON

Un manifest JSON post-publish deve essere leggibile da una persona e validabile
da test semplici. Deve contenere almeno:

- `step`;
- `status`;
- `pr_number` o oggetto equivalente;
- `merge_commit` o oggetto equivalente;
- `checks`;
- `bridge_outputs`;
- `next_step`;
- indicatori `is_example` / `not_live_evidence` quando non e' stato generato
  da una run reale.

Se il JSON usa dati reali di uno step gia' pubblicato, deve chiarire se sono
dati derivati dal log/report o evidence live prodotta automaticamente.

## 9. Validazione di chiusura pubblicazione

Una pubblicazione e' davvero chiusa solo se:

1. lo step precedente richiesto e' su `main`;
2. la PR attesa e' mergiata;
3. il commit finale atteso compare su `main`;
4. i check finali locali sono passati;
5. `git --no-pager diff --check` e' passato;
6. il working tree finale e' pulito o le modifiche residue sono spiegate;
7. il report compatto Bridge esiste su path primario o fallback;
8. i warning sono classificati e accettati esplicitamente;
9. il prossimo step e' indicato.

Se uno di questi punti manca, il pack deve indicare `BLOCCATO` o
`COMPLETATO CON WARNING`, non forzare `COMPLETATO`.

## 10. Esempio evidence pack

Esempio derivato dal riepilogo post-publish dello STEP 0830:

```text
step: 0830
step_title: MVP Real Step Pilot 4 - Slightly More Operational
status: published
pr_number: 76
merge_commit: a759546
branch: main
remote: origin/main
checks:
  pytest: 637 passed
  workflow_health: PASS
  verification_gate: PASS
  diff_check: PASS
  working_tree: clean
bridge_outputs:
  compact_output: generated
  last_compact: LAST-Output_Compatto.md copied to clipboard
warnings:
  accepted only when final gates passed
next_step: 0840) Runner Hook Evidence Manifest Post-Publish Pack
```

Il JSON versionato in
`examples/publish_runner/0840_post_publish_evidence_manifest.example.json`
mostra lo stesso schema in forma validabile. E' un esempio, non un output live
del runner.

## 11. Rischi residui

- Un pack scritto manualmente puo' riportare dati incompleti o copiati male.
- Bridge e LAST restano superfici operative e possono essere bloccati da sync,
  editor, preview o antivirus.
- Un warning accettato senza spiegazione puo' nascondere un gate reale fallito.
- Il pack non sostituisce la verifica di Git, PR e commit su `main`.
- I dati reali di una pubblicazione devono essere verificati al momento, non
  assunti da memoria.

## 12. Fuori scope

Restano fuori scope:

- nuova fase runner `EvidenceManifest`;
- generazione automatica obbligatoria del pack;
- commit, push, PR, merge, deploy o tag;
- modifica della skill installata fuori repository;
- accesso al Bridge reale nei test;
- DOCX obbligatorio;
- automazione non approvata di publish o merge.

## 13. Prossimo step consigliato

```text
0850) Verification Profile Cost Tuning
```

Motivo: dopo avere consolidato la tracciabilita' post-publish, il passo naturale
e' ottimizzare costo e profilo dei check senza ridurre i gate fail-closed.
