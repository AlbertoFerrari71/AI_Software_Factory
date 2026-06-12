# 1070 - Windows CI Matrix for PowerShell Runner

## Purpose

ASF operates primarily on Windows/PowerShell. CI must detect runner and path
regressions that Linux-only checks can miss.

## Implementation

The CI workflow adds `windows-powershell-runner-gate` on `windows-latest`.

The job is intentionally focused:

- install project dev dependencies;
- validate `pwsh` availability;
- parse `scripts/verify.ps1`;
- run publish-runner and operator-focused pytest files.

This avoids an unnecessary full matrix while covering the highest-risk Windows
surfaces.

## No silent skips

The job does not silently skip PowerShell. If `pwsh` is missing or
`verify.ps1` does not parse, the job fails.

## Acceptance

- Windows CI coverage exists for PowerShell runner paths.
- Local tests remain unchanged and authoritative before handoff.
