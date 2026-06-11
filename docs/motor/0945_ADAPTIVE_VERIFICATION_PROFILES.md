# 0945 - Adaptive Verification Profiles

## Scopo

Lo STEP 0945 estende il selector storico dei verification profile con quattro profili operativi per il supervised loop:

- `LIGHT`
- `STANDARD`
- `FULL`
- `ESCALATED`

La riduzione dei test e' ammessa solo negli step intermedi a basso rischio. I gate forti restano pieni.

## Script

```text
scripts/asf_verification_profile_selector.py
```

Lo script mantiene i profili legacy `docs-only`, `code-unit`, `motor-core`, `publish`, `final-main` e `high-risk` per retrocompatibilita'. In aggiunta emette:

- `selected_profile`;
- `required_commands`;
- `optional_commands`;
- `skipped_commands`;
- `rationale`;
- `escalation_reasons`;
- `full_required`;
- `stop_reasons`.

## Regole profili

| Profilo | Uso | Comandi minimi |
|---|---|---|
| `LIGHT` | docs-only o template-only L0/L1 durante iterazione | diff check, workflow health, test workflow health mirato |
| `STANDARD` | code-unit o docs indicizzati con rischio medio ma chiaro | `LIGHT` piu' `scripts\verify.ps1` |
| `FULL` | Phase C, milestone, runner/core/test/API/security, retry sospetti | `STANDARD` piu' `python -m pytest` |
| `ESCALATED` | fallimenti ripetuti, rischio L3/L4, falso PASS sospetto, path vietato, input ambiguo | `FULL` piu' stop/ASK_ALBERTO se la causa non e' chiara |

## FULL obbligatorio

`FULL` resta obbligatorio per:

- Phase C o verifica finale;
- milestone;
- modifiche a runner, core, test, API o sicurezza;
- retry sospetti;
- rischio alto.

## Stop policy

`ESCALATED` non autorizza automazione piu' ampia. Indica che il loop deve fermarsi o chiedere Alberto se:

- il path e' vietato;
- la causa del fallimento non e' chiara;
- il retry sarebbe una ripetizione cieca;
- serve approval, credenziale, publish, merge o deploy;
- il retry count raggiunge il max retry assoluto 10.

## Non azioni

Il selector non esegue test, non pubblica, non apre PR, non chiama API live e non invoca Codex exec.
