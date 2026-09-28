# FlowLens Industrial AI — W03-C07 Authorization Contract

```text
task = W03-C07-I/H/R
checkpoint = W03-C07 — Offline HGT Evaluation
contract_version = W03-C07-A-v1
gpt_contract_review = COMPLETE / FROZEN
human_implementation_authorization = APPROVED
product_mode = OFFLINE / SHADOW / HUMAN-IN-THE-LOOP
operational_mutation = PROHIBITED
runtime_hgt = PROHIBITED
evaluation_hgt = AUTHORIZED / PROTECTED / OFFLINE ONLY
outcome_evaluation = DEFERRED
c08 = NOT AUTHORIZED
```

## Authorized result

C07 may consume an already-finalized canonical C05 `DecisionPacket`, a
finalized W2 `ScenarioResult`, its protected `HiddenGroundTruth`, and the
required in-memory baseline dataset and paired packet. It may emit exactly one
protected C01 `RecommendationEvaluation`.

The evaluator is a separate sidecar package under `flowlens.evaluation`.
Runtime packages may not import it. It has no operational, database,
filesystem, manifest, network, model, LLM, tool, subprocess, random or ambient
wall-clock capability.

## Frozen versions

```text
evaluator = w03-c07-evaluator-v1
metric_policy = w03-c07-metrics-v1
replay_policy = w03-c07-replay-v1
producer = flowlens.evaluation.c07_recommendation
recommendation_evaluation = recommendation-evaluation.v1 / UNCHANGED
outcome_evaluation = NOT IMPLEMENTED
```

## Dependency direction

```text
evaluation -> frozen C01-C05 artifacts / finalized W2 dataset + HGT
runtime     -X-> evaluation / HGT
```

Protected evaluation output may not alter or enter the original
`RecommendationRecord` or `DecisionPacket`. Human decisions are not business
outcomes and are not evaluated by C07.

## Lifecycle

```text
Context Lock
→ implementation + H1-H38 harness
→ implementation commit
→ I / FULL_EXACT_SHA
→ Development Round Report + CURRENT_STATE
→ report commit
→ P / PUBLICATION_EXACT_SHA
→ final synchronization
→ REVIEW_READY
→ STOP
```

GPT C07 independent review and Human acceptance remain pending. C07 is not
closed and C08 is not authorized.
