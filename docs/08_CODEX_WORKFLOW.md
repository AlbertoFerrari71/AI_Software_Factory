# 08 — Codex Workflow

## 1. Obiettivo

Definire come usare Codex CLI e Codex Cloud/Web senza perdere controllo.

---

## 2. Modalità consentite

| Modalità | Uso | Regola |
|---|---|---|
| Ask only | Analisi, review, spiegazioni | Nessuna modifica |
| Suggest | Proposte e patch suggerite | Revisione umana |
| Auto Edit | Modifica controllata su branch | Solo file ammessi |
| Full Auto | Task sandbox non distruttivi | Non usare per L3/L4 |

---

## 3. Regole obbligatorie

Codex deve sempre ricevere:

- task ID;
- obiettivo;
- branch;
- file da leggere;
- file modificabili;
- file da non toccare;
- test;
- criteri di accettazione;
- rischi;
- cosa non fare.

---

## 4. Divieti standard

Codex non deve:

- fare commit automatico salvo richiesta;
- fare push automatico salvo richiesta;
- fare merge;
- fare force push;
- cancellare file o dati;
- modificare credenziali;
- aggirare test falliti;
- introdurre dipendenze senza motivazione.

---

## 5. Output finale richiesto a Codex

Ogni task Codex deve terminare con:

- file modificati;
- riepilogo diff;
- test eseguiti;
- test non eseguiti;
- rischi residui;
- rollback consigliato;
- prossimo passo.
