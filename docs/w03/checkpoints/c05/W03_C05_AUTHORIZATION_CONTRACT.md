# FlowLens Industrial AI — W03-C05 Authorization Contract

```text
task = W03-C05-I/H/R
checkpoint = W03-C05 — Counterfactual Evaluation + Recommendation + DecisionPacket
contract_version = W03-C05-A-v1
human_implementation_authorization = APPROVED
product_mode = OFFLINE / SHADOW / HUMAN-IN-THE-LOOP
operational_mutation = PROHIBITED
runtime_hgt = PROHIBITED
```

## Authorized result

C05 may validate the canonical frozen C01–C04 artifacts, derive a deterministic
categorical evaluation, build one canonical `RecommendationRecord`, and assemble
one canonical pre-human-decision `DecisionPacket`.

Policy versions are frozen as:

```text
decision_policy_version = w03-c05-decision-v1
evaluation_schema_version = w03-c05-evaluation-v1
packet_policy_version = w03-c05-packet-v1
```

Non-`NO_ACTION` C04 results are stress probes for investigation. They are not
intervention-efficacy evidence and grant no operational permission.

## Frozen dispositions

```text
NO_ACTION
NO_RECOMMENDATION
INVESTIGATION_ONLY
DEFER_TO_HUMAN
```

`CANDIDATE_RECOMMENDED` is structurally reserved and must not be emitted by
C05 v1. There is no aggregate score, weighted sum, probability, confidence,
utility or benefit scalar.

## Authorized implementation paths

```text
docs/sprints/W03_ai_decision_loop.md
docs/w03/checkpoints/c05/**

src/flowlens/decision/c05_policy.py
src/flowlens/decision/c05_validation.py
src/flowlens/decision/c05_evaluation.py
src/flowlens/decision/c05_recommendation.py
src/flowlens/decision/c05_packet.py

tests/test_c05_policy.py
tests/test_c05_recommendation.py
tests/test_c05_packet.py
tests/test_c05_harness.py
```

After implementation exact-SHA CI passes, the report stage may modify exactly:

```text
docs/w03/reports/W03_C05_R_DEVELOPMENT_ROUND_REPORT.md
docs/CURRENT_STATE.md
```

## Runtime capability boundary

Allowed runtime inputs are immutable in-memory C01–C04 artifacts. C05 has no
database, filesystem, network, model, tool, subprocess, random, wall-clock,
scenario-execution, HGT, HumanDecisionEvent or operational-write capability.

C01 contracts/enums/primitives/serialization and C02/C03/C04 runtime source are
frozen. Any required change to those surfaces is a Type-B contract conflict.

## Lifecycle

```text
Context Lock
→ implementation + complete H1–H19 harness
→ implementation commit
→ I / FULL_EXACT_SHA
→ Development Round Report + CURRENT_STATE
→ report commit
→ P / PUBLICATION_EXACT_SHA
→ final synchronization
→ REVIEW_READY
→ STOP
```

GPT C05 review and Human C05 acceptance remain pending. C05 is not closed and
C06 is not authorized.
