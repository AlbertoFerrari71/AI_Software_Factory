# 0220 - Luca Onboarding Checklist

## Scopo

[F] Questo documento definisce la checklist iniziale per abilitare Luca a lavorare sui repository ASF con micro-step controllati.

[S] La checklist assume Windows/PowerShell come ambiente principale, coerente con il metodo locale usato da Alberto.

[O] Luca dovrebbe completare prima un micro-step read-only, poi un micro-step documentale con PR draft.

## Decisioni

- [F] Luca usa un account GitHub personale proprio.
- [F] Luca non usa token, password o account di Alberto.
- [F] Luca lavora su branch di step e PR, non direttamente su `main`.
- [F] ChatGPT/GPT puo' fare review indipendente, ma la fonte ufficiale resta il repository.
- [S] L'accesso Organization viene dato solo dopo decisione manuale su ruoli e repo.

## Checklist account e accessi

- [ ] [F] Account GitHub Luca creato e verificato.
- [ ] [F] 2FA GitHub abilitata se richiesta dalla Organization.
- [ ] [S] Luca invitato nella Organization o nel repo specifico.
- [ ] [S] Ruolo assegnato: Owner, Admin, Maintain o Write secondo decisione Alberto.
- [ ] [S] Accesso Dropbox condiviso attivato solo alle cartelle Bridge necessarie.
- [ ] [S] Accesso ChatGPT Projects condivisi configurato secondo disponibilita' del piano e policy.

## Checklist workstation

- [ ] [F] Git installato e disponibile: `git --version`.
- [ ] [F] GitHub CLI installata e disponibile: `gh --version`.
- [ ] [F] PowerShell disponibile: `$PSVersionTable.PSVersion`.
- [ ] [F] Python disponibile se richiesto dal repo: `python --version`.
- [ ] [S] Codex installato o verificato secondo policy locale.
- [ ] [F] Editor configurato senza auto-format globale indesiderato.

## Checklist Git iniziale

```powershell
git config --global user.name "Nome Cognome"
git config --global user.email "email-personale@example.com"
gh auth status
git clone <repo-url>
cd <repo>
git branch --show-current
git status --short
```

[F] I comandi sopra sono esempi documentali: vanno eseguiti manualmente da Luca, non automaticamente da Codex.

## Verifica repository

- [ ] [F] Repository clonato fuori da Dropbox.
- [ ] [F] Branch corrente verificato.
- [ ] [F] `git status --short` pulito.
- [ ] [F] `AGENTS.md` letto.
- [ ] [F] `README.md`, `docs/10_ROADMAP.md` e `docs/11_DECISIONS.md` letti.
- [ ] [F] Cartelle `docs/collaboration`, `templates/collaboration`, `scripts/collaboration` presenti se il backbone e' stato applicato.

## Skills

- [ ] [F] Distinzione compresa tra skills comuni e skills locali del repo.
- [ ] [S] `Codex_Skills` usato come fonte ufficiale per skills comuni.
- [ ] [S] Sync eseguito prima in dry-run.
- [ ] [F] Backup creato prima di ogni overwrite reale.
- [ ] [F] Report sync salvato e letto.

## Primo test read-only

1. [F] Aprire PowerShell nel repository.
2. [F] Eseguire `git status --short`.
3. [F] Eseguire `python scripts/check_workflow_health.py` se presente.
4. [F] Eseguire `scripts/collaboration/Test-CollaborationReadiness.ps1` se presente.
5. [F] Salvare un report locale o Bridge numerato, senza `LAST-*` o `latest-*` se la policy del repo lo vieta.

## Primo micro-step controllato

- [S] Tipo consigliato: L0 documentazione o checklist read-only/quasi read-only.
- [F] Vietato includere segreti.
- [F] Vietato modificare branch protection, permessi o Organization.
- [F] Vietato fare commit/push/PR/merge se il prompt non lo autorizza esplicitamente.
- [O] Il primo micro-step dovrebbe chiudersi con report e review Alberto/GPT, non con merge automatico.

## Problemi tipici e soluzioni

| Problema | Sintomo | Soluzione prudente |
|---|---|---|
| Git non in PATH | `git` non riconosciuto | Verificare installazione Git for Windows e riaprire terminale |
| gh non autenticato | `gh auth status` fallisce | Eseguire `gh auth login` manualmente con account Luca |
| Repo clonato in Dropbox | File conflicted copy o lock | Riclonare fuori Dropbox, usare Bridge solo per report |
| Branch sbagliato | Branch non atteso | Fermarsi, chiedere ad Alberto, non fare reset/clean |
| Skills diverse | Codex risponde in modo incoerente | Eseguire sync dry-run da `Codex_Skills`, poi backup/apply autorizzato |
| Test falliscono | Gate rosso | Classificare causa: step, preesistente o ambiente; non inventare PASS |

## Regole operative

- [F] Ogni fatto nel report deve citare comando, file o fonte.
- [F] Non usare clipboard per report condivisi.
- [F] Non committare `.env` o credenziali.
- [F] Non usare `--no-verify`.
- [O] Usare PR draft per il primo contributo reale.

## Rischi

- [S] Permessi troppo larghi aumentano il rischio di merge accidentale.
- [S] Chat non sincronizzate possono produrre decisioni divergenti.
- [F] Token personali condivisi violano la policy segreti.

## Checklist finale onboarding

- [ ] [F] Account e accessi verificati.
- [ ] [F] Tool locali verificati.
- [ ] [F] Repo clonato fuori Dropbox.
- [ ] [F] `AGENTS.md` letto.
- [ ] [F] Primo test read-only eseguito.
- [ ] [S] Primo micro-step controllato pianificato.

## Prossimo step consigliato

[O] Eseguire il prompt `templates/collaboration/luca_first_micro_step_prompt.md` su un repository non critico o su `ASF_Blueprint_Studio` durante lo step 0290.