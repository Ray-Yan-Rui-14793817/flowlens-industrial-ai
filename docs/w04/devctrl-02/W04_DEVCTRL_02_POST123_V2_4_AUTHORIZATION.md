# W04-DEVCTRL-02 POST123 V2.4 Human Authorization

Human authorization: APPROVED by the explicit pasted request on 2026-10-09.

The Human adopts FLOWLENS_W04_DEVCTRL_02_POST_123_RESILIENT_CUTOVER_TASK_V2_4.md (raw SHA-256 ea7ea2cc8a92e421ca4101104885e5d4442a42ef7d7269ecca56db8bd7d8d2df) as the current normative task. The complete task, current Repair-01 governance, workflow, weights, four helpers and three CI-control test files were read before any repository write. V2.3 is superseded and must not execute.

This authorization supersedes the historical Repair-01 sentence “A native failure grants no second repair commit” only for the two exact commits, scopes and gates below. Repair-01 history and both repaired test bodies remain frozen.

Human clarification on 2026-10-09: use exact integer millisecond loads and the lowest shard id for a true load tie. The Human explicitly approved assigning the zero-weight tests/test_c06_policy.py to shard 3. This corrects the §4.1 illustrative placement in shard 5; the other 61 file assignments and all seven nominal loads remain unchanged. Corrected file counts are 1,1,10,15,10,14,11. This clarification does not expand either allowlist or any stage gate.

## R2: final same-SHA migration proof

Exactly one commit, parent 76a5f207a343c673382490bba0c489cb8b667af6:

```text
ci(w04-devctrl-02): harden sharding against runner variance
```

Exact allowlist:

```text
.github/workflows/ci.yml
docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json
docs/w04/devctrl-02/W04_DEVCTRL_02_POST123_V2_4_AUTHORIZATION.md
docs/w04/devctrl-02/W04_DEVCTRL_02_POST123_V2_4_CONTEXT_LOCK.md
scripts/ci/plan_non_integration_shards.py
scripts/ci/pytest_outcome_receipt.py
scripts/ci/run_non_integration_shard.py
scripts/ci/verify_non_integration_shards.py
tests/test_ci_test_sharding.py
tests/test_c09_ci_gate.py
tests/test_ci_change_classifier.py
```

Use only the normative #122 JUnit-backed V2 evidence: 62 files, 6671.752 seconds, run #122 / 37889883403 / 9d5b6e3baea1a860446b70d9b254cc3dc41815a4. Remove progress timestamps and unseen-file defaults. Selected files must exactly equal modeled files; malformed, missing, extra, duplicate, nonfinite and negative weights fail closed.

Seven fixed deterministic file-atomic LPT shards, descending weight then path, lowest-load then lowest-id tie breaks. Preserve exact once-only node union, empty pairwise intersections, immutable HEAD binding, entry no-loss, canonical seals, all six terminal outcome categories and the three accepted Linux skips. Use one authoritative SHARD_COUNT = 7; matrix 0..6, max-parallel 7, fail-fast false, migration shard timeout 60 minutes. Every aggregate downloads exactly seven same-run exact-name/HEAD artifacts.

Keep legacy Quality integration and complete non-integration execution for this final same-SHA coverage and six-outcome equivalence proof. W03 may depend on classify-change only to remove ordering delay; preserve its runner, manifest, exact HEAD, class-P skip and final Verification enforcement. Compose and publication semantics stay frozen.

After normal push, wait for this exact SHA's terminal native CI. Require classifier/full route, legacy integration 70 passed, legacy non-integration 2807 selected / 2804 passed / exactly 3 accepted skipped / no failed,error,xfail,xpass, all seven shadow shards, aggregate, shadow integration, equivalence, Ruff, strict mypy, dependency lock, Compose, W03 38 selectors / 85 cases and Verification PASS. Longest actual shadow job/test duration must be <=45 minutes before B2. Functional failure stops at R2_CI_FAILED; successful proof with longest >45 minutes stops at TARGET_NOT_MET. No automatic repair or rerun.

## B2: conditional authoritative cutover

Only after R2's own native PASS and longest shadow shard <=45 minutes, exactly one commit:

```text
ci(w04-devctrl-02): cut over to seven-shard exact-SHA proof
```

Exact allowlist:

```text
.github/workflows/ci.yml
tests/test_ci_test_sharding.py
tests/test_c09_ci_gate.py
tests/test_ci_change_classifier.py
```

Rename the proven graph to static-and-plan, integration-and-data, non-integration and non-integration-aggregate. Remove duplicated legacy pytest execution and steady-state shadow-equivalence. Retain quality / Quality gate as a fail-closed compatibility aggregator over all three authoritative proof results, without PostgreSQL or tests. W03 stays early and Compose independent. Final Verification enforces every required result and preserves publication-only class P.

Timeouts in minutes: static-and-plan 15; integration-and-data 25; non-integration 55; aggregate 10; Quality 5; W03 15; Verification 5; Compose retain 15. Helpers, weights and governance are frozen after R2.

Wait for the exact B2 SHA's terminal native CI. Preserve 2807 non-integration and 70 integration node identities and accepted outcomes. PROOF_EXECUTION_ELAPSED <=60 minutes hard, <=45 target, <=35 stretch; ACTIVE_REQUIRED_JOB_DURATION_SUM <=197m14s hard. Report workflow elapsed, actual proof elapsed, active required duration sum, initial queue/start delay, dependency/runner waiting and all seven shard timings separately. A >45 but <=60 minute proof is an honest target miss at review-ready; a >60 minute proof is PERFORMANCE_HARD_FAIL.

## Frozen boundary and stop codes

Existing CI-control test bodies may evolve; node additions, removals, renames, parameterization, skip and xfail changes are forbidden. No runtime/product source, frozen C01-C07 source/tests, Repair-01 tests, dependencies, migrations/schema, W03 source/manifest, source-evolution manifest, Compose definition, publication routing or HGT/data authority changes.

No pytest-xdist, file splitting, sampling, retries/reruns, continue-on-error, cancel-in-progress, cross-run runtime proof, history rewrite, amend/rebase/reset/force push, B3, Stage C, C08, closeout, DEVCTRL-03, merge, branch deletion or main write. Normal pushes only; PR #7 remains OPEN / DRAFT / UNMERGED.

```text
W04_DEVCTRL_02_POST123_V24_CONTEXT_CHANGED
W04_DEVCTRL_02_POST123_V24_SCOPE_VIOLATION
W04_DEVCTRL_02_POST123_V24_NODESET_DRIFT
W04_DEVCTRL_02_POST123_V24_WEIGHT_EVIDENCE_INVALID
W04_DEVCTRL_02_POST123_V24_R2_CI_FAILED
W04_DEVCTRL_02_POST123_V24_TARGET_NOT_MET
W04_DEVCTRL_02_POST123_V24_B2_CI_FAILED
W04_DEVCTRL_02_POST123_V24_PERFORMANCE_HARD_FAIL
W04_DEVCTRL_02_POST123_V24_REQUIRES_GPT_CLARIFICATION
```

Maximum terminal authority after successful B2: REVIEW_READY_POST123_V24. Independent GPT review and Human acceptance remain pending; this is not closeout.

