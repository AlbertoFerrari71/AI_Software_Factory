# 1130 - Known Limits and Next Roadmap

## Known limits

- Latest report resolver validates required fields but does not perform full
  JSON Schema validation through an external dependency.
- Publish readiness is a local evidence gate, not a publication command.
- Secret scan is strong in CI; local gitleaks can be unavailable and reported
  as warning.
- Operator status depends on the local Git checkout and Bridge path supplied.
- Reviewer independence is protocol/template based; no live model call is
  automatic.
- Dogfood evidence is fixture-based and local.

## Next roadmap

1140) Prompt Injection Adversarial Samples and Fencing

1150) Property-Based Tests Dev-Only

1160) Mutation Baseline Informative

1170) Split Monolithic Documents

1180) Docs Structure and Behavior Test Taxonomy

Future recovery item: Error Learning Ledger 0930 if a source branch or artifact
is identified and reviewed.

## Stop policy

Do not expand this RC into publish automation, web UI, scheduler, live AI loop,
multi-repo writes or automatic Codex autonomy without a new explicit step.
