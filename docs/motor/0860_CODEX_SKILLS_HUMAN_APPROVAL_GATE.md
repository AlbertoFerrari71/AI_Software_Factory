# STEP 0860 - Codex_Skills Human Approval Gate

## 1. Decisione 0860

Decisione per lo step corrente:

```text
GO_FOR_READ_ONLY_DRY_RUN_COMPLETED
```

Motivo: la repo esterna e' stata ispezionata solo in lettura, risulta
accessibile, pulita e coerente con il target atteso. Nessun write e' stato
eseguito.

## 2. Gate per 0870

Decisione richiesta prima di qualunque futuro write:

```text
HUMAN APPROVAL REQUIRED BEFORE ANY EXTERNAL WRITE
```

## 3. Informazioni da approvare

Alberto deve approvare esplicitamente:

- file esterno esatto;
- obiettivo della modifica;
- rischio stimato;
- comandi di verifica;
- criterio di rollback;
- conferma che Codex non deve fare commit, push, PR, merge, deploy o tag.

## 4. Default sicuro

Default se manca una qualsiasi informazione:

```text
HOLD
```

## 5. Stop condition

Fermare il futuro step se:

- `git status --short` della repo esterna non e' clean;
- la modifica proposta tocca piu' file o piu' skill senza motivo forte;
- serve rigenerare cataloghi senza regola chiara;
- serve un comando di sync o publish;
- il rischio supera `L2`;
- il gate umano non e' esplicito.

## 6. Conferma no-write 0860

Nessuna repo esterna e' stata modificata nello step 0860.
