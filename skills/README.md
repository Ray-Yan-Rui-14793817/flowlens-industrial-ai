# FlowLens W03 Project Skills

## Current G0 Decision

```text
EXECUTABLE PROJECT SKILLS:
NONE REQUIRED FOR G0 / C01 ENTRY
```

This directory exists to make the project-level Skill policy explicit.

It does **not** define an active executable skill yet.

---

## Why Skills Are Deferred

The W03 workflow has been architected but has not yet accumulated repeated C01/C02 execution evidence.

Creating reusable Skills before observing stable repetition would duplicate governance and increase drift risk.

The preferred sequence is:

```text
G0
freeze governance

C01
execute contract-driven workflow once

C02
execute the workflow again

then
identify stable repetitive procedures worth packaging
```

---

## Possible Future Skill Candidates

Non-binding candidates:

```text
context-lock-validator
harness-evidence-collector
round-report-assembler
checkpoint-preflight
```

These are not authorized capabilities.

Actual skill creation requires a separate design/review step.

---

## Source-of-Truth Rule

A Skill may implement a reusable procedure.

A Skill may **not** become the source of truth for:

```text
business semantics
AI Loop architecture
Semantic Trust
runtime tool permissions
checkpoint authorization
human acceptance
```

Those remain in repository control documents.
