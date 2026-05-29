from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_RUNTIME_ERROR = 3


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class GitSnapshot:
    branch: str
    status: str
    recent_commits: str

    @property
    def working_tree_state(self) -> str:
        return "CLEAN" if not self.status else "DIRTY/WARNING"


@dataclass(frozen=True)
class ValidationResult:
    mode: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def status(self) -> str:
        return "PASS" if self.returncode == 0 else "FAIL"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a local ASF next-step handoff without running Codex or changing the target repo.",
    )
    parser.add_argument("--mode", required=True, help="Runner mode. STEP 300 supports only: prepare.")
    parser.add_argument("--project-name", required=True, help="Logical target project name.")
    parser.add_argument("--repo-path", required=True, help="Local path of the target repository.")
    parser.add_argument("--main-branch", default="main", help="Target repository main branch. Default: main.")
    parser.add_argument("--step", required=True, help="Next step number. Must be numeric and a multiple of 10.")
    parser.add_argument("--title", required=True, help="Next step title.")
    parser.add_argument("--branch", required=True, help="Expected dedicated working branch for the next step.")
    parser.add_argument("--objective", required=True, help="Short objective for the next step.")
    parser.add_argument(
        "--output-dir",
        default="tmp/asf_next_step",
        help="Output base directory inside AI Software Factory unless an absolute path is used.",
    )
    parser.add_argument(
        "--strict-ready",
        dest="strict_ready",
        action="store_true",
        default=True,
        help="Run Strict validation too. This is the default; the flag is accepted for explicit calls.",
    )
    parser.add_argument(
        "--no-strict-ready",
        dest="strict_ready",
        action="store_false",
        help="Run only Lite validation.",
    )
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    if args.mode.strip() != "prepare":
        raise InputError("--mode supports only 'prepare' in STEP 300.")

    if not args.project_name.strip():
        raise InputError("--project-name must not be empty.")

    step = args.step.strip()
    if not step.isdigit():
        raise InputError("--step must be numeric.")
    if int(step) % 10 != 0:
        raise InputError("--step must be a multiple of 10.")

    if not args.title.strip():
        raise InputError("--title must not be empty.")
    if not args.branch.strip():
        raise InputError("--branch must not be empty.")
    if re.search(r"\s", args.branch.strip()):
        raise InputError("--branch must not contain spaces.")
    if not args.objective.strip():
        raise InputError("--objective must not be empty.")


def resolve_target_repo(repo_path: str) -> Path:
    path = Path(repo_path).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()

    if not path.exists():
        raise InputError(f"--repo-path does not exist: {path}")
    if not path.is_dir():
        raise InputError(f"--repo-path is not a directory: {path}")
    if not (path / ".git").is_dir():
        raise InputError(f"--repo-path is not a Git repository with a .git directory: {path}")
    return path


def safe_path_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("._-")
    return cleaned or "project"


def output_step_dir(args: argparse.Namespace, root: Path) -> Path:
    base = Path(args.output_dir).expanduser()
    if not base.is_absolute():
        base = root / base
    return base / safe_path_component(args.project_name) / f"step_{args.step.strip()}"


def run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def read_git_snapshot(target_repo: Path) -> GitSnapshot:
    branch_result = run_command(["git", "branch", "--show-current"], cwd=target_repo)
    status_result = run_command(["git", "status", "--short"], cwd=target_repo)
    log_result = run_command(["git", "--no-pager", "log", "--oneline", "--max-count=10"], cwd=target_repo)

    failures = [
        ("current branch", branch_result),
        ("working tree", status_result),
        ("recent commits", log_result),
    ]
    failed = [f"{label}: {result.stderr.strip() or result.stdout.strip()}" for label, result in failures if result.returncode != 0]
    if failed:
        raise RuntimeError("Unable to read target Git status: " + " | ".join(failed))

    return GitSnapshot(
        branch=branch_result.stdout.strip() or "(detached or unavailable)",
        status=status_result.stdout.strip(),
        recent_commits=log_result.stdout.strip(),
    )


def markdown_block(value: str) -> str:
    return value.strip() if value.strip() else "(none)"


def build_task_packet(args: argparse.Namespace, target_repo: Path, snapshot: GitSnapshot) -> str:
    step = args.step.strip()
    title = args.title.strip()
    branch = args.branch.strip()
    objective = args.objective.strip()
    strict_note = "Strict validation is enabled for this generated packet." if args.strict_ready else "Only Lite validation was requested."

    return f"""# STEP {step} - {title}

## Project context

Repository target: `{args.project_name.strip()}`.

Cartella locale target: `{target_repo}`.

Branch principale: `{args.main_branch.strip()}`.

Branch corrente rilevato nel target: `{snapshot.branch}`.

Working tree rilevata nel target: `{snapshot.working_tree_state}`.

Metodo operativo: ChatGPT prepara e rivede il task packet, Codex lavora solo dopo handoff umano, Alberto controlla diff, test, PR e merge. Il runner prepara file locali e non sostituisce Human gate, review umana, Git o Step Closure Report.

## Prerequisito

- Verificare che il repository target sia quello atteso.
- Verificare che il branch principale sia `{args.main_branch.strip()}`.
- Verificare che il branch di lavoro previsto sia `{branch}`.
- Se la working tree e' `DIRTY/WARNING`, Alberto deve decidere se proseguire, integrare lo stato esistente o fermarsi.

## BRANCH DA USARE

Branch dedicato previsto:

```text
{branch}
```

Prima di modificare file, Codex deve verificare branch corrente, `main` del progetto, working tree e scope. Se il branch corrente non corrisponde al task, fermarsi e segnalarlo.

## Objective

{objective}

## ALLOWED SCOPE

Default ASF-compatible da confermare per il progetto target:

- `docs/**`
- `tests/**`
- `templates/**`
- `scripts/**`

Se il progetto target richiede scope diverso, fermarsi e chiedere conferma prima di modificare file.

## FORBIDDEN SCOPE

- `src/**` salvo decisione esplicita dello step.
- `policies/**`.
- `.github/workflows/ci.yml` e modifiche CI.
- Dipendenze e lockfile.
- Secret, `.env` o configurazioni sensibili.
- Database reali, dati sensibili, produzione.
- File fuori dal repository target.

## FORBIDDEN ACTIONS

- Nessun commit/push/PR/merge da parte di Codex.
- Non fare commit.
- Non fare push.
- Non aprire PR.
- Non fare merge.
- Non modificare direttamente GitHub.
- Non creare release.
- Non installare hook Git.
- Non modificare git config core.hooksPath.
- Non usare `ASF_ALLOW_MAIN_BYPASS`.
- Non creare branch nel repository target senza richiesta esplicita.
- Non eseguire reset distruttivi o pulizie distruttive.
- Non modificare secret, `.env`, dati sensibili, CI o dipendenze.
- Non invocare Codex da script.
- Non automatizzare commit/push/PR/merge.

## File da ispezionare

- `README.md`
- `AGENTS.md` se presente
- `CHANGELOG.md` se presente
- `docs/**` rilevanti
- `tests/**` rilevanti
- script di verifica documentati dal progetto
- file specifici indicati da Alberto per lo step

## Stato Git target rilevato read-only

Branch corrente:

```text
{snapshot.branch}
```

Working tree:

```text
{snapshot.working_tree_state}
```

Dettaglio working tree:

```text
{markdown_block(snapshot.status)}
```

Ultimi commit:

```text
{markdown_block(snapshot.recent_commits)}
```

## Required changes

- Preparare solo le modifiche coerenti con lo step {step}.
- Mantenere il diff piccolo, leggibile, testabile e reversibile.
- Aggiornare documentazione solo se cambia comportamento, workflow o decisione operativa.
- Non introdurre nuove dipendenze.

## Verification Gate

Eseguire o motivare se non eseguiti:

```powershell
python -m pytest
git diff --check
git status --short
```

Se il progetto target ha un gate locale equivalente, usarlo solo dopo aver letto la documentazione del progetto.

## Documentation Sync

Valutare esplicitamente:

- `CHANGELOG.md`;
- `docs/10_ROADMAP.md` o Roadmap equivalente;
- `docs/11_DECISIONS.md` o Decisions equivalente;
- documenti specifici dello step.

Non aggiornare documenti per zelo.

## Soft Protection awareness

- `main` e' trattato come protetto.
- I Soft Protection Guardrails sono opt-in.
- Gli hook locali vivono in `.githooks` quando il progetto li usa.
- `core.hooksPath` non deve essere modificato da Codex.
- Codex non deve installare hook Git.

## Golden samples

Quando applicabile, usare come riferimento i sample ASF:

- `examples/task_packets/valid/step_valid_minimal_task_packet.md`;
- `examples/task_packets/valid/step_valid_strict_task_packet.md`;
- `examples/task_packets/invalid/`.

## Validazione del packet

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

## Step Closure Report richiesto

Dopo il lavoro locale e dopo le azioni Git/PR/main eseguite da Alberto, compilare:

```text
templates/codex_tasks/step_closure_report_template.md
```

Lo Step Closure Report deve distinguere lavoro locale, commit, push, PR, merge e verifica finale su `main`.

## Rollback / safe stop

Rollback minimo: ripristinare i file modificati sul branch dedicato o abbandonare il branch.

Safe stop se:

- il branch non corrisponde;
- compaiono file fuori scope;
- compaiono secret;
- falliscono test critici;
- serve L3/L4 non approvato;
- il rollback non e' chiaro.
"""


def build_handoff(args: argparse.Namespace, target_repo: Path, task_packet: Path, report: Path, snapshot: GitSnapshot) -> str:
    return f"""# ASF Next Step Runner - Codex Handoff

## Progetto

- Nome: `{args.project_name.strip()}`
- Repo path: `{target_repo}`
- Branch principale: `{args.main_branch.strip()}`
- Branch corrente rilevato: `{snapshot.branch}`
- Working tree: `{snapshot.working_tree_state}`

## Step

- Step: {args.step.strip()}
- Titolo: {args.title.strip()}
- Branch previsto: `{args.branch.strip()}`
- Obiettivo: {args.objective.strip()}

## Prerequisito

Leggere il task packet generato prima di qualsiasi modifica:

```text
{task_packet}
```

Se la working tree e' `DIRTY/WARNING`, fermarsi e chiedere conferma ad Alberto prima di modificare file.

## Vincoli

- Lavorare solo dopo conferma umana.
- Usare branch dedicato.
- Mantenere diff piccolo, testabile e reversibile.
- Non modificare repository target fuori dallo scope del task packet.
- Non modificare CI, dipendenze, secret, `.env`, dati sensibili o produzione.

## Forbidden actions

- Nessun commit/push/PR/merge da parte di Codex.
- Non fare commit.
- Non fare push.
- Non aprire PR.
- Non fare merge.
- Non modificare direttamente GitHub.
- Non creare release.
- Non installare hook Git.
- Non modificare git config core.hooksPath.
- Non invocare altri agenti o Codex automaticamente.

## Test

Eseguire i test e le verifiche indicate dal task packet. Se una verifica non e' eseguita, dichiarare motivo e rischio residuo.

## Report finale

Il report finale deve includere file creati, file modificati, comandi eseguiti, risultati, verifiche non eseguite, rischi, conferme vincoli e prossimo step consigliato.

Runner report operativo:

```text
{report}
```
"""


def run_validation(root: Path, task_packet: Path, *, strict: bool) -> ValidationResult:
    command = [sys.executable, str(root / "scripts" / "validate_task_packet.py")]
    mode = "Strict" if strict else "Lite"
    if strict:
        command.append("--strict")
    command.append(str(task_packet))

    result = run_command(command, cwd=root)
    return ValidationResult(
        mode=mode,
        returncode=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )


def validation_section(result: ValidationResult) -> str:
    return f"""### {result.mode}

- Status: {result.status}
- Exit code: {result.returncode}

Output:

```text
{markdown_block(result.stdout)}
```

Errors:

```text
{markdown_block(result.stderr)}
```
"""


def build_report(
    args: argparse.Namespace,
    target_repo: Path,
    output_dir: Path,
    task_packet: Path,
    handoff: Path,
    report: Path,
    snapshot: GitSnapshot,
    validations: list[ValidationResult],
) -> str:
    validation_summary = "\n".join(validation_section(result) for result in validations)
    strict_status = next((result.status for result in validations if result.mode == "Strict"), "SKIPPED")
    lite_status = next((result.status for result in validations if result.mode == "Lite"), "SKIPPED")

    warning = ""
    if snapshot.status:
        warning = "\nWARNING: target working tree is DIRTY/WARNING. Alberto must decide whether to continue.\n"

    return f"""# ASF Next Step Runner Report

## Summary

- project-name: `{args.project_name.strip()}`
- repo-path: `{target_repo}`
- mode: `prepare`
- step: `{args.step.strip()}`
- title: `{args.title.strip()}`
- branch previsto: `{args.branch.strip()}`
- output-dir: `{output_dir}`

## Target Git status

- branch corrente target: `{snapshot.branch}`
- working tree: `{snapshot.working_tree_state}`
{warning}
Dettaglio working tree:

```text
{markdown_block(snapshot.status)}
```

Ultimi commit:

```text
{markdown_block(snapshot.recent_commits)}
```

## Output creati

- `task_packet.md`: `{task_packet}`
- `codex_handoff.md`: `{handoff}`
- `runner_report.md`: `{report}`

## Validazione

- Lite: {lite_status}
- Strict: {strict_status}

{validation_summary}

## Prossimo comando consigliato

```powershell
Get-Content -Raw "{handoff}"
```

Copiare manualmente il contenuto di `codex_handoff.md` in Codex solo dopo review umana. Il runner non invoca Codex.

## Azioni non eseguite

- Nessun commit.
- Nessun push.
- Nessuna PR.
- Nessun merge.
- Nessuna modifica a GitHub.
- Nessuna modifica al repository target.
- Nessuna creazione branch nel repository target.
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def prepare(args: argparse.Namespace) -> int:
    root = repo_root()
    target_repo = resolve_target_repo(args.repo_path)
    snapshot = read_git_snapshot(target_repo)

    out_dir = output_step_dir(args, root)
    task_packet_path = out_dir / "task_packet.md"
    handoff_path = out_dir / "codex_handoff.md"
    report_path = out_dir / "runner_report.md"

    task_packet = build_task_packet(args, target_repo, snapshot)
    write_text(task_packet_path, task_packet)

    validations = [run_validation(root, task_packet_path, strict=False)]
    if args.strict_ready:
        validations.append(run_validation(root, task_packet_path, strict=True))

    handoff = build_handoff(args, target_repo, task_packet_path, report_path, snapshot)
    write_text(handoff_path, handoff)

    report = build_report(
        args,
        target_repo,
        out_dir,
        task_packet_path,
        handoff_path,
        report_path,
        snapshot,
        validations,
    )
    write_text(report_path, report)

    print(report)

    if any(result.returncode != 0 for result in validations):
        return EXIT_RUNTIME_ERROR
    return EXIT_SUCCESS


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        validate_args(args)
        return prepare(args)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
