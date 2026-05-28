from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2


class InputError(ValueError):
    pass


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Codex task packet markdown file.",
    )
    parser.add_argument("--step", required=True, help="Step number, for example 170.")
    parser.add_argument("--title", required=True, help="Step title.")
    parser.add_argument("--branch", required=True, help="Expected dedicated branch name.")
    parser.add_argument("--objective", required=True, help="Short objective for the step.")
    parser.add_argument("--output", help="Output markdown file path.")
    parser.add_argument(
        "--print",
        dest="print_output",
        action="store_true",
        help="Print generated markdown to stdout. If --output is omitted, stdout is the only output.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite --output if it already exists.",
    )
    parser.add_argument(
        "--strict-ready",
        action="store_true",
        help="Add a note that the generated task packet can be checked with validate_task_packet.py --strict.",
    )
    return parser.parse_args(argv)


def validate_inputs(args: argparse.Namespace) -> None:
    step = args.step.strip()
    title = args.title.strip()
    branch = args.branch.strip()
    objective = args.objective.strip()

    if not step.isdigit():
        raise InputError("--step must be numeric.")
    if int(step) % 10 != 0:
        raise InputError("--step must be a multiple of 10.")
    if not title:
        raise InputError("--title must not be empty.")
    if not branch:
        raise InputError("--branch must not be empty.")
    if re.search(r"\s", branch):
        raise InputError("--branch must not contain spaces.")
    if not objective:
        raise InputError("--objective must not be empty.")
    if not args.output and not args.print_output:
        raise InputError("--output is required unless --print is used.")


def build_task_packet(args: argparse.Namespace) -> str:
    step = args.step.strip()
    title = args.title.strip()
    branch = args.branch.strip()
    objective = args.objective.strip()
    strict_note = ""

    if args.strict_ready:
        strict_note = """
## Strict-ready note

Questo task packet puo' essere controllato anche con:

```powershell
python scripts/validate_task_packet.py --strict <task-packet.md>
```
"""

    return f"""# STEP {step} - {title}

## Project context

Repository: AlbertoFerrari71/AI_Software_Factory.

Cartella locale: `C:\\Users\\alberto.ferrari\\source\\repos\\AI_Software_Factory`.

Branch principale: `main`.

Metodo operativo: ChatGPT prepara il task packet, Codex lavora localmente su branch dedicato, Alberto verifica diff, test e stato Git prima di commit, push, PR e merge.

## Completed steps

- 010) Visione e contesto.
- 020) Repository Genesis.
- 030) Safety Model.
- 140) Prompt Packet Validation Lite.
- 150) Prompt Packet Examples and Golden Samples.
- 160) Prompt Packet Validation Strict Mode.

## BRANCH DA USARE

Creare o usare il branch dedicato:

```text
{branch}
```

Prima di procedere verificare che `main` sia aggiornato e che il working tree sia pulito. Se il branch corrente non corrisponde, fermarsi e segnalarlo.

## Objective

{objective}

## ALLOWED SCOPE

- `docs/**`
- `tests/**`
- `templates/**`
- `scripts/**`

Se serve uscire dallo scope, fermarsi e segnalarlo.

## FORBIDDEN SCOPE

- `src/**`
- `policies/**`
- `.github/workflows/ci.yml`
- CI fuori scope salvo approval esplicita;
- dipendenze e lockfile salvo approval esplicita;
- secret, `.env` o configurazioni sensibili;
- file fuori repository.

## FORBIDDEN ACTIONS

- Non fare commit.
- Non fare push.
- Non aprire PR.
- Non fare merge.
- Non modificare direttamente GitHub.
- Non applicare configurazioni GitHub reali.
- Non applicare branch protection/rulesets.
- Non installare hook Git.
- Non modificare git config core.hooksPath.
- Non usare bypass ASF_ALLOW_MAIN_BYPASS.
- Non modificare secret, `.env` o configurazioni sensibili.
- Non modificare `src/**`.
- Non modificare `policies/**`.
- Non modificare CI o dipendenze senza approval esplicita.

## File da ispezionare

- `README.md`
- `AGENTS.md`
- `docs/10_ROADMAP.md`
- `docs/05_SECURITY_MODEL.md`
- documenti specifici dello step.

## File modificabili

- Dichiarare qui i file ammessi per lo step.

## Requisiti funzionali

- Mantenere modifiche piccole, leggibili e verificabili.
- Rispettare il branch dedicato e lo scope approvato.
- Non introdurre schema JSON/YAML formale se non richiesto dallo step.

## Required changes

- Descrivere qui le modifiche richieste.
- Aggiungere o aggiornare test automatici se cambia comportamento.
- Aggiornare documentazione solo quando collegata allo step.

## Verification Gate

Eseguire o motivare se non eseguiti:

```powershell
python -m pytest
git diff --check
git status --short
```

Se applicabile:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\verify.ps1
```

## Documentation Sync

Valutare esplicitamente:

- `CHANGELOG.md`;
- `docs/10_ROADMAP.md`;
- Roadmap;
- `docs/11_DECISIONS.md`;
- Decisions;
- documenti specifici coinvolti.

Non aggiornare documenti per zelo.

## Soft Protection awareness

- `main` e' trattato come protetto.
- I Soft Protection Guardrails sono opt-in.
- Gli hook locali vivono in `.githooks`.
- `core.hooksPath` non deve essere modificato da Codex.
- Codex non deve installare hook Git.
- Codex non deve usare `ASF_ALLOW_MAIN_BYPASS`.

## Golden samples

Usare i golden samples come riferimento:

- valid sample: `examples/task_packets/valid/step_valid_minimal_task_packet.md`;
- valid strict sample: `examples/task_packets/valid/step_valid_strict_task_packet.md`;
- invalid samples: `examples/task_packets/invalid/`.
{strict_note}
## Output finale richiesto

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

La sezione I deve includere:

- Step eseguito: {step}) {title}
- Tempo impiegato: ...
- Stato step: ...
- Prossimo step: ...

## Rollback / safe stop

Rollback minimo: ripristinare i file modificati o abbandonare il branch.

Safe stop se:

- compaiono file fuori scope;
- compaiono secret;
- falliscono test critici;
- serve L3/L4 non approvato;
- il rollback non e' chiaro.
"""


def write_output(path: Path, content: str, *, force: bool) -> None:
    if path.exists() and not force:
        raise InputError(f"Output file already exists: {path}. Use --force to overwrite.")

    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(content, encoding="utf-8")


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        validate_inputs(args)
        content = build_task_packet(args)
        if args.output:
            write_output(Path(args.output), content, force=args.force)
        if args.print_output or not args.output:
            print(content, end="")
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
