# 1050 - Contract Coherence and Numbering Baseline

## Scope

This step aligns agent contracts before the ASF V1 supervised operator RC.

## LAST-* rule

`LAST-*` is deprecated as a general repository artifact pattern.

Allowed exception:

- Bridge/codex_command operational output;
- Bridge/pwsh_command operational output;
- standard Bridge mirrors already produced by the publish runner/state machine.

The exception is compatibility-only. `LAST-*` files are not authoritative and
must not be introduced as permanent repository artifacts.

## Multi-series numbering

The step namespace is the directory or series:

```text
namespace = directory/serie
```

- `motor/1050`;
- `collaboration/0200`;
- `skills/0260`.

The number `NNNN` is unique inside the series, not globally. Cross-series
references must include the namespace. Historical gaps and legacy names are
frozen and must not be renumbered.

## TREE.txt status

TREE.txt is not the live operational map.

`TREE.txt` is not the live operational map for ASF. If found in historical
references, treat it as legacy. The live map is
`docs/34_PROJECT_WORKFLOW_INDEX.md`, backed by
`scripts/check_workflow_health.py`.

No manual TREE regeneration is required for this RC.

## Acceptance

- AGENTS.md and CLAUDE.md document the Bridge-only `LAST-*` exception.
- README.md, AGENTS.md and CLAUDE.md document multi-series numbering.
- New motor docs use current naming without renumbering historical gaps.
