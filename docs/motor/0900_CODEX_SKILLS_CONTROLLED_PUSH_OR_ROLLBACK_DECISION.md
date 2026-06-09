# STEP 0900 - Codex_Skills Controlled Push or Rollback Decision

## 1. Scopo dello step

Lo STEP 0900 e' uno step decisionale. Analizza il commit locale
`Codex_Skills` creato nello STEP 0890 e prepara una scelta umana tra push
controllato, rollback locale o mantenimento temporaneo.

Questo step non esegue push, rollback, commit, PR, merge, deploy, tag, reset,
clean, cancellazioni o modifiche nella repo esterna.

## 2. Contesto 0860/0870/0880/0890

- STEP 0860: dry-run esterno read-only su `Codex_Skills`.
- STEP 0870: micro-modifica locale documentale in `Codex_Skills`.
- STEP 0880: decision pack per rollback/keep/commit.
- STEP 0890: commit locale controllato del file pilota 0870.

Commit ASF verificati su `main`:

```text
9d9356d 0890 add Codex_Skills controlled local commit execution (#82)
101f400 0880 add Codex_Skills controlled write review decision (#81)
672f3ba 0870 add Codex_Skills controlled write pilot (#80)
e6102fc 0860 add Codex_Skills external workflow dry-run pilot (#79)
```

## 3. Stato ASF

- branch ASF: `main`;
- STEP 0880 presente su `main`;
- STEP 0890 presente su `main` con commit `9d9356d`;
- working tree ASF iniziale: pulita.

Non serve warning su 0890 non pubblicato: lo step risulta gia' pubblicato su
`main`.

## 4. Stato Codex_Skills

Path repo esterna:

```text
C:\Users\alberto.ferrari\.agents\skills
```

Branch:

```text
main
```

Status short:

```text

```

Status `-sb`:

```text
## main...origin/main [ahead 1]
```

Branch `-vv`:

```text
* main b488745 [origin/main: ahead 1] 0870 add ASF controlled write pilot note
```

Remote:

```text
origin  https://github.com/AlbertoFerrari71/Codex_Skills.git (fetch)
origin  https://github.com/AlbertoFerrari71/Codex_Skills.git (push)
```

Interpretazione: la repo esterna e' pulita e il branch locale risulta ahead 1
rispetto al tracking branch locale `origin/main`. Non e' stato fatto fetch, quindi
l'ahead/behind non e' verificato live per vincolo no-fetch.

## 5. Commit locale b488745

Commit osservato:

```text
b488745 0870 add ASF controlled write pilot note
```

Stat:

```text
.../asf_external_pilot/0870_CONTROLLED_WRITE_PILOT.md | 19 +++++++++++++++++++
1 file changed, 19 insertions(+)
```

File incluso:

```text
docs/asf_external_pilot/0870_CONTROLLED_WRITE_PILOT.md
```

## 6. Opzioni decisionali

### A) Push controllato

Pubblicare su `origin/main` il commit locale `b488745`.

Pro:

- chiude il pilot rendendo permanente la documentazione in `Codex_Skills`;
- allinea repo locale e remote;
- mantiene una traccia storica diretta nella repo esterna.

Contro:

- e' una pubblicazione remota reale;
- richiede approvazione esplicita e controllo finale prima del push;
- dopo il push, il rollback dovrebbe preferire un revert pubblico.

Rischio: medio-basso se i guardrail restano puliti e Alberto approva
esplicitamente; piu' alto se eseguito senza review.

### B) Rollback locale

Rimuovere localmente il commit `b488745` se non e' stato pushato.

Pro:

- chiude il pilot senza pubblicazione remota;
- riporta `Codex_Skills` allo stato precedente locale;
- mantiene la traccia storica solo in ASF.

Contro:

- richiede comandi Git di rollback e rimozione file;
- e' distruttivo sul commit locale se eseguito con reset;
- va eseguito solo con path e stato confermati.

Rischio: medio, perche' include reset/rimozione locale e deve restare puntuale.

### C) Keep local temporaneo

Mantenere il commit `b488745` solo locale per una breve review.

Pro:

- non pubblica nulla;
- lascia tempo per review umana;
- conserva un punto locale pronto per push o rollback futuro.

Contro:

- lascia la repo esterna ahead 1;
- rischio di dimenticare il commit locale;
- non e' una soluzione stabile nel lungo periodo.

Rischio: basso nel breve periodo, crescente se resta sospeso troppo a lungo.

## 7. Raccomandazione

Poiche' lo STEP 0890 e' pubblicato su `main` ASF e `Codex_Skills` e' pulita con
`b488745` su `main`, l'opzione A puo' essere considerata nello step successivo
solo con approvazione esplicita di Alberto.

Default operativo immediato: C) keep local temporaneo fino alla decisione
esplicita. Se Alberto vuole chiudere il pilot senza pubblicazione remota,
l'opzione B resta prudente. Se Alberto vuole conservare la nota nella repo
esterna, procedere con A nello step 0910.

## 8. Precondizioni per push

- approvazione esplicita di Alberto;
- `Codex_Skills` su branch `main`;
- status pulito;
- `b488745` ancora HEAD locale;
- file committato unico e atteso;
- remote coerente con `AlbertoFerrari71/Codex_Skills`;
- nessuna azione ASF pendente che blocchi il publish decisionale;
- comando push eseguito solo in step separato.

## 9. Precondizioni per rollback

- approvazione esplicita di Alberto;
- conferma che `b488745` non e' stato pushato;
- `Codex_Skills` su branch `main`;
- status pulito prima del rollback;
- rollback puntuale al commit `b488745`;
- rimozione del file solo con path esplicito, se scelta;
- nessun cleanup ampio, `git clean` o reset non mirato.

## 10. Human gate richiesto

Qualunque opzione A, B o C oltre questo decision pack richiede decisione umana
esplicita. Lo STEP 0900 non esegue nessuna delle tre opzioni.

## 11. Criteri di stop

Fermarsi se:

- `Codex_Skills` non e' su `main`;
- lo status non e' pulito;
- `b488745` non e' presente o non e' HEAD locale;
- il file incluso non e'
  `docs/asf_external_pilot/0870_CONTROLLED_WRITE_PILOT.md`;
- il remote non e' coerente con `AlbertoFerrari71/Codex_Skills`;
- viene richiesto push, rollback, commit, PR, merge, deploy o tag nello stesso
  step decisionale;
- un gate locale ASF fallisce.

## 12. Prossimo step consigliato

```text
0910) Codex_Skills Controlled Push Execution or Local Rollback
```
