# W05-G0 Successor Governance Contract

TASK_ID = W05_G0_SUCCESSOR_GOVERNANCE_RECOVERY_R2

## Authority and scope

This is the Human-authorized, two-commit governance transition from exact main
2f1627342ff2b04d8324fbffec3db2e230b302e0. Commit A synchronizes exactly README.md,
AGENTS.md and docs/CURRENT_STATE.md. Commit B evolves only the expressly admitted
workflow, planner/receipt/aggregate, three legacy meta-test files, new successor
verifier/tests, five governance documents and current router/state projection.
No third commit, merge, operational mutation or product implementation is admitted.

The historical PR #8 merge is CLOSED / VERIFIED with first exact-head native CI
#153 / 39142499049, attempt 1 SUCCESS. P2-03 and Post-W04 stabilization are CLOSED.
W01-W04 runtime, closed evidence, dataset semantics, HGT isolation and the W04
source-evolution manifest are preserved. G0 does not authorize W05-C01/C02,
API/UI, W06, or FlowLens v1.0 release.

## Historical proof plane

W05_G0_W04_HISTORICAL_BASELINE.json is generated from the exact historical tree.
Its local collection/plan is identical to the native plan artifact
12142237262 from run 39142499049. The artifact ZIP SHA-256 is
46088c2d901e5288438e9cfbbbd89c6729b3ff0a3854264456874d60c1633b06.

The sealed baseline contains the sorted 2997 non-integration node IDs and
63 file paths, seven shards, native identity, W03 38/85, W04 9/67/81,
Integration 70, and governance 172/223/93/95/98.

| Historical identity | SHA-256 |
| --- | --- |
| Nodes | 9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a |
| Files | 890fdd5c30c7e2a1e90da8cb8b7123937d3356f1d519f82dff4a941f13659fd7 |
| Measured weights | a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851 |

The baseline is immutable after G0. A canonical JSON SHA-256 seal uses UTF-8,
sorted object keys, compact separators and no nonfinite numbers. Both seal and
approved identity are checked; recomputing a seal cannot admit altered history.
The C08 2807-node entry baseline and older weight evidence remain unchanged,
independently verifiable historical records. They do not define the W05 count.

## Active proof plane

W05_G0_ACTIVE_POLICY.json has schema w05-active-governance-policy-v1.
The active plan schema is w05-active-non-integration-plan-v1.

Every run collects the exact current HEAD. The historical 2997 nodes must be a
subset. Added test nodes and files are allowed by this planner; checkpoint scope
and Human implementation authority remain separate requirements. Missing,
renamed, duplicate or malformed nodes and collection errors fail closed.
No current W05 count or digest is predetermined.

The sealed plan records current counts, exact nodes, file digest, additions,
historical identities, policy identity, weights, assignment and exact HEAD.
Current fields and historical fields are explicitly distinct. The retained
collected_* transport aliases always mean the current collection and are
validated against the current_* fields when the plan is reconstructed.
entry_baseline_nodeids_sha256 continues to identify the immutable C08 baseline;
historical_nodeids_sha256 identifies the complete 2997-node W04 floor.

## Scheduling

Seven file-atomic shards use longest-processing-time assignment, ordered by
descending integer milliseconds then ascending file path. Each file goes to
the lowest-load shard, with lowest shard ID breaking ties.

A historical file with its exact historical node list and a positive measured
weight uses HISTORICAL_MEASURED. Human R2 clarification requires the two
historical zero-weight files (test_c06_policy.py and test_c08_prompt.py) to use
CONSERVATIVE_MAX_HISTORICAL_WEIGHT in active scheduling too. Their original
zero measurements and the historical weights digest remain immutable.
A new file or a historical file with changed collection uses
CONSERVATIVE_MAX_HISTORICAL_WEIGHT, the maximum accepted historical measured
file weight: 2040544 milliseconds. This value is derived, not independently
tunable. No zero weight, source-size estimate, or node-count estimate is admitted.

Each file records weight_milliseconds, weight_basis, historical_file and
collection_changed. A new file has historical_file=false and
collection_changed=true. Body-only test changes with unchanged collection use
the positive historical measured weight, subject to the same zero fallback.
Same collection, head and policy yield the same plan; semantic input changes
change its seal. A different exact HEAD also changes the plan identity.

## Execution receipts and aggregation

The existing execution stack verifies exact HEAD and recomputes the complete
sealed plan. Each shard performs collect-only exact equality before execution.
Receipts use w05-active-pytest-outcome-receipt-v1 and bind the exact plan/current
collection and historical anchor/digest. Terminal outcomes partition assigned
nodes. JUnit counts and digest must agree. Failed/error/xfail/xpass outcomes fail.
Only the three frozen Linux Windows-junction skips are accepted by native proof;
no new skip or silently missing accepted skip is admitted.

The aggregate requires all seven receipts, exact current union and exact once.
It rechecks the historical floor and prints HISTORICAL_NO_LOSS,
EXACT_CURRENT_UNION and EXACT_CURRENT_ONCE only after validation succeeds.
Existing artifact transport names are retained for compatibility; their plan
and receipt schemas identify W05, and no current digest replaces historical W04.

## Current regression and historical replay

W03 38 selectors / 85 cases and W04 9 families / 67 selectors / 81 cases execute
on current HEAD using unchanged runners and manifests.

The unchanged W04 governance verifier executes only in a clean detached tree at
2f1627342ff2b04d8324fbffec3db2e230b302e0. Its source, tests and workflow are the
historical versions. Inside that detached tree, uv sync --frozen builds an
isolated historical environment from its own pyproject.toml and uv.lock. The
historical environment's interpreter executes the unchanged verifier with
PYTHONPATH directed to historical src. Clean-tree checks bracket the replay,
and set -euo pipefail preserves failures through tee. Current
protected runtime bytes must independently match the anchor.

The historical replay must report gate_contract PASS,
W04_POST_MERGE_INTEGRATED, P2_03_PR8_MERGED_MAIN, exact 2997/63/7 identities and
172/223/93/95/98 controls. The successor job verifies those emitted records.
Local replay is local proof only. Native proof requires the first exact Commit-B
native attempt, with successful required jobs.

## Surface and protected-material governance

W05_G0_SURFACE_BASELINE.json pins exact entry Git blob identities and modes for
pyproject.toml, uv.lock, docker-compose.yml, migrations/ and apps/.
Current content and path sets must match. These surfaces are frozen at G0,
not permanently immutable: future evolution needs explicit versioned successor
admission and separate Human authorization.

The successor verifier verifies the actual historical anchor/tree/ancestry,
baseline and policy seals, current plan/collection, surfaces, protected source
and evidence, and current documentation projection. It preserves original
runtime files and closed runtime packages, docs/w03, docs/w04 and non-admitted
existing CI/test controls. The seven expressly mutable planner/receipt/runner/
aggregate and legacy test files are governed by active tests rather than
historical byte equality. New tests and upstream packages still need checkpoint
authority and their own semantic/security review; planner admission alone does
not authorize their behavior.

HGT access, future leakage and operational mutation remain forbidden. Policy
tampering to admit them fails closed. This verifier does not duplicate W03/W04
product semantics and is not a new checkpoint lifecycle state machine.

## Legacy test transition

All historical test node identities are retained. Tests in
test_ci_test_sharding.py keep old baseline/weight tamper controls, explicitly
test historical scheduling, and separately assert additive current collection.
test_c09_ci_gate.py uses the G0 surface/protected-source guard and extends the
actual shell truth table to require the successor job on full routes.
test_investigation_replay.py keeps runtime and HGT traps unchanged, replaces
the current-tree W04 workflow freeze with successor obligations, and validates
dynamic native current collection. Historical versions remain replayable at
the anchor. No test is skipped, xfailed or deleted to admit the transition.

## CI, review and completion

The major jobs, existing timeouts, immutable action pins, full-route classifier
and publication behavior are retained. W05 successor governance adds historical
replay plus active proof. Verification gate requires successor success on every
non-publication route and skipped status on publication routes.

Required proof includes whitespace, Ruff, strict mypy, lock consistency,
focused tests, current W03/W04, historical replay, and active exact-plan proof.
A first native failure stops at W05_G0_NATIVE_PROOF_FAILED; no rerun substitutes
for first-attempt evidence. A need for any additional tracked path stops at
W05_G0_SCOPE_EXPANSION_REQUIRED.

Pre-commit documentation records native proof as conditional. Actual generated
SHA/run identities and the effective final state belong in PR metadata and the
external evidence-led Development Report after they exist. G0 readiness remains
subject to independent review, and the PR stays OPEN / READY / UNMERGED.
W05-C01 implementation and merge authority are not granted by this task.
