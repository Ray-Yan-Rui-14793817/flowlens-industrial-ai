# W04-DEVCTRL-02 Repair-01 Human Authorization

## Authorization

```text
PROJECT: FlowLens Industrial AI
TASK: W04-DEVCTRL-02 REPAIR-01
TASK VERSION: V2.2.1 / POST-#122
HUMAN AUTHORIZATION: APPROVED
PURPOSE: HISTORICAL CONTROL-FREEZE TEMPORAL-SCOPE COMPATIBILITY
B1 ATTEMPT 1: 9d5b6e3baea1a860446b70d9b254cc3dc41815a4
B1 CI: #122 / 37889883403 / COMPLETED / FAILURE
```

The Human's explicit pasted continuation request adopts FLOWLENS_W04_DEVCTRL_02_POST_122_CUTOVER_TASK_V2_2_1.md as the normative contract. V2.2 defines the referenced repair context, B3 and Stage C details. The full contracts and referenced V2.2 design/review were read before mutation. V2.2.1 controls any conflict with older instructions. Stage A and the failed B1 attempt remain immutable evidence.

Authorized existing tests:

- tests/test_investigation_evidence_queries.py::test_n52_committed_source_governance_and_frozen_blobs
- tests/test_investigation_summary.py::test_s52_frozen_upstream_w03_dependencies_and_control_bytes_unchanged

## Exact four-path scope

Create the two governance files and modify only the two existing test bodies:

```text
docs/w04/devctrl-02/W04_DEVCTRL_02_REPAIR_01_AUTHORIZATION.md
docs/w04/devctrl-02/W04_DEVCTRL_02_REPAIR_01_CONTEXT_LOCK.md
tests/test_investigation_evidence_queries.py
tests/test_investigation_summary.py
```

```text
RUNTIME SOURCE CHANGE: NOT AUTHORIZED
WORKFLOW CHANGE DURING REPAIR: NOT AUTHORIZED
CI SCRIPT CHANGE DURING REPAIR: NOT AUTHORIZED
TEST NODE ADD / REMOVE / RENAME: NOT AUTHORIZED
TEST PARAMETERIZATION / SKIP / XFAIL CHANGE: NOT AUTHORIZED
W04-C08: NOT AUTHORIZED
```

This repair does not weaken closed-checkpoint runtime, source, W03, dependency or source-evolution freeze. It only corrects the temporal scope of historical CI-control freeze assertions. C04 retains its actual closeout workflow blob; C07 retains equality of its entry and closeout control trees. Current runtime and frozen dependencies remain asserted against current HEAD. Git ancestry must prove both historical closeouts precede HEAD. Current CI behavior remains governed by the dedicated DEVCTRL controls and native exact-SHA proof.

## Commit and proof boundary

Exactly one new repair commit is authorized, with parent 9d5b6e3baea1a860446b70d9b254cc3dc41815a4 and message:

```text
test(w04-devctrl-02): preserve historical freeze under authorized CI evolution
```

Normal push only. Preserve the two current node sets exactly. The repair SHA must independently pass legacy Quality, the complete existing shadow graph, coverage and six terminal-outcome equivalence, entry no-loss, Compose, W03 38/85 and final Verification before B2 may begin. A native failure grants no second repair commit.

## Stop codes

```text
W04_DEVCTRL_02_REPAIR_01_WAITING_FOR_B1_TERMINAL
W04_DEVCTRL_02_REPAIR_01_CONTEXT_CHANGED
W04_DEVCTRL_02_REPAIR_01_NODESET_DRIFT
W04_DEVCTRL_02_REPAIR_01_SCOPE_VIOLATION
W04_DEVCTRL_02_REPAIR_01_CI_FAILED
```

The continuation authorizes B1R, then B2, B3 and Stage C only after each preceding exact-SHA native PASS. The final status is at most REVIEW_READY. Independent GPT implementation review and Human acceptance remain PENDING. DEVCTRL-02 closeout, DEVCTRL-03, C08, merge, branch deletion, main write and history rewrite are NOT AUTHORIZED. PR #7 remains OPEN / DRAFT / UNMERGED.
