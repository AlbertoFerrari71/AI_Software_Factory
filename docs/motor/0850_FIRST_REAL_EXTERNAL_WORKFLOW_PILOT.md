# STEP 0850 - First Real External Workflow Pilot

## 1. Scopo dello step

Lo STEP 0850 prepara il primo External Workflow Pilot Pack per provare AI
Software Factory su una repository esterna in modo controllato, documentato e
non pubblicante.

L'obiettivo e' scegliere il target piu' prudente, definire il rischio,
preparare il piano operativo, indicare le safety boundaries, descrivere
l'evidence attesa e lasciare un manifest esempio validabile.

Questo step non esegue il pilot esterno. Prepara lo step successivo.

## 2. Prerequisiti 0800-0840

Il pilot esterno parte solo dopo la catena post-MVP gia' pubblicata su `main`:

- 0800: native command guardrail nel publish runner;
- 0805: skill/template PowerShell allineati al runner ASF provato;
- 0810: scope discovery, recovery UX e no-false-completed guard;
- 0820: retry/fallback Bridge e LAST validation;
- 0830: pilot operativo reale post-hardening;
- 0840: runner hook evidence manifest post-publish pack.

Prima di qualunque futuro pilot esterno va ricontrollato `main`, il commit
atteso dello step precedente e il working tree del repository corrente.

## 3. Cosa significa external workflow pilot

Per external workflow pilot intendiamo una prova ASF su un repository diverso
da `AI_Software_Factory`, con output controllati e human gate esplicito.

Nel primo ciclo esterno il target viene usato per osservare readiness, stato Git,
scope, piano dry-run e proposta locale. Non viene usato per pubblicare o
automatizzare modifiche.

## 4. Fuori scope

Restano fuori scope per lo STEP 0850:

- accesso operativo a repository esterne;
- modifica di `Codex_Skills`, `Family_Photo_Organizer` o altri repository;
- esecuzione di workflow reali su progetti esterni;
- sync di skill installate;
- commit, push, PR, merge, deploy o tag;
- cancellazioni o cleanup distruttivi;
- configurazioni capaci di pubblicare automaticamente.

## 5. Candidate repo

Le candidate documentate sono:

- `Codex_Skills`, percorso probabile
  `C:\Users\alberto.ferrari\.agents\skills` o remote
  `AlbertoFerrari71/Codex_Skills`;
- `Family_Photo_Organizer`, percorso probabile
  `C:\Users\alberto.ferrari\source\repos\Family_Photo_Organizer`;
- `AI_Software_Factory`, solo come quasi-external dry pilot fallback;
- `Mansionario_Vivo`, escluso come primo pilot esterno per rischio alto.

I percorsi sono solo candidati testuali. Questo step non li usa come dipendenza
di test e non li modifica.

## 6. Confronto candidati

| Candidate repo | Value | Risk | Why / Why not | Recommended |
|---|---:|---:|---|---|
| Codex_Skills | 3 | 1 | Repo reale ma non produttiva, vicina a skill/template, impatto limitato, utile per validare coerenza del metodo ASF su materiale operativo leggero. | Yes, default |
| Family_Photo_Organizer | 3 | 2 | Progetto reale e utile, ma safety-sensitive e con rischio maggiore; meglio usarlo dopo un dry-run esterno riuscito. | Future candidate |
| AI_Software_Factory self-pilot fallback | 2 | 1 | Prudente se non e' opportuno uscire dal repository, ma meno rappresentativo di un vero target esterno. | Fallback only |
| Mansionario_Vivo | 2 | 3 | Progetto piu' operativo/produttivo; non e' adatto come primo pilot esterno controllato. | No |

## 7. Repo consigliata

La repo consigliata per il primo pilot esterno controllato e' `Codex_Skills`.

Motivi:

- e' reale ma non produttiva;
- e' collegata direttamente a skill e template;
- ha impatto limitato rispetto a un'applicazione operativa;
- puo' validare allineamenti di contenuto senza toccare sistemi produttivi;
- ha rischio inferiore rispetto a progetti applicativi come
  `Family_Photo_Organizer` o `Mansionario_Vivo`.

## 8. Rischio stimato

Rischio stimato del pilot consigliato: `L1`, solo se il futuro step resta
read-only o dry-run e non modifica repository esterne.

Il rischio sale almeno a `L2` se il futuro step propone modifiche locali su una
repo esterna. Il rischio sale ulteriormente se include publishing, secret,
dati personali, deploy o sistemi produttivi.

## 9. Safety boundaries

Safety boundaries obbligatorie:

- nessun write su repository esterne nello STEP 0850;
- nel futuro STEP 0860, default read-only;
- nessun commit, push, PR, merge, deploy o tag da Codex;
- nessuna cancellazione o cleanup distruttivo;
- nessun accesso a secret, token o credenziali;
- nessuna dipendenza dei test da path locali esterni;
- output del pilot come report, dry-run plan e changed-files preview;
- human gate obbligatorio prima di qualunque proposta di modifica;
- stop immediato se la repo esterna e' sporca, sensibile o non compresa.

## 10. Flusso operativo proposto

Flusso proposto per il pilot esterno futuro:

1. verificare prerequisito su `main` di ASF;
2. confermare target `Codex_Skills`;
3. ispezionare solo in read-only branch, log e status della repo esterna;
4. produrre repo readiness report;
5. generare dry-run plan senza modifiche;
6. produrre changed-files preview solo se esistono modifiche proposte;
7. classificare rischio;
8. presentare human gate;
9. fermarsi prima di qualunque write o pubblicazione.

## 11. Checklist pre-pilot

- `AI_Software_Factory` e' su `main` e contiene lo step precedente richiesto.
- Working tree ASF pulito o modifiche note.
- Target esterno scelto esplicitamente.
- Scopo limitato a read-only/dry-run.
- Nessun secret richiesto.
- Nessun comando di pubblicazione previsto.
- Criteri stop accettati.
- Human gate esplicito prima di qualunque passo operativo oltre il read-only.

## 12. Checklist post-pilot

- Report readiness prodotto.
- Piano dry-run prodotto.
- Rischio classificato.
- Nessuna repo esterna modificata.
- Nessun commit, push, PR, merge, deploy o tag eseguito.
- Evidence salvata in output locali o Bridge operativo, se richiesto.
- Proposta eventuale di modifica minima separata dal pilot.
- Prossimo step deciso da Alberto.

## 13. Evidence attesa

Evidence attesa per il futuro pilot:

- repo readiness report;
- branch corrente e working tree della repo target;
- log sintetico degli ultimi commit target;
- dry-run plan;
- changed-files preview;
- risk assessment;
- human approval gate;
- stop reason in caso di blocco;
- conferma no-publish.

## 14. Criteri di successo

Il pack 0850 e' pronto se:

- `Codex_Skills` e' raccomandata come prima candidata;
- `Family_Photo_Organizer` resta candidata futura con rischio maggiore;
- `Mansionario_Vivo` e' esclusa come primo pilot per rischio alto;
- safety boundaries e human gate sono espliciti;
- il manifest esempio e' `planning_only`;
- i test coprono documento e manifest;
- le verifiche locali ASF passano;
- nessuna repo esterna e' stata modificata.

## 15. Criteri di stop

Fermare il futuro pilot se:

- il prerequisito ASF richiesto non e' su `main`;
- la repo esterna non e' identificata con certezza;
- il target e' sporco e le modifiche non sono comprese;
- il target contiene secret o dati sensibili non necessari;
- serve scrivere fuori dal perimetro approvato;
- serve commit, push, PR, merge, deploy o tag;
- il rischio supera `L1` senza nuova approvazione umana;
- un check read-only fallisce in modo non spiegato.

## 16. Runbook minimo per STEP 0860

Runbook sintetico per il futuro step 0860, senza eseguirlo ora:

1. verificare repo esterna candidata;
2. controllare branch corrente;
3. leggere stato Git;
4. eseguire solo controlli read-only;
5. produrre piano dry-run;
6. proporre eventuale modifica minima come proposta separata;
7. attendere human gate;
8. non fare commit, push, PR, merge, deploy o tag.

## 17. Prossimo step operativo suggerito

```text
0860) Codex_Skills External Workflow Dry-Run Pilot
```

Motivo: `Codex_Skills` e' il target piu' adatto per validare il primo pilot
esterno reale mantenendo rischio basso, confini leggibili e nessuna
pubblicazione automatica.
