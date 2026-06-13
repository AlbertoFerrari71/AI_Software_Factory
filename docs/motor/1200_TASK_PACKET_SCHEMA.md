# 1200 - Task Packet Schema

## Purpose

The Task Packet is the compact executable contract for one milestone. It must
be complete enough to work, but small enough to avoid saturating model context.
If it becomes too large, ASF must split the step.

## Required Fields

| Field | Meaning |
|---|---|
| task_packet_version | Schema contract version. |
| project | Project name. |
| step | Milestone or step id. |
| state | Runner state when the packet was built. |
| scope | Objective, risk, included and excluded scope. |
| allowed_files | Explicit files or path patterns that may be touched. |
| forbidden_actions | Explicit actions the executor must not perform. |
| deliverables | Expected files or outputs. |
| gates | Required checks and expected status. |
| report | Required report format and output paths. |
| publish_policy | Whether commit, push, PR, merge, tag or deploy are allowed. |
| human_gate_policy | Human approval requirements before execution or publish. |
| repair_policy | Bounded repair attempts and escalation rule. |

## Size Policy

The Task Packet should contain:

- current objective;
- exact allowed scope;
- exact forbidden actions;
- deliverables;
- verification commands;
- stop conditions;
- report requirements.

The Task Packet should not contain:

- full chat history;
- long historical reports;
- redundant copies of large documents;
- unrelated roadmap details;
- raw provider output;
- secrets or private credentials.

## Split Rule

ASF must split the step when:

- allowed scope spans unrelated modules;
- the packet needs too many source files;
- the repair plan would exceed the original packet size;
- gates become ambiguous;
- human review cannot evaluate the diff as a single unit.

## Machine Contract

The JSON Schema is:

```text
schemas/asf_automation/task_packet.schema.json
```

The offline example is:

```text
examples/asf_automation/task_packet_example.json
```
