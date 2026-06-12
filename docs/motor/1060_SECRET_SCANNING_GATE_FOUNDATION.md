# 1060 - Secret Scanning Gate Foundation

## Purpose

Add a pragmatic secret scanning gate without new Python runtime dependencies.

## Implementation

- CI contains a dedicated `secret-scan` job using gitleaks.
- `.gitleaks.toml` is versioned for documented placeholder handling.
- `scripts/verify.ps1` runs gitleaks when available locally.
- If gitleaks is missing locally, verify prints a warning and continues.

CI is the strong gate. Local missing-tool warning is explicit and must be
reported; it is not evidence that a scan passed.

## Policy

No real secrets, credentials, tokens, API keys or raw provider payloads are
allowed in fixtures, docs, reports or logs. Fake placeholders must be obvious
and non-sensitive.

## Commands

```powershell
gitleaks detect --source . --config .gitleaks.toml --redact
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1
```

## Acceptance

- CI secret-scan job is present.
- Local verify degrades explicitly if gitleaks is unavailable.
- Security model documents the operational policy.
