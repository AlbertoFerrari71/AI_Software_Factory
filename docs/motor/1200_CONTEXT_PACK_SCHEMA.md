# 1200 - Context Pack Schema

## Purpose

The Context Pack is the controlled context slice used to build a Task Packet or
review a milestone. It is selected by policy, not by model memory.

## Required Content

The Context Pack documents:

- max size policy;
- included summaries;
- relevant files;
- previous report summary;
- constraints;
- gates;
- stop conditions;
- auto-split policy.

## Excluded Content

The Context Pack must not contain:

- complete chat history;
- very long reports without compression;
- full historical documents that are not needed;
- redundant sources;
- previous full prompts unless a specific policy requires them;
- secrets, credentials or private tokens.

## Max Size Policy

Each Context Pack should define:

- target token or character budget;
- hard maximum;
- compression rule;
- overflow behavior;
- auto-split trigger.

If the pack exceeds the hard maximum, ASF must split the milestone or ask for
human review. It must not silently drop high-risk constraints.

## Auto-Split Rule

Auto-split is required when:

- the context budget is exceeded;
- relevant files exceed the max file count;
- independent deliverables can be separated safely;
- gate evidence would become too large for a compact review.

## Machine Contract

The JSON Schema is:

```text
schemas/asf_automation/context_pack.schema.json
```

The offline example is:

```text
examples/asf_automation/context_pack_example.json
```
