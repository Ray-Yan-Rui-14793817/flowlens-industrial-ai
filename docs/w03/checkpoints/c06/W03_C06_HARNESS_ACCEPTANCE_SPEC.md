# FlowLens Industrial AI — W03-C06 Harness Acceptance Specification

All H1-H22 are mandatory. PASS requires detection, fail-closed enforcement and
recorded evidence for each family:

| Gate | Required proof |
|---|---|
| H1-H2 | frozen enum/schema; canonical deterministic immutable event identity/provenance |
| H3-H4 | ACCEPT/REJECT/DEFER non-execution semantics; exact C05 packet binding |
| H5-H6 | explicit aware monotonic time; reason subsets/disjointness/omission semantics |
| H7-H8 | comment and priority remain inert audit metadata |
| H9-H12 | first event, exact-tail chaining, cross-chain rejection and time monotonicity |
| H13-H16 | immutable history, canonical bytes, narrow readback and idempotent retry |
| H17-H19 | corruption/fork/cycle fail-closed, packet lock and filesystem confinement |
| H20-H21 | denied runtime capabilities and fresh-import purity |
| H22 | unchanged C05/C04/C03/C02/C01/W2 regressions |

The adversarial store pack must cover invalid roots, traversal-like audit text,
wrong packet/run/provenance/contracts, invalid decision/reasons, wrong filename
or digest, malformed/noncanonical JSON/UTF-8/datetime/LF, multiple roots, fork,
cycle, missing/cross-chain parent, time regression, stale pending state, busy
lock and same-ID/different-byte collision. Every failure must preserve all
existing committed event bytes.

Required local gates are focused C06 tests, the frozen focused regressions,
`pytest -m "not integration"`, guarded PostgreSQL tests only when the established
safety environment exists, `ruff check .`, `mypy .`, `git diff --check`, and
`docker compose config --quiet`. Actual totals and any environment limitation
must be reported without fabrication.

The accepted frozen regression baselines are C05 98, C04 31, C03 77, C02 26,
C01 39 and W2 154 passes.
