# 0200-0280 - Shared Four-Hands Development Backbone

## Scopo

[F] Questo documento definisce il Collaboration Backbone per lavorare a quattro mani sui repository `AI_Software_Factory`, `AI_Release_Radar`, `ASF_Blueprint_Studio` e `Codex_Skills`.

[F] Il backbone nasce per separare codice versionato, decisioni operative, prompt, report, skills e segreti, mantenendo Alberto Ferrari e Luca nel controllo umano del processo.

[S] Il backbone e' una base documentale iniziale: diventa operativo solo dopo review umana, applicazione manuale ai singoli repository e verifica dei permessi reali.

[O] La scelta prudente e' trattare questo pack come standard comune, ma applicarlo per fasi piccole e reversibili.

## Decisioni

- [F] Il Collaboration Backbone viene versionato in `AI_Software_Factory` come riferimento comune.
- [F] Il pack copre GitHub, Dropbox Bridge, ChatGPT Projects, Codex Skills, AGENTS.md, branch/PR/gate, review/merge e segreti.
- [F] Questo step non esegue trasferimenti GitHub, modifiche Organization, cambi permessi, branch protection, commit, push, PR, merge o deploy.
- [S] La futura Organization GitHub e' proposta, non applicata.
- [O] Il rollout deve partire da un pilot piccolo su `ASF_Blueprint_Studio`.
## Progetti coperti

- [F] `AI_Software_Factory`: metodo, runner, gate, template e documentazione comune.
- [F] `AI_Release_Radar`: primo progetto pilota reale basato su ASF.
- [S] `ASF_Blueprint_Studio`: progetto candidato a pilot successivo del backbone.
- [F] `Codex_Skills`: repository/sorgente delle skills comuni da sincronizzare in modo controllato.

## Ruoli

| Ruolo | Responsabilita' | Confine operativo |
|---|---|---|
| Alberto | Strategia, priorita', approvazioni, merge controllati | Non delega merge o segreti agli agenti senza policy esplicita |
| Luca | Sviluppo, review, micro-step controllati, manutenzione condivisa | Opera su branch e PR, non su main diretto salvo regola umana separata |
| ChatGPT/GPT | Pianificazione, review indipendente, handoff, analisi rischi | Non e' fonte ufficiale del codice o delle decisioni persistenti |
| Codex | Esecuzione locale controllata, modifica file, report verificabili | Non decide autonomamente commit, push, PR, merge, deploy o segreti |
| PowerShell | Runner deterministici, verifiche, dry-run, report | Safe-by-default; niente azioni distruttive senza flag e consenso esplicito |

## Architettura GitHub + Dropbox + ChatGPT Projects + Codex Skills

[F] GitHub resta la fonte ufficiale del codice, della documentazione stabile, dei template e degli script versionati.

[F] Dropbox Bridge resta spazio operativo per prompt, report, log e handoff temporanei; non deve contenere repository Git come working copy principale.

[F] ChatGPT Projects contiene contesto e handoff, ma non sostituisce file versionati come `docs/11_DECISIONS.md`, roadmap o ADR.

[F] Codex usa `AGENTS.md` e le skill disponibili come istruzioni persistenti, ma ogni repository mantiene le proprie regole locali.

[S] Una GitHub Organization comune riduce dispersione e rende piu' semplice gestire ruoli, CODEOWNERS, PR review e repository condivisi.

## Regole operative

- [F] Codice, documenti stabili, template e script versionabili stanno nei repository Git.
- [F] Prompt, report, log e handoff operativi stanno nel Bridge con nomi numerati/datati.
- [F] Segreti, token e credenziali non stanno in Git, Dropbox, chat o report.
- [F] Codex esegue modifiche locali controllate e report, ma non decide merge o permessi reali.
- [F] PowerShell deve essere dry-run/read-only per default salvo flag esplicito e consenso umano.
- [S] Organization, branch protection, CODEOWNERS e permessi sono rollout manuali successivi.
- [O] Ogni applicazione del backbone deve partire da micro-step e PR draft.
## Confini tra codice, documenti, prompt, report e segreti

| Tipo | Fonte ufficiale | Dove puo' stare | Dove non deve stare |
|---|---|---|---|
| Codice | Repository Git | Repo, branch, PR | Dropbox Bridge come sorgente primaria |
| Documenti stabili | Repository Git | `docs/`, `templates/`, `AGENTS.md` | Solo chat non versionata |
| Prompt operativi | Bridge o template versionato | Bridge numerato/datato, `templates/` | File `LAST-*` o `latest-*` condivisi |
| Report runtime | Bridge | `codex_command`, `pwsh_command`, `shared_reports` | Repo, salvo report stabili approvati |
| Segreti | Account/tool dedicati | Secret manager, GitHub Secrets, `.env` locale ignorato | Git, Dropbox, chat, log, report |

## Tabella decisioni 0200-0280

| Step | Decisione | Documento specialistico | Stato |
|---|---|---|---|
| 0200 | Creare un backbone comune per collaborazione Alberto-Luca | Questo documento | [F] Definito in questo pack |
| 0210 | Preferire Organization GitHub per collaborazione stabile | `0210_GITHUB_ORG_REPO_PLAN.md` | [S] Proposta manuale, non eseguita |
| 0220 | Onboarding Luca con checklist verificabile | `0220_LUCA_ONBOARDING_CHECKLIST.md` | [F] Checklist preparata |
| 0230 | Usare ChatGPT Projects come contesto, non sorgente ufficiale | `0230_CHATGPT_PROJECTS_HANDOFF_POLICY.md` | [F] Policy documentata |
| 0240 | Sincronizzare skills comuni da `Codex_Skills` con dry-run e backup | `0240_CODEX_SKILLS_SYNC_SPEC.md` | [F] Specifica e script base preparati |
| 0245 | Standardizzare AGENTS.md globale/repo e template condiviso | `0245_AGENTS_MD_POLICY.md` | [F] Policy e template preparati |
| 0250 | Separare Bridge condiviso per progetto e utente | `0250_DROPBOX_BRIDGE_SHARED_SPEC.md` | [S] Struttura proposta, non creata automaticamente |
| 0260 | Usare branch di step, PR draft, gate e review | `0260_BRANCH_PR_GATE_WORKFLOW.md` | [F] Workflow documentato |
| 0270 | Separare autore, reviewer e executor | `0270_REVIEW_AND_MERGE_POLICY.md` | [F] Policy documentata |
| 0280 | Vietare segreti in Git, Dropbox, chat e report | `0280_SECRETS_AND_CREDENTIALS_POLICY.md` | [F] Policy documentata |

## Roadmap di rollout

1. [F] Versionare il backbone in `AI_Software_Factory` come standard comune.
2. [S] Fare review Alberto/GPT del pack e dei template.
3. [S] Applicare un pilot piccolo ad `ASF_Blueprint_Studio` senza trasferimenti GitHub automatici.
4. [S] Applicare la struttura Bridge condivisa con `New-SharedBridgeStructure.ps1` prima in dry-run.
5. [S] Preparare Organization e trasferimenti repository solo con checklist 0210 completata.
6. [S] Abilitare CODEOWNERS, PR template e branch protection solo dopo decisione umana separata.

## Criterio fonte ufficiale

[F] Un'informazione e' fonte ufficiale se si trova in uno di questi punti:

- repository Git nella branch principale approvata;
- PR approvata e tracciata;
- documento decisionale versionato come `docs/11_DECISIONS.md` o equivalente;
- configurazione GitHub visibile e verificata manualmente;
- secret manager o impostazioni GitHub Secrets, senza esporre valori.

[S] Chat, Bridge e report sono fonti operative temporanee: possono motivare un cambiamento, ma la decisione stabile deve entrare nel repo.

## Rischi principali e mitigazioni

| Rischio | Impatto | Mitigazione |
|---|---|---|
| Repo Git in Dropbox | Conflitti, corruzione working tree, copie divergenti | Bridge solo per prompt/report/log; repo fuori Dropbox |
| Permessi GitHub troppo ampi | Merge o modifiche non controllate | Ruoli minimi, branch protection, review obbligatoria |
| Decisioni perse in chat | Divergenza operativa | Decisioni importanti in docs versionati |
| Skills sovrascritte a mano | Comportamenti diversi tra PC | Sync dry-run, backup, report, hash/lista file |
| Segreti nei report | Compromissione credenziali | `.env` locale ignorato, GitHub Secrets, scan minimo |
| Codex decide troppo | Azioni non autorizzate | AGENTS.md, prompt con forbidden actions, review umana |

## Checklist

- [ ] [F] Tutti i repository coinvolti hanno `AGENTS.md` locale.
- [ ] [F] Esiste una fonte ufficiale per decisioni e roadmap.
- [ ] [S] La Organization GitHub e' stata scelta ma non ancora applicata automaticamente.
- [ ] [S] Il Bridge condiviso e' stato creato in dry-run prima dell'applicazione.
- [ ] [F] I template sono disponibili in `templates/collaboration`.
- [ ] [F] Gli script sono dry-run/read-only per default.
- [ ] [O] Ogni nuovo collaboratore parte da un micro-step read-only.

## Prossimo step consigliato

[O] `0290) Apply Collaboration Backbone to ASF Blueprint Studio Pilot`.