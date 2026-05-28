# Prompt Packet Hardening

## 1. Purpose

Prompt Packet Hardening makes operational prompts and Codex Task Packets safer, more repeatable, and less ambiguous.

The goal is practical control: each future step should tell Codex exactly what to do, what not to do, which files are in scope, which files are forbidden, which checks must run, and which final report must be returned.

---

## 2. Core principle

Every task packet must clearly state:

- what to do;
- what not to do;
- which branch to work on;
- which files may be touched;
- which files must not be touched;
- which verification commands must run;
- which final report Codex must produce.

If Codex needs to leave the approved scope, it must stop and report the gap instead of guessing.

---

## 3. Required task packet sections

Future task packets should include these sections:

- Project context;
- Completed steps;
- Current branch and target branch;
- Objective;
- Allowed scope;
- Forbidden scope;
- Forbidden actions;
- Required changes;
- Verification commands;
- Documentation Sync;
- Verification Gate;
- Soft Protection awareness;
- Final Codex report.

The exact wording can vary, but the operational content must be present.

---

## 4. Forbidden actions standard block

Use this block as the default forbidden actions list:

- Non fare commit.
- Non fare push.
- Non aprire PR.
- Non fare merge.
- Non modificare direttamente GitHub.
- Non applicare branch protection/rulesets.
- Non installare hook Git.
- Non modificare git config core.hooksPath.
- Non usare bypass ASF_ALLOW_MAIN_BYPASS.
- Non modificare secret, .env o configurazioni sensibili.
- Non modificare src/** se non esplicitamente richiesto.
- Non introdurre nuove dipendenze se non esplicitamente autorizzato.

Add step-specific forbidden actions when needed.

---

## 5. Allowed scope / forbidden scope rule

Every task packet must include:

- explicit allowed scope;
- explicit forbidden scope;
- a stop rule for scope expansion.

Stop rule:

```text
Se serve uscire dallo scope, fermati e segnala la modifica minima necessaria.
```

Do not use broad wording such as "update everything needed" without naming the expected areas.

---

## 6. Documentation Sync integration

Every step must evaluate:

- `CHANGELOG.md`;
- `docs/10_ROADMAP.md`;
- `docs/11_DECISIONS.md`;
- specific documents involved by the step.

Not every document must be updated on every step, but the evaluation must be explicit. The final report must say which central documents were updated or why they were not needed.

---

## 7. Verification Gate integration

Every task packet must list verification commands.

Default commands:

```powershell
python -m pytest
git diff --check
git status --short
```

When applicable, include:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

Add step-specific checks when needed. If a check is not executed, Codex must explain why.

---

## 8. Soft Protection awareness

Codex must know that:

- `main` is treated as protected;
- GitHub hard protection is not available on the current private repository and plan;
- soft guardrails are opt-in;
- Codex must not install hooks;
- Codex must not run `git config core.hooksPath`;
- Codex must not use `ASF_ALLOW_MAIN_BYPASS`.

Soft Protection reduces local mistakes but does not replace GitHub hard protection.

---

## 9. Final Codex report standard

Every implementation task must end with this structure:

```text
A) STEP ESEGUITO
B) STATO
C) FILE CREATI
D) FILE MODIFICATI
E) VERIFICHE ESEGUITE
F) VERIFICHE NON ESEGUITE
G) RISCHI / NOTE
H) PROSSIMO STEP CONSIGLIATO
I) RIEPILOGO FINALE OBBLIGATORIO
```

Section `I` must include:

- Step eseguito;
- Tempo impiegato;
- Stato step;
- Prossimo step.

The report must also state whether tests were run, whether CI/policy/src/dependencies/secrets were touched, and whether any requested check was skipped.

---

## 10. Anti-patterns

Avoid:

- vague prompts;
- undeclared scope;
- missing forbidden actions;
- free-form final reports;
- changes made for zeal;
- unrequested refactors;
- duplicated documentation copied across many files;
- fragile tests based on long exact sentences.

The task packet should be strict enough to control execution and short enough to be usable.

---

## 11. Future validation

STEP 140 introduces Prompt Packet Validation Lite in `docs/26_PROMPT_PACKET_VALIDATION_LITE.md` and `scripts/validate_task_packet.py`.

The validator checks that required sections and keywords exist without turning prompt writing into a rigid schema too early. It is a support tool for task packet quality, not a replacement for Alberto review, Verification Gate, or tests.

STEP 150 adds golden samples in `docs/27_PROMPT_PACKET_GOLDEN_SAMPLES.md`.

- `examples/task_packets/valid/step_valid_minimal_task_packet.md` is the practical reference for a compact valid task packet.
- `examples/task_packets/invalid/` contains anti-pattern samples that should fail validation.

Use the valid sample as a reference for structure. Do not copy invalid samples into real work.
