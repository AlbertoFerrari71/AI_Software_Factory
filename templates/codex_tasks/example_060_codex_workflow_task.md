# Codex Task Packet - STEP 060 Codex Workflow

## Task ID

ASF-060-CODEX-WORKFLOW

## Titolo

Standardizzare il workflow Codex CLI e Codex Web/Cloud.

## Obiettivo

Aggiornare documentazione, template, prompt e test per rendere verificabile il modo in cui AI Software Factory usa Codex in modalita' Ask/Suggest, Auto Edit controllato, Review e Repair.

## Contesto

Il repository e' nello stato post STEP 050. Lo STEP 060 collega il Safety Model L0-L4 e il GitHub Workflow al lavoro operativo di Codex, senza introdurre logica applicativa reale.

## Branch consigliato

060-codex-workflow

## Livello rischio L0-L4

Livello massimo ammesso: L2 - Write controlled.

Safety level: L2, perche' il task modifica documentazione, template e test su branch dedicato.

## Modalita' Codex consigliata

A) Ask only
B) Suggest
C) Auto Edit controllato
D) Full Auto sandboxed

Default: C

Full Auto non e' ammesso per questo task.

## File da leggere prima

- `README.md`
- `AGENTS.md`
- `docs/05_SECURITY_MODEL.md`
- `docs/08_CODEX_WORKFLOW.md`
- `docs/10_ROADMAP.md`
- `docs/15_GITHUB_WORKFLOW.md`
- `docs/19_PROMPT_PACKET_GENERATOR.md`
- `policies/safety_policy.v0.json`
- `templates/codex_tasks/codex_task_packet_template.md`
- `templates/prompts/codex_ask_only_prompt.md`
- `templates/prompts/codex_code_controlled_prompt.md`
- `templates/prompts/codex_review_prompt.md`
- `templates/prompts/codex_repair_prompt.md`

## File modificabili

- `docs/08_CODEX_WORKFLOW.md`
- `docs/10_ROADMAP.md`
- `docs/checklists/060_CODEX_WORKFLOW_CHECKLIST.md`
- `templates/codex_tasks/codex_task_packet_template.md`
- `templates/codex_tasks/example_060_codex_workflow_task.md`
- `templates/prompts/codex_ask_only_prompt.md`
- `templates/prompts/codex_code_controlled_prompt.md`
- `templates/prompts/codex_review_prompt.md`
- `templates/prompts/codex_repair_prompt.md`
- `tests/unit/test_codex_workflow.py`
- `CHANGELOG.md`
- `TREE.txt`

## File vietati / file da non toccare

- `.env`
- `.env.*`
- `.github/workflows/ci.yml`
- `policies/safety_policy.v0.json`
- `policies/path_policy.v0.json`
- `pyproject.toml`
- `src/**`
- file fuori repository
- credenziali o secret

## Vincoli

- Non introdurre codice applicativo reale.
- Non modificare CI.
- Non modificare policy L0-L4.
- Non introdurre dipendenze.
- Non modificare `src/**`.
- Non fare commit.
- Non fare push.
- Non fare merge.
- Regola sintetica: no commit, no push, no merge.
- Aggiornare roadmap, changelog e TREE.
- Fermarsi se serve un livello superiore a L2.

## Output atteso

1. Step eseguito.
2. Stato sintetico.
3. File creati.
4. File modificati.
5. Test eseguiti.
6. Esito test.
7. Conferma che CI, policy, `src/**`, dipendenze e secret non sono stati toccati.
8. Rischi residui.
9. Prossimo step consigliato.

## Criteri di accettazione

- `docs/08_CODEX_WORKFLOW.md` aggiornato e operativo.
- Checklist 060 presente.
- Esempio task STEP 060 presente.
- Prompt Codex coerenti con no commit, no push, no merge, safety level, file da non toccare e output atteso.
- Test unitari nuovi presenti.
- Roadmap, changelog e TREE aggiornati.
- Nessuna modifica a CI, policy, `src/**`, dipendenze o secret.

## Test / verifica

```powershell
python -m pytest -q
git diff --check
git status
```

## Rollback / safe stop

Rollback L2: ripristinare i file modificati o abbandonare il branch.

Safe stop se:

- il branch corrente non e' `060-codex-workflow`;
- compaiono file fuori scope;
- compaiono secret;
- falliscono test critici;
- serve L3/L4 non approvato;
- il rollback non e' chiaro.

## Cosa NON fare

- Non fare commit.
- Non fare push.
- Non fare merge.
- Non modificare main.
- Non modificare CI.
- Non modificare policy.
- Non modificare `src/**`.
- Non introdurre dipendenze.
- Non inserire credenziali.
