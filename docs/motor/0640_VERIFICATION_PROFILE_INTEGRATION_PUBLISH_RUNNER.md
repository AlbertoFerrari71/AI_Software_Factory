# 0640 - Verification Profile Integration with Publish Runner

## 1. Scopo

Lo STEP 0640 integra il Verification Profile Selector dello STEP 0630 con il Publish Runner dello STEP 0590.

L'integrazione e' prudente:

- le config legacy senza campi profilo continuano a funzionare senza invocare il selector;
- le config che dichiarano un profilo vengono validate dal selector locale;
- un profilo dichiarato piu' leggero del profilo raccomandato blocca il runner;
- il selector che fallisce chiuso blocca il runner;
- Phase B e Phase C restano human-gated.

Il runner non copia le regole del selector. Usa il selector come fonte locale della raccomandazione e mantiene nel PowerShell solo la validazione del contratto.

---

## 2. Campi config opzionali

Campi supportati:

```text
verification_profile
risk_level
changed_files
verification_phase
allow_profile_check_reduction
profile_selector_input
profile_selector_expected_profile
intent
checks_already_run
provided_gates
```

`verification_profile` e `profile_selector_expected_profile` indicano il profilo dichiarato. Se sono entrambi presenti devono coincidere.

`changed_files` alimenta il selector. Se manca, il runner usa `expected_files` come scope di fallback.

`profile_selector_input` puo' essere un path JSON verso un input del selector oppure un oggetto JSON con campi compatibili.

`allow_profile_check_reduction` ha default `false`.

---

## 3. Regole fail-closed

Il runner blocca quando:

- il selector non esiste o non restituisce JSON valido;
- il selector restituisce `fail_closed: true`;
- il profilo dichiarato e' sconosciuto;
- `verification_profile` manca ma sono presenti campi di integrazione profilo;
- `risk_level` e' L4 e il profilo dichiarato non e' `high-risk`;
- il profilo dichiarato e' piu' leggero del profilo raccomandato;
- `allow_profile_check_reduction` e' true ma il profilo raccomandato non e' `docs-only` o `code-unit`;
- `allow_profile_check_reduction` e' true ma Phase C non contiene check robusti.

La scala prudente usata per la validazione e':

```text
docs-only < code-unit < publish < motor-core < final-main < high-risk
```

Per intento publish, `publish`, `motor-core`, `final-main` e `high-risk` sono profili adeguati. Profili piu' leggeri non lo sono.

---

## 4. Phase B e Phase C

Phase B resta invariata sul piano dei gate:

- richiede sempre `-ApprovePublish`;
- riesegue Phase A internamente;
- controlla scope file;
- esegue diff check;
- non fa merge.

Phase C resta invariata sul piano dei gate:

- richiede sempre `-ApproveMerge`;
- verifica PR/check;
- fa merge solo nella fase esplicitamente approvata;
- esegue i `phase_c_checks`;
- verifica `main` e working tree clean.

Lo STEP 0640 non riduce Phase C. Anche quando `allow_profile_check_reduction` e' true, il report indica `Phase C reduction: disabled`.

---

## 5. Output Bridge

I file Bridge gia' prodotti dal runner restano compatibili:

```text
NNNN-Richiesta_Generazione_<nome>.txt
NNNN-Comando_Eseguito_<nome>.ps1
NNNN-Output_Completo_<nome>.txt
NNNN-Output_Compatto_<nome>.md
NNNN-Output_Compatto_<nome>.docx
LAST-*
```

Quando la config contiene campi profilo, l'output include:

- profilo dichiarato;
- profilo raccomandato;
- esito validazione;
- `fail_closed` del selector;
- riduzione check abilitata o no;
- riduzione Phase C;
- motivazioni e warning principali.

Quando la config legacy non contiene profilo, l'output riporta:

```text
Verification profile validation: not configured
```

---

## 6. Esempi

Esempi publish config:

```text
examples/publish_step/0640_publish_config_motor_core.example.json
examples/publish_step/0640_publish_config_docs_only.example.json
examples/publish_step/0640_publish_config_profile_mismatch_fail_closed.example.json
```

L'esempio mismatch dichiara `docs-only` su `scripts/asf_publish_step.ps1`: il selector raccomanda `motor-core`, quindi il runner deve bloccare.

---

## 7. Impatto sui tempi

La riduzione tempi attesa e' prudente:

- le config publish possono dichiarare il profilo e non ripetere decisioni manuali gia' codificate;
- Phase B evita ancora il lancio separato di Phase A, perche' la riesegue internamente;
- docs-only e code-unit possono abilitare riduzioni locali esplicite;
- motor-core, publish, final-main e high-risk restano conservativi;
- Phase C resta robusta e non ridotta nello STEP 0640.

Il beneficio principale e' ridurre ambiguita' e duplicazioni di configurazione, non tagliare gate finali.

---

## 8. Verifica

Test mirati:

```powershell
python -m pytest tests/unit/test_asf_publish_step_runner.py -q
python -m pytest tests/unit/test_asf_verification_profile_selector.py -q
```

Gate repository:

```powershell
python -m pytest -q
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git --no-pager diff --check
git status --short --untracked-files=all
```

---

## 9. Stato dopo STEP 0650

Lo STEP 0650 ha aggiunto un generator che produce bozze config compatibili con questo runner:

```text
scripts/asf_publish_config_generator.py
examples/publish_config_generator/
docs/motor/0650_VERIFICATION_PROFILE_DRIVEN_PUBLISH_CONFIG_GENERATOR.md
```

Il runner resta l'unico componente operativo per Phase A/B/C. Il generator prepara la config, ma non esegue il runner e non sostituisce `-ApprovePublish` o `-ApproveMerge`.

## 10. Prossimo step

## 10. Stato dopo STEP 0660

Lo STEP 0660 ha aggiunto un Bridge dedicato al generator:

```text
docs/motor/0660_PUBLISH_CONFIG_GENERATOR_BRIDGE_OUTPUT_INTEGRATION.md
examples/publish_config_generator/sample_bridge_output_input.json
```

Il runner resta l'unico componente operativo per Phase A/B/C.

`LAST-Publish_Config.json` del generator puo' essere usato come input del runner, ma non sostituisce review umana, `-ApprovePublish`, numero PR o `-ApproveMerge`.

Il prossimo step consigliato e':

```text
0670) Step Execution State Machine
```
