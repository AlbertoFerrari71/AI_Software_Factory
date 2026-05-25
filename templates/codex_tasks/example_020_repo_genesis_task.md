# Codex Task Packet — Example

## Task ID

ASF-020-REPO-GENESIS

## Titolo

Creare struttura iniziale repository AI Software Factory.

## Obiettivo

Creare o verificare lo scheletro iniziale del repository, senza implementare logica applicativa.

## Branch consigliato

020-repo-genesis

## Modalità Codex consigliata

Suggest o Auto Edit.

Non usare Full Auto.

## File da leggere prima

- README.md
- AGENTS.md
- docs/10_ROADMAP.md
- docs/11_DECISIONS.md

## File modificabili

- README.md
- AGENTS.md
- CHANGELOG.md
- .gitignore
- .env.example
- pyproject.toml
- docs/**
- templates/**
- src/**
- tests/**
- .github/**

## File da NON toccare

- file fuori repository;
- credenziali;
- configurazioni globali Git/Codex;
- repository remoti.

## Vincoli

- Nessuna logica applicativa.
- Nessuna chiamata API.
- Nessun database.
- Nessun commit/push/merge.
- Nessuna cancellazione.

## Test da eseguire

```powershell
python -m pytest -q

```

## Criteri di accettazione

- Struttura repo completa.
- Smoke test passa.
- Documentazione aggiornata.
- Nessuna automazione distruttiva.
