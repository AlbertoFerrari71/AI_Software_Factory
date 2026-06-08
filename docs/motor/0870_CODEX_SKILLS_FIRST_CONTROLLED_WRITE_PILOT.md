# STEP 0870 - Codex_Skills First Controlled Write Pilot

## 1. Scopo dello step

Lo STEP 0870 esegue il primo controlled write pilot locale su una repository
esterna candidata, `Codex_Skills`, partendo dal dry-run 0860.

Lo scopo e' dimostrare che AI Software Factory puo' preparare, autorizzare con
guardrail e svolgere una micro-modifica documentale esterna mantenendo:

- scope minimo;
- human gate;
- nessun commit/push/PR/merge/deploy/tag;
- rollback plan esplicito;
- evidence pack versionato in `AI_Software_Factory`;
- separazione netta tra write locale e pubblicazione Git.

## 2. Riferimento a 0860

Prerequisito verificato su `main`:

```text
e6102fc 0860 add Codex_Skills external workflow dry-run pilot (#79)
```

Lo STEP 0860 aveva gia' prodotto readiness report, changed-files preview,
human approval gate ed evidence manifest per `Codex_Skills` senza modificare la
repo esterna.

## 3. Prerequisiti

Prerequisiti verificati in `AI_Software_Factory`:

- branch: `main`;
- STEP 0860 presente negli ultimi commit;
- working tree iniziale pulito.

Prerequisiti verificati in `Codex_Skills`:

- path esistente: `C:\Users\alberto.ferrari\.agents\skills`;
- repo Git valida;
- branch: `main`;
- status prima del write: clean;
- remote: `https://github.com/AlbertoFerrari71/Codex_Skills.git`;
- log leggibile, HEAD osservato: `36b065d 150) Add installed skills sync checker`.

## 4. Guardrail

Azioni vietate e non eseguite:

- commit;
- push;
- apertura PR;
- merge;
- deploy;
- tag;
- pull/fetch/switch/checkout/rebase/reset/clean;
- installazione, disinstallazione o sync automatico skill;
- modifica di branch remoti;
- cancellazione di file non richiesta.

Azioni consentite:

- controlli read-only su `Codex_Skills`;
- una sola micro-scrittura locale, documentale, non funzionale e reversibile;
- controllo finale `git status --short` sulla repo esterna.

## 5. Controlli read-only eseguiti su Codex_Skills

Comandi read-only eseguiti prima del write:

```powershell
git -C "C:\Users\alberto.ferrari\.agents\skills" branch --show-current
git -C "C:\Users\alberto.ferrari\.agents\skills" status --short
git -C "C:\Users\alberto.ferrari\.agents\skills" remote -v
git -C "C:\Users\alberto.ferrari\.agents\skills" log --oneline --max-count=10
```

Esito:

- branch rilevato: `main`;
- status prima: clean, output vuoto;
- remote coerente con `AlbertoFerrari71/Codex_Skills`;
- ultimi commit leggibili.

## 6. Esito readiness

Readiness sintetica: `GO_FOR_LOCAL_CONTROLLED_WRITE`.

Questo e' un local controlled write: non e' una pubblicazione Git e non abilita
azioni remote.

Il write locale e' stato consentito perche' tutti i guardrail richiesti erano
verificati:

- repo esterna pulita;
- branch `main`;
- remote coerente;
- modifica documentale/non funzionale;
- scope esplicito;
- nessun commit/push/PR/merge/deploy/tag;
- rollback plan prodotto.

## 7. Micro-modifica eseguita

Micro-modifica eseguita localmente in `Codex_Skills`:

```text
docs/asf_external_pilot/0870_CONTROLLED_WRITE_PILOT.md
```

La modifica e':

- piccola;
- documentale;
- non funzionale;
- locale;
- non committata;
- non pushata;
- reversibile tramite rollback manuale dopo review umana.

## 8. File esterno creato

File esterno creato:

```text
C:\Users\alberto.ferrari\.agents\skills\docs\asf_external_pilot\0870_CONTROLLED_WRITE_PILOT.md
```

Contenuto: nota Markdown di pilot locale con stato `local-only`, conferma
`not committed`, `not pushed`, non release, safety statement e richiesta di
human review per qualunque azione successiva.

## 9. Conferma no publish

Conferma esplicita:

- nessun commit/push/PR/merge e' stato eseguito;
- nessun deploy e' stato eseguito;
- nessun tag e' stato creato;
- nessuna pubblicazione Git e' stata avviata;
- nessuna sync skill e' stata eseguita.

Questo step distingue il write locale esterno dalla pubblicazione Git. Il file
rimane in working tree locale di `Codex_Skills` fino a review umana.

## 10. Rollback plan

Rollback documentato in:

```text
docs/motor/0870_CODEX_SKILLS_ROLLBACK_PLAN.md
```

Comando suggerito, da eseguire solo dopo review umana:

```powershell
Remove-Item -Path "C:\Users\alberto.ferrari\.agents\skills\docs\asf_external_pilot\0870_CONTROLLED_WRITE_PILOT.md"
```

Non eseguire rollback automatico in STEP 0870.

## 11. Evidence

Evidence ASF prodotta:

- `docs/motor/0870_CODEX_SKILLS_FIRST_CONTROLLED_WRITE_PILOT.md`;
- `docs/motor/0870_CODEX_SKILLS_CONTROLLED_WRITE_RESULT.md`;
- `docs/motor/0870_CODEX_SKILLS_ROLLBACK_PLAN.md`;
- `examples/publish_runner/0870_codex_skills_controlled_write_evidence.example.json`;
- `tests/unit/test_codex_skills_first_controlled_write_pilot.py`.

Status finale osservato su `Codex_Skills`:

```text
?? docs/asf_external_pilot/
```

## 12. Criteri di successo

Lo step 0870 e' riuscito se:

- STEP 0860 e' presente su `main`;
- i guardrail read-only su `Codex_Skills` passano prima del write;
- il write locale e' minimo, documentale e reversibile;
- nessun commit/push/PR/merge/deploy/tag viene eseguito;
- gli artefatti ASF documentano result report, rollback plan, evidence e test;
- i test e i gate locali ASF passano;
- il report finale distingue write esterno locale e publish Git.

## 13. Criteri di stop

Fermare lo step e produrre solo piano/readiness se:

- `AI_Software_Factory` non e' su `main`;
- STEP 0860 non e' presente su `main`;
- `AI_Software_Factory` ha dirty files inattesi;
- `Codex_Skills` non e' su `main`;
- `Codex_Skills` non e' clean prima del write;
- il remote non e' coerente con `AlbertoFerrari71/Codex_Skills`;
- la modifica richiesta non e' documentale, minima o reversibile;
- servirebbe commit, push, PR, merge, deploy, tag o sync skill.

## 14. Prossimo step consigliato

```text
0880) Codex_Skills Controlled Write Review and Rollback/Commit Decision
```

Lo step 0880 dovra' decidere, con review umana separata, se rimuovere il file
locale oppure preparare una futura pubblicazione controllata. Lo STEP 0870 non
anticipa quella decisione.
