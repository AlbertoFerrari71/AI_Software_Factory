# STEP 0921 - Publish Runner PowerShell Compatibility Regression Fix

## Scopo

Questo step corregge le regressioni del publish runner PowerShell emerse
durante il tentativo di pubblicazione dello STEP 0920. Il blocco era corretto:
i test specifici 0920 e Workflow Health passavano, ma il full pytest non
passava e non doveva essere bypassato.

## Sintesi failure

Le aree segnalate erano:

- accesso diretto a `$PSNativeCommandUseErrorActionPreference` sotto
  `Set-StrictMode`;
- output DOCX Bridge non sempre generato come zip/docx valido;
- compatibilita' `ProcessStartInfo.ArgumentList` e normalizzazione argomenti
  durante `PrepareConfig` e scope discovery;
- messaggio recovery out-of-scope oscurato da errori infrastrutturali;
- state hooks Phase B/Phase C non sempre raggiunti se il runner falliva prima.

## Root cause accertate

1. `Invoke-NativeChecked` leggeva direttamente
   `$PSNativeCommandUseErrorActionPreference`. In ambienti PowerShell dove la
   variabile non esiste, `Set-StrictMode -Version Latest` puo' bloccare il
   runner prima dei messaggi attesi.
2. `Invoke-NativeStdoutChecked` usava `ProcessStartInfo.ArgumentList`, che non
   e' disponibile in runtime piu' vecchi basati su .NET Framework.
3. `Write-MinimalDocx` dipendeva solo da
   `[System.IO.Compression.ZipArchive]`; se l'assembly non era caricato o non
   disponibile, il DOCX accessorio falliva.
4. STEP 0921-B: i JSON generati da PrepareConfig e dalla recovery
   out-of-scope venivano scritti con `Set-Content -Encoding UTF8`; in Windows
   PowerShell 5.1 questo puo' produrre UTF-8 con BOM.

## Fix applicati

- Aggiunto salvataggio/ripristino sicuro di
  `PSNativeCommandUseErrorActionPreference` tramite `Get-Variable` e
  `Set-Variable`, con rimozione sicura se la variabile non esisteva prima.
- Aggiunta compatibilita' `ProcessStartInfo`: usa `.ArgumentList` quando
  disponibile, altrimenti costruisce una stringa `Arguments` quotata.
- Aggiunto caricamento esplicito degli assembly `System.IO.Compression`.
- Aggiunto fallback Python standard library
  `scripts/asf_minimal_docx.py` per produrre un DOCX zip valido, non un file
  testuale rinominato.
- STEP 0921-B: aggiunto writer `.NET` UTF-8 senza BOM per i JSON runner
  generati da PrepareConfig e recovery suggested config.
- Aggiunto test regressione
  `tests/unit/test_publish_runner_powershell_compat_regression_fix.py`.

## Compatibilita' PowerShell 5.1 / 7+

Il runner non assume piu' che
`$PSNativeCommandUseErrorActionPreference` o
`ProcessStartInfo.ArgumentList` esistano. Su PowerShell 7+ mantiene il
comportamento corrente; su runtime piu' vecchi usa fallback compatibili senza
ridurre i guardrail.

## DOCX validi

Il DOCX Bridge resta accessorio e best-effort, ma quando viene creato deve
essere un vero zip/docx valido con almeno:

- `[Content_Types].xml`;
- `_rels/.rels`;
- `word/document.xml`.

Il fallback Python usa solo `zipfile` dalla standard library.

## PrepareConfig e ArgumentList

La discovery stdout-only non dipende piu' dalla proprieta' `.ArgumentList`.
Questo evita che `PrepareConfig` e recovery scope falliscano prima di arrivare
al messaggio operativo atteso.

I JSON draft config e suggested recovery config sono prodotti in UTF-8 senza
BOM, cosi' restano leggibili con `path.read_text(encoding="utf-8")` e
`json.loads(...)` senza scorciatoie `utf-8-sig`.

## Out-of-scope recovery e state hooks

I fix infrastrutturali lasciano riemergere i comportamenti gia' previsti:

- out-of-scope blocca con `Out-of-scope changes detected`;
- recovery/suggested config resta disponibile;
- `phase_b_started`, `phase_b_failed`, `phase_c_started` e `phase_c_failed`
  non vengono nascosti da errori di compatibilita' PowerShell.

## Test eseguiti

Test mirati richiesti:

```powershell
python -m pytest tests/unit/test_asf_publish_step_runner.py -q
python -m pytest tests/unit/test_asf_publish_config_generator.py tests/unit/test_asf_publish_step_scope_discovery.py tests/unit/test_asf_step_state_machine.py -q
python -m pytest tests/unit/test_codex_skills_remote_verification_evidence_closure.py tests/unit/test_workflow_health_check.py -q
python -m pytest tests/unit/test_asf_publish_step_scope_discovery.py::test_prepare_config_generates_draft_config_without_warning_paths tests/unit/test_asf_publish_step_scope_discovery.py::test_out_of_scope_blocks_and_writes_recovery_suggested_config -q
```

Gate finali richiesti:

```powershell
python -m pytest -q
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1
git --no-pager diff --check
```

## Cosa resta da fare

Riprovare la pubblicazione controllata del pacchetto locale 0920 + 0921 con un
nuovo comando PowerShell dedicato. Non procedere a 0930 prima di avere una
pubblicazione riuscita del fix e della closure 0920.

## Prossimo step consigliato

```text
0920 publish retry after 0921 fix
```
