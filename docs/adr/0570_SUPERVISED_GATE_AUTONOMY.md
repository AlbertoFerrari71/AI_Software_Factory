# ADR 0570 — Adozione dell'autonomia supervisionata a gate

**Data:** 2026-06-07
**Stato:** Accepted by Alberto, pending implementation

---

## Contesto

AI Software Factory ha gia' consolidato prompt packet, verification gate, report intake, human approval gate, closure pack, invocation design read-only e adapter OpenAI con gate espliciti.

La rotta precedente stava pero' rischiando di accumulare meta-processo senza chiudere un ciclo operativo completo. Lo STEP 0570 corregge la priorita': prima un motore minimo supervisionato a gate, poi ulteriori raffinamenti.

Lo STEP 0560 resta separato: il provider-side block OpenAI e' documentato nei file 0560 e non autorizza retry, nuove live call o nuove evidence in questo step.

---

## Problema

ASF deve aumentare autonomia senza diventare fire-and-forget.

I rischi principali sono:

- esecuzione di step successivi senza evidence sufficiente;
- promozione automatica di output incompleti o fuori scope;
- confusione tra test automatici, revisione indipendente e approvazione umana;
- crescita di nuovi guardrail isolati prima di avere un loop end-to-end;
- live run, costi API, merge o deploy attivati senza gate espliciti.

Serve un modello che lasci il motore lavorare, ma lo fermi a ogni punto in cui rischio, scope o confidence richiedono controllo.

---

## Decisione

ASF adotta l'autonomia supervisionata a gate.

Il motore futuro deve avanzare attraverso stati espliciti, produrre evidence per ogni transizione e fermarsi quando i gate non passano. L'autonomia e' ammessa solo dentro un perimetro dichiarato, con risk classifier L0-L4, review indipendente e decisione finale di gate.

La sequenza MVP del motore diventa:

```text
0570 -> 0580 -> 0590 -> 0600 -> 0610 -> 0620 -> 0630
```

Nuovi step di meta-processo, naming, packaging, validazioni strict o guardrail isolati sono congelati finche' il motore non completa almeno un giro end-to-end dry-run.

---

## Alternative considerate

### Fire-and-forget

Il motore pianifica, esegue, testa, committa o prepara pubblicazione senza fermate intermedie.

Scartata perche' contraddice la missione ASF: safe, repeatable, diagnosable, human-gated automation. Aumenta il rischio di drift, scope creep, costi API live, merge errati e modifiche non reversibili.

### Conferma umana a ogni step

Ogni micro-transizione richiede conferma di Alberto.

Scartata come default perche' riduce troppo il valore del motore. Resta valida per L3/L4, bassa confidence, scope ambiguo, test falliti o decisioni che coinvolgono costi, segreti, deploy, merge o repository esterni.

### Solo test automatici

Il motore procede se pytest, verify gate o smoke check passano.

Scartata perche' i test non coprono da soli scope, intenti, qualita' del diff, documentazione, rischio operativo e output incompleti. I test sono necessari ma non sufficienti.

### Gate condizionale

Il motore procede automaticamente solo quando rischio, scope, test, review indipendente e confidence superano criteri espliciti.

Accettata. E' coerente con il principio local-first e human-gated: autonomia dove il rischio e' basso e l'evidence e' forte, stop o revisione umana dove il rischio cresce.

---

## Conseguenze positive

- La roadmap torna orientata a un MVP operativo del motore.
- Il motore puo' avanzare senza chiedere conferme inutili su stati L0/L1 ben evidenziati.
- Gli step L3/L4 restano bloccati o human-gated.
- La revisione indipendente diventa nodo esplicito, non commento opzionale.
- Le future esecuzioni Codex controllate sono precedute da dry-run, risk report e gate decision.
- Il progetto riduce la proliferazione di meta-processo non validato end-to-end.

---

## Rischi residui

- Un classifier troppo permissivo puo' sottostimare rischio reale.
- Una review indipendente basata sugli stessi input puo' condividere bias o omissioni del primo agente.
- Evidence incompleta puo' essere scambiata per confidence alta se il gate non e' severo.
- Il loop dry-run puo' sembrare piu' maturo del motore write reale.
- L3/L4 richiedono ancora responsabilita' umana e non devono essere convertiti in autorizzazioni implicite.

Mitigazione: fail closed, evidence obbligatoria, STOP condition esplicite, nessun commit/push/PR/merge automatico nello MVP e primo pilot write solo dopo end-to-end dry run verificato.

---

## Impatto sulla roadmap

La priorita' passa da ulteriori raffinamenti meta-operativi e retry live separati a MVP Motore:

- 0570 - ADR + MVP Motor Roadmap;
- 0580 - Dry-run Loop Runner;
- 0590 - Risk Classifier + Gate Policy;
- 0600 - Independent Review Node;
- 0610 - Controlled Codex Executor;
- 0620 - First End-to-End Dry Run;
- 0630 - First Controlled Write Pilot.

Fino al completamento di almeno un giro end-to-end dry-run, i nuovi step di meta-processo non essenziali restano congelati.
