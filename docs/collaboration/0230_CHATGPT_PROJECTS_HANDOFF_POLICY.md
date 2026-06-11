# 0230 - ChatGPT Projects and Handoff Policy

## Scopo

[F] Questo documento definisce come Alberto e Luca usano ChatGPT Projects per contesto, pianificazione e review, senza trasformare la chat nella fonte ufficiale del progetto.

[F] La fonte ufficiale del codice e delle decisioni persistenti resta il repository Git.

[S] ChatGPT Projects e' utile per mantenere contesto operativo tra piu' chat, ma puo' contenere informazioni obsolete se non sincronizzate con i file versionati.

## Decisioni

- [F] ChatGPT Projects e' spazio di contesto, non sorgente ufficiale del codice.
- [F] Le decisioni importanti entrano in `docs/11_DECISIONS.md`, ADR, roadmap o file equivalente del repository.
- [F] Handoff e report operativi possono stare nel Bridge, ma non sostituiscono docs versionati.
- [S] Le chat operative usano titoli numerati a passo 10 per orientare le sessioni.
- [O] Alberto e Luca dovrebbero evitare decisioni finali solo in chat.

## Regola titoli chat numerati

[S] Schema consigliato:

```text
0200 - Shared Four-Hands Backbone - Planning
0210 - GitHub Org Plan - Review
0220 - Luca Onboarding - Execution
0290 - ASF Blueprint Studio Pilot - Codex
```

[O] Usare passo 10 lascia spazio a sotto-sessioni intermedie, ad esempio `0215`.

## Uso handoff

Un handoff efficace contiene:

- [F] repository e branch;
- [F] obiettivo dello step;
- [F] file ammessi e vietati;
- [F] azioni vietate;
- [F] test richiesti;
- [F] stato Git iniziale se noto;
- [S] rischi attesi;
- [O] prossimo step consigliato.

## Uso manifesto/progetto

[F] Il manifesto di progetto deve rimandare ai documenti versionati principali: README, roadmap, decision log, AGENTS.md e documenti di workflow.

[S] Un manifesto ChatGPT puo' contenere sintesi e link, ma deve dichiarare quando una decisione e' solo proposta.

[O] Ogni progetto condiviso dovrebbe avere una pagina iniziale con: scopo, repo, branch principale, Bridge, regole Git, test e policy segreti.

## Passaggio contesto Alberto-Luca

1. [F] Chi produce lo step salva report o handoff in posizione concordata.
2. [F] Il reviewer legge diff, report e test, non solo il riassunto in chat.
3. [F] Le decisioni accettate vengono copiate in docs versionati.
4. [F] Le ipotesi restano marcate come [S] finche' non verificate.
5. [O] Quando il contesto e' lungo, creare un riepilogo operativo prima di cambiare chat.

## Come evitare decisioni perse nella chat

- [F] Ogni decisione con effetto su repo, permessi, segreti, workflow o merge va versionata.
- [F] Ogni decisione temporanea deve avere scadenza o prossimo check.
- [F] Ogni prompt Codex importante deve indicare se puo' modificare file, commit, push o PR.
- [S] Le chat possono restare utili come storico, ma non sono audit trail sufficiente.

## Regole operative

- [F] Non incollare segreti in ChatGPT Projects.
- [F] Non usare chat come unica fonte per branch protection, token, ruoli o permessi.
- [F] Non considerare un report Codex come merge su `main`.
- [O] Usare ChatGPT come reviewer indipendente prima della review umana finale.

## Rischi

| Rischio | Mitigazione |
|---|---|
| Decisione valida solo in chat | Trasferire in `docs/11_DECISIONS.md` o ADR |
| Contesto vecchio | Citare commit, branch e data nel handoff |
| Confusione tra proposta e fatto | Usare `[F]`, `[S]`, `[O]` |
| Chat troppo lunghe | Creare riepilogo operativo e nuovo thread numerato |

## Checklist

- [ ] [F] Titolo chat numerato.
- [ ] [F] Repo, branch e step indicati.
- [ ] [F] Confini file/azioni indicati.
- [ ] [F] Decisioni importanti versionate.
- [ ] [F] Segreti assenti.
- [ ] [S] Handoff Bridge o repo creato se serve.

## Prossimo step consigliato

[O] Integrare questa policy nei progetti ChatGPT condivisi prima del pilot 0290.