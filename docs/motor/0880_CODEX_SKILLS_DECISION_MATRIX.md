# STEP 0880 - Codex_Skills Decision Matrix

| Opzione | Descrizione | Pro | Contro | Rischio | Quando sceglierla | Raccomandazione |
|---|---|---|---|---|---|---|
| A) Rollback del file 0870 | Rimuovere il file locale `docs/asf_external_pilot/0870_CONTROLLED_WRITE_PILOT.md` dopo approvazione umana | Ripulisce `Codex_Skills`; chiude il pilot dimostrativo; evita residui locali | Il file non resta come doc permanente nella repo esterna | Basso | Quando l'obiettivo era solo dimostrare il write controllato | Default consigliato |
| B) Keep local temporaneo | Lasciare il file untracked per breve review manuale | Permette ispezione locale senza decidere subito | Lascia repo dirty; rischio dimenticanza se prolungato | Basso nel breve, crescente nel tempo | Solo se Alberto vuole leggere il file prima della decisione | Sconsigliata oltre breve periodo |
| C) Commit controllato futuro su Codex_Skills | Pubblicare il file in repo esterna con step separato e gate esplicito | Conserva una traccia permanente del pilot in `Codex_Skills` | Richiede commit reale; serve review di naming, posizione e utilita' | L1/L2 | Solo se Alberto decide che il file deve diventare documentazione permanente | Solo con approvazione esplicita e step separato |

## Raccomandazione

Default: A) rollback.

C) future controlled commit e' ammessa solo con approvazione esplicita e step
separato. B) keep local temporaneo e' accettabile solo per una review breve e
non deve diventare lo stato permanente della repo esterna.
