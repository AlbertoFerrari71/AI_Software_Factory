from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
class ProjectProfile:
    name: str
    project_name: str
    repo_path: str
    main_branch: str
    test_command: str
    health_command: str
    notes: tuple[str, ...]
    default_forbidden_notes: tuple[str, ...]
    recommended_inspection: tuple[str, ...]


@dataclass(frozen=True)
class RunnerSettings:
    profile_name: str | None
    project_name: str
    repo_path: str
    main_branch: str
    test_command: str
    health_command: str
    notes: tuple[str, ...]
    default_forbidden_notes: tuple[str, ...]
    recommended_inspection: tuple[str, ...]

    @property
    def profile_label(self) -> str:
        return self.profile_name or "manual arguments"


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
    parser.add_argument("--mode", required=True, help="Runner mode. Current runner supports only: prepare.")
    parser.add_argument("--profile", help="Project profile name from config/asf_project_profiles.json.")
    parser.add_argument(
        "--profiles-config",
        default="config/asf_project_profiles.json",
        help="Profiles JSON path. Default: config/asf_project_profiles.json.",
    )
    parser.add_argument("--project-name", help="Logical target project name. Overrides profile value.")
    parser.add_argument("--repo-path", help="Local path of the target repository. Overrides profile value.")
    parser.add_argument("--main-branch", help="Target repository main branch. Overrides profile value.")
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


def string_list(value: Any, *, field: str, profile_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise InputError(f"profile '{profile_name}' field '{field}' must be a list of strings.")
    return tuple(item.strip() for item in value if item.strip())


def optional_string(profile: dict[str, Any], key: str, *, default: str = "") -> str:
    value = profile.get(key, default)
    if value is None:
        return default
    if not isinstance(value, str):
        raise InputError(f"profile field '{key}' must be a string.")
    return value.strip()


def load_profile(root: Path, config_path: str, profile_name: str) -> ProjectProfile:
    path = Path(config_path).expanduser()
    if not path.is_absolute():
        path = root / path

    if not path.is_file():
        raise InputError(f"profile config not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError(f"profile config is not valid JSON: {path}: {exc.msg}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("profiles"), dict):
        raise InputError("profile config must contain an object field named 'profiles'.")

    raw_profile = data["profiles"].get(profile_name)
    if raw_profile is None:
        raise InputError(f"profile not found: {profile_name}")
    if not isinstance(raw_profile, dict):
        raise InputError(f"profile '{profile_name}' must be a JSON object.")

    project_name = optional_string(raw_profile, "project_name")
    repo_path = optional_string(raw_profile, "repo_path")
    main_branch = optional_string(raw_profile, "main_branch", default="main") or "main"

    if not project_name:
        raise InputError(f"profile '{profile_name}' field 'project_name' is required.")
    if not repo_path:
        raise InputError(f"profile '{profile_name}' field 'repo_path' is required.")

    return ProjectProfile(
        name=profile_name,
        project_name=project_name,
        repo_path=repo_path,
        main_branch=main_branch,
        test_command=optional_string(raw_profile, "test_command", default="python -m pytest") or "python -m pytest",
        health_command=optional_string(raw_profile, "health_command"),
        notes=string_list(raw_profile.get("notes"), field="notes", profile_name=profile_name),
        default_forbidden_notes=string_list(
            raw_profile.get("default_forbidden_notes"),
            field="default_forbidden_notes",
            profile_name=profile_name,
        ),
        recommended_inspection=string_list(
            raw_profile.get("recommended_inspection"),
            field="recommended_inspection",
            profile_name=profile_name,
        ),
    )


def resolve_settings(args: argparse.Namespace, root: Path) -> RunnerSettings:
    profile: ProjectProfile | None = None
    if args.profile:
        profile = load_profile(root, args.profiles_config, args.profile.strip())

    project_name = (args.project_name or (profile.project_name if profile else "")).strip()
    repo_path = (args.repo_path or (profile.repo_path if profile else "")).strip()
    main_branch = (args.main_branch or (profile.main_branch if profile else "main")).strip() or "main"
    test_command = profile.test_command if profile else "python -m pytest"
    health_command = profile.health_command if profile else ""
    notes = profile.notes if profile else ()
    default_forbidden_notes = profile.default_forbidden_notes if profile else ()
    recommended_inspection = profile.recommended_inspection if profile else ()

    if not project_name:
        raise InputError("--project-name is required unless --profile provides project_name.")
    if not repo_path:
        raise InputError("--repo-path is required unless --profile provides repo_path.")

    return RunnerSettings(
        profile_name=profile.name if profile else None,
        project_name=project_name,
        repo_path=repo_path,
        main_branch=main_branch,
        test_command=test_command,
        health_command=health_command,
        notes=notes,
        default_forbidden_notes=default_forbidden_notes,
        recommended_inspection=recommended_inspection,
    )


def validate_args(args: argparse.Namespace) -> None:
    if args.mode.strip() != "prepare":
        raise InputError("--mode supports only 'prepare'.")

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


def output_step_dir(args: argparse.Namespace, settings: RunnerSettings, root: Path) -> Path:
    base = Path(args.output_dir).expanduser()
    if not base.is_absolute():
        base = root / base
    return base / safe_path_component(settings.project_name) / f"step_{args.step.strip()}"


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
    failed = [
        f"{label}: {result.stderr.strip() or result.stdout.strip()}"
        for label, result in failures
        if result.returncode != 0
    ]
    if failed:
        raise RuntimeError("Unable to read target Git status: " + " | ".join(failed))

    return GitSnapshot(
        branch=branch_result.stdout.strip() or "(detached or unavailable)",
        status=status_result.stdout.strip(),
        recent_commits=log_result.stdout.strip(),
    )


def markdown_block(value: str) -> str:
    return value.strip() if value.strip() else "(none)"


def bullet_lines(values: tuple[str, ...], *, fallback: str) -> str:
    if not values:
        return f"- {fallback}"
    return "\n".join(f"- {value}" for value in values)


def inspection_lines(settings: RunnerSettings) -> str:
    defaults = (
        "README.md",
        "AGENTS.md se presente",
        "CHANGELOG.md se presente",
        "docs/** rilevanti",
        "tests/** rilevanti",
        "script di verifica documentati dal progetto",
        "file specifici indicati da Alberto per lo step",
    )
    merged = [*defaults, *settings.recommended_inspection]
    return "\n".join(f"- `{item}`" if "/" in item or "." in item else f"- {item}" for item in merged)


def previous_step_note(step: str) -> str:
    try:
        previous = int(step) - 10
    except ValueError:
        return "Prerequisito non deducibile automaticamente; controllare manualmente lo step precedente su main."
    if previous <= 0:
        return "Prerequisito non deducibile automaticamente; controllare manualmente lo stato di main."
    return f"Controllare manualmente che lo step {previous} risulti gia' su main prima di procedere."


def build_task_packet(args: argparse.Namespace, settings: RunnerSettings, target_repo: Path, snapshot: GitSnapshot) -> str:
    step = args.step.strip()
    title = args.title.strip()
    branch = args.branch.strip()
    objective = args.objective.strip()
    strict_note = "Strict validation is enabled for this generated packet." if args.strict_ready else "Only Lite validation was requested."

    return f"""# STEP {step} - {title}

## Project context

Repository target: `{settings.project_name}`.

Profilo runner: `{settings.profile_label}`.

Cartella locale target: `{target_repo}`.

Branch principale: `{settings.main_branch}`.

Branch corrente rilevato nel target: `{snapshot.branch}`.

Working tree rilevata nel target: `{snapshot.working_tree_state}`.

Metodo operativo: ChatGPT prepara e rivede il task packet, Codex lavora solo dopo handoff umano, Alberto controlla diff, test, PR e merge. Il runner prepara file locali e non sostituisce Human gate, review umana, Git o Step Closure Report.

## Prerequisito

- {previous_step_note(step)}
- Verificare che il repository target sia quello atteso.
- Verificare che il branch principale sia `{settings.main_branch}`.
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
{bullet_lines(settings.default_forbidden_notes, fallback="Nessuna nota vietata aggiuntiva dal profilo.")}

## File da ispezionare

{inspection_lines(settings)}

## Note safety dal profilo

{bullet_lines(settings.notes, fallback="Nessuna nota safety di profilo.")}

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
{settings.test_command}
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


def build_handoff(
    args: argparse.Namespace,
    settings: RunnerSettings,
    target_repo: Path,
    task_packet: Path,
    report: Path,
    verification_pack: Path,
    snapshot: GitSnapshot,
) -> str:
    step = args.step.strip()
    title = args.title.strip()
    branch = args.branch.strip()
    objective = args.objective.strip()

    return f"""# STEP {step} - {title}

Questo handoff e' stato generato dal runner; deve comunque essere revisionato da Alberto/ChatGPT prima dell'uso.

## Contesto progetto target

- Repository: `{settings.project_name}`
- Cartella locale: `{target_repo}`
- Branch principale: `{settings.main_branch}`
- Branch di lavoro previsto: `{branch}`
- Profilo runner: `{settings.profile_label}`

## Stato Git letto dal runner

- Branch corrente target: `{snapshot.branch}`
- Working tree: `{snapshot.working_tree_state}`

Ultimi commit:

```text
{markdown_block(snapshot.recent_commits)}
```

Dettaglio working tree:

```text
{markdown_block(snapshot.status)}
```

## Prerequisito

- {previous_step_note(step)}
- Se il prerequisito non e' chiaro, controllarlo manualmente prima di modificare file.
- Se la working tree e' `DIRTY/WARNING`, Alberto deve decidere se proseguire.

## Obiettivo

{objective}

## FASE 1 - Allineamento sintetico

### Riepilogo

Preparare lo step {step} sul repository target mantenendo gate umano, branch dedicato, scope controllato e verifiche esplicite.

### Assunzioni

- [100] Il repository target e' quello indicato sopra.
- [101] Il branch di lavoro previsto e' `{branch}`.
- [102] Codex lavora solo dopo conferma di Alberto.
- [103] Il task packet generato e' una bozza da revisionare.

### Domande chiuse

- A) Procedere con il task packet generato dopo review umana. Default A.
- B) Rigenerare il task packet con obiettivo piu' stretto.
- C) Fermarsi per working tree `DIRTY/WARNING`.
- D) Fermarsi per prerequisito non verificato su main.

### Criticita'

- Verificare prerequisito su main.
- Verificare scope incluso ed escluso.
- Verificare eventuali note safety del profilo.
- Non trattare il report runner come Step Closure Report.

## FASE 2 - Istruzioni operative per Codex

### Istruzioni

- Leggere prima il task packet:

```text
{task_packet}
```

- Usare il verification pack come checklist locale:

```text
{verification_pack}
```

- Lavorare solo sul branch previsto dopo conferma umana.
- Se serve allargare scope, fermarsi e chiedere conferma.

### File da ispezionare

{inspection_lines(settings)}

### Scope incluso

- File e cartelle indicati dal task packet.
- Documentazione e test coerenti con lo step.
- Piccole modifiche reversibili e verificabili.

### Scope escluso

- CI.
- Dipendenze.
- Secret e `.env`.
- Dati sensibili.
- Produzione.
- Repository target fuori dallo scope.

### Forbidden actions

- Codex non deve fare commit/push/PR/merge.
- Codex non deve modificare direttamente GitHub.
- Codex non deve modificare hook/core.hooksPath.
- Codex non deve toccare secret/.env.
- Codex non deve allargare scope.
- Codex non deve invocare altri agenti o Codex automaticamente.

### Note safety dal profilo

{bullet_lines(settings.notes, fallback="Nessuna nota safety di profilo.")}

### Comandi di verifica

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=10
{settings.test_command}
git --no-pager diff --stat
git --no-pager diff --check
```

### Output finale richiesto

- step eseguito;
- stato;
- branch corrente;
- file creati;
- file modificati;
- descrizione tecnica sintetica;
- comandi eseguiti e risultati;
- verifiche non eseguite;
- rischi o note;
- conferme vincoli;
- prossimo step consigliato;
- richiesta esplicita di Step Closure Report.

## Step Closure Report

Dopo lavoro locale, commit/push/PR/merge eventualmente eseguiti manualmente da Alberto e verifica finale su main, compilare lo Step Closure Report:

```text
templates/codex_tasks/step_closure_report_template.md
```

## Report runner

```text
{report}
```
"""


def build_verification_pack(
    args: argparse.Namespace,
    settings: RunnerSettings,
    target_repo: Path,
    snapshot: GitSnapshot,
    task_packet: Path,
    report: Path,
) -> str:
    health_command = settings.health_command or "# Nessun health command configurato nel profilo."

    return f"""# ASF Runner Verification Pack

## Progetto target

- Progetto: `{settings.project_name}`
- Repo path: `{target_repo}`
- Profilo runner: `{settings.profile_label}`

## Step

- Step: `{args.step.strip()}`
- Titolo: `{args.title.strip()}`
- Branch previsto: `{args.branch.strip()}`

## Stato Git target letto dal runner

- Branch corrente target: `{snapshot.branch}`
- Working tree: `{snapshot.working_tree_state}`

Ultimi commit:

```text
{markdown_block(snapshot.recent_commits)}
```

Dettaglio working tree:

```text
{markdown_block(snapshot.status)}
```

## Pre-Codex checks consigliati

Eseguire o verificare nel repository target prima di incollare l'handoff in Codex:

```powershell
git branch --show-current
git status --short
git --no-pager log --oneline --max-count=10
```

- Controllare che il branch corrente sia coerente con il task.
- Controllare che la working tree sia `CLEAN` oppure che `DIRTY/WARNING` sia compreso e accettato da Alberto.
- Controllare che gli ultimi commit includano il prerequisito dello step precedente.
- Leggere `codex_handoff.md` e `task_packet.md`.
- Confermare Human gate prima di usare Codex.

## Post-Codex local checks consigliati

Eseguire nel repository target:

```powershell
git status --short
git --no-pager diff --stat
git --no-pager diff --check
{settings.test_command}
{health_command}
```

- Verificare che i file temporanei restino sotto `tmp/` o in percorsi ignorati.
- Verificare che il report Codex sia salvato come file Markdown prima dell'intake.

## Scope checks

- Elencare file creati e modificati.
- Confermare nessun file fuori scope.
- Confermare nessuna modifica a secret o `.env`.
- Confermare nessuna modifica a CI salvo autorizzazione esplicita.
- Confermare nessuna operazione vietata.
- Confermare nessuna modifica a repository target esterni non richiesta.

## Codex report checks

Il report Codex finale deve essere presente e includere almeno:

- STEP ESEGUITO;
- STATO;
- BRANCH CORRENTE;
- FILE CREATI;
- FILE MODIFICATI;
- COMANDI ESEGUITI;
- VERIFICHE NON ESEGUITE;
- RISCHI / NOTE;
- CONFERME VINCOLI;
- PROSSIMO STEP;
- RIEPILOGO FINALE.

## ASF checks lato AI_Software_Factory

```powershell
python scripts/validate_task_packet.py "{task_packet}"
python scripts/validate_task_packet.py --strict "{task_packet}"
```

Runner report review:

```text
{report}
```

## Human gates

- Review diff.
- Verificare scope incluso.
- Verificare scope escluso.
- Verificare vincoli e forbidden actions.
- Verificare note safety del profilo.
- Approvazione commit.
- Approvazione push.
- Approvazione PR.
- Approvazione merge.
- Solo dopo procedere manualmente al ciclo Git presidiato usando Quick Reference e Workflow Command Cookbook.

## PR checks handling

Comando di riferimento manuale:

```powershell
gh pr checks --watch
```

Se i check non sono disponibili o viene riportato `no checks reported`, trattare il caso come attenzione da registrare, non come fallimento automatico. Registrare l'attenzione nello Step Closure Report insieme ai controlli locali eseguiti.

## LF/CRLF handling

I warning LF/CRLF non sono bloccanti se `git diff --check`, test e Verification Gate passano con exit code 0.

## Closure stages da presidiare

- Prima di Codex: branch, working tree, prerequisito, handoff e Human gate.
- Dopo Codex: diff, test, health command e report Codex.
- Prima del commit: scope, secret, CI, operazioni vietate e Verification Gate.
- Prima del push: branch corretto e commit revisionato da Alberto.
- Prima della PR: titolo, body, scope e rischi coerenti.
- Prima del merge: PR checks, review e assenza di blocchi aperti.
- Dopo il pull finale di main: dashboard, health check, test, Verification Gate e Step Closure Report.

## Riferimenti

- Quick Reference: `docs/36_WORKFLOW_QUICK_REFERENCE.md`
- Step Closure Report: `docs/37_STEP_CLOSURE_REPORT.md`
- Workflow Command Cookbook: `docs/38_WORKFLOW_COMMAND_COOKBOOK.md`

## Nota

Il Verification Pack non sostituisce test, review umana, PR checks o Step Closure Report. Non contiene comandi per automatizzare commit, push, PR o merge.
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
    settings: RunnerSettings,
    target_repo: Path,
    output_dir: Path,
    task_packet: Path,
    handoff: Path,
    verification_pack: Path,
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

- project-name: `{settings.project_name}`
- profile: `{settings.profile_label}`
- repo-path: `{target_repo}`
- mode: `prepare`
- step: `{args.step.strip()}`
- title: `{args.title.strip()}`
- branch previsto: `{args.branch.strip()}`
- output-dir: `{output_dir}`
- handoff improvements active: yes

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
- `verification_pack.md`: `{verification_pack}`

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
    settings = resolve_settings(args, root)
    target_repo = resolve_target_repo(settings.repo_path)
    snapshot = read_git_snapshot(target_repo)

    out_dir = output_step_dir(args, settings, root)
    task_packet_path = out_dir / "task_packet.md"
    handoff_path = out_dir / "codex_handoff.md"
    report_path = out_dir / "runner_report.md"
    verification_pack_path = out_dir / "verification_pack.md"

    task_packet = build_task_packet(args, settings, target_repo, snapshot)
    write_text(task_packet_path, task_packet)

    validations = [run_validation(root, task_packet_path, strict=False)]
    if args.strict_ready:
        validations.append(run_validation(root, task_packet_path, strict=True))

    verification_pack = build_verification_pack(
        args,
        settings,
        target_repo,
        snapshot,
        task_packet_path,
        report_path,
    )
    write_text(verification_pack_path, verification_pack)

    handoff = build_handoff(
        args,
        settings,
        target_repo,
        task_packet_path,
        report_path,
        verification_pack_path,
        snapshot,
    )
    write_text(handoff_path, handoff)

    report = build_report(
        args,
        settings,
        target_repo,
        out_dir,
        task_packet_path,
        handoff_path,
        verification_pack_path,
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
