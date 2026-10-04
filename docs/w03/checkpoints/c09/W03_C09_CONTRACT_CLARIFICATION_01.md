# FlowLens Industrial AI — W03-C09 Contract Clarification 01

```text
checkpoint = W03-C09
base_contract = W03-C09-A-v1
clarification = W03-C09-CONTRACT-CLARIFICATION-01
effective_contract = W03-C09-A-v1.1
entry_sha = d71d5baeb0862f2706358c26e182554b3807e8f6
status = GPT_CLARIFICATION_FROZEN / PRODUCT_OWNER_APPROVAL_REQUIRED
```

## 1. Why this clarification exists

The original V1 execution task required both (a) exact pytest node IDs and (b)
`observed test count = target count`. The frozen V1 manifest, however, contains
38 exact **test-function selectors**, and 10 of those functions are
parameterized. Therefore one selector may intentionally collect multiple leaf
test cases.

Codex correctly stopped before repository mutation because interpreting a
parameterized function selector as one leaf node would either discard accepted
regression cases or silently change the counting contract.

This is a GPT-package contract defect, not a repository defect and not a C01-C08
semantic defect.

## 2. Approved resolution design

Clarification-01 chooses the second safe option identified by Codex:

```text
KEEP exact frozen function selectors
+
FREEZE expanded pytest case counts
```

Do **not** replace the parameterized functions with a hand-written list of
pytest-generated leaf IDs. Generated parameter IDs are evidence, not the stable
contract key. The stable contract key is the exact function selector plus its
frozen expanded case count.

## 3. Frozen selector semantics

A C09 manifest target is now exactly:

```json
{
  "selector": "tests/path.py::test_function_name",
  "expected_cases": 1
}
```

Rules:

```text
selector must identify exactly one test function
selector may expand through pytest parameterization
selector itself must NOT contain a parameter suffix like [case]
selector may not use wildcard / -k / marker / shell syntax
expected_cases must equal the exact collected leaf-case count
all collected leaf cases under that selector must execute
all leaf cases must pass with zero skip/xfail/xpass/error/failure
missing or renamed selector = FAIL
expanded count drift = FAIL
partial parameter execution = FAIL
```

## 4. Frozen count audit at entry SHA

The amended manifest freezes:

```text
TOTAL FUNCTION SELECTORS: 38
PARAMETERIZED SELECTORS: 10
TOTAL EXPANDED TEST CASES: 85
```

Family expanded counts:

```text
F01 CORE_CONTRACTS: 3
F02 TEMPORAL_SEMANTIC_TRUST: 7
F03 SIGNAL_DIAGNOSIS_FAIL_CLOSED: 10
F04 COUNTERFACTUAL_ISOLATION: 5
F05 RECOMMENDATION_ABSTENTION: 11
F06 HUMAN_AUTHORITY_AUDIT: 6
F07 PROTECTED_EVALUATION_REPLAY: 11
F08 LLM_GROUNDING_SCHEMA_INJECTION: 6
F09 REAL_DATASET_BINDING_DIRECTION: 6
F10 RUNTIME_CAPABILITY_ISOLATION: 20
TOTAL: 85
```

The ten parameterized selectors have frozen expanded counts:

```text
tests/test_decision_temporal.py::test_cross_dataset_future_tail_preserves_normalized_semantics = 5
tests/test_c03_harness.py::test_all_critical_conflicts_fail_closed = 3
tests/test_c03_harness.py::test_cross_dataset_normalized_future_tail_replay = 5
tests/test_c03_harness.py::test_runtime_source_audit_rejects_fully_qualified_forbidden_surface = 16
tests/test_c04_simulation.py::test_baseline_mutation_on_every_error_path_is_a_hard_fail = 3
tests/test_c05_policy.py::test_strict_neutral_blocker_matrix_is_fail_closed = 8
tests/test_c06_human.py::test_canonical_event_construction_for_every_decision = 3
tests/test_c07_replay.py::test_required_replay_matrix = 6
tests/test_c07_harness.py::test_h31_fresh_runtime_imports_do_not_reach_evaluation_or_hgt = 4
tests/integration/test_c03_decision_database.py::test_scenario_business_facts_direction_smoke = 4
```

All other 28 selectors freeze `expected_cases = 1`.

## 5. Runner enforcement

The runner may execute one selector at a time or a family batch, but it must be
able to prove the selector-to-expanded-case mapping. For each selector it must
verify the collected leaf count equals `expected_cases`. For each family it must
verify the sum equals the family's frozen `expected_cases`. The global sum must
be exactly 85.

Successful summary evidence should distinguish selectors from expanded tests,
for example:

```json
{
  "id": "F02 TEMPORAL_SEMANTIC_TRUST",
  "status": "PASS",
  "selectors": 3,
  "tests": 7
}
```

Leaf node IDs observed from collection/execution should be retained in test/log
evidence where useful, but they are not substituted into the manifest.

## 6. What does not change

Clarification-01 changes no proof family, no selected test function, no runtime
source, no C01-C08 semantic contract, no C08 prompt/provider/model boundary, no
Week 2 semantics, no dependency, no schema/migration, no CI trigger scope, no
classifier rule, no operational capability and no C10 authority.

The original Human Authorization remains the base authorization for C09 scope,
but this post-authorization contract clarification must receive a separate
Product Owner approval before Codex resumes mutation:

```text
W03-C09 CONTRACT CLARIFICATION-01: APPROVED
```

Until that exact line is present, repository mutation remains blocked.

## 7. Supersession rule

Where V1 package text says:

```text
exact pytest node IDs
selectors other than exact node IDs are rejected
observed test count = expected exact target count
```

Clarification-01 supersedes those phrases with:

```text
exact pytest function selectors
parameterization expansion explicitly permitted
per-selector expected_cases exact
family expected_cases exact
global expanded case count = 85
```

All other V1 requirements remain in force.
