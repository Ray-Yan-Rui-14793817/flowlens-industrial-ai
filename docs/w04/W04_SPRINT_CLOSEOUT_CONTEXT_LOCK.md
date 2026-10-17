# W04 Sprint Closeout Context Lock

Locked 2026-10-16T13:28:16.272632+08:00 (Asia/Shanghai), before Phase-2 document authoring. This is development context, not runtime evidence.

## Authority and immutable inputs

```text
PARENT_TASK = W04-SPRINT-FINAL-CLOSEOUT-PR7-READINESS-V1
PARENT_TASK_RAW_SHA256 = 6648278c758ab4c73d18615c405c2280b84ab43ded08a45a3ccb354496a3455f
RESUME_TASK = FLOWLENS_W04_SPRINT_FINAL_CLOSEOUT_PR7_READINESS_RESUME_FROM_PREP146_TASK_V1.md
RESUME_TASK_RAW_SHA256 = f5c4641339a8250d10c5c2d983d3524740a2c01b5af67e8b3f747c5abd39fcef
GPT_REVIEW_RAW_SHA256 = 061fc3f41659499fc7e1069345abe7b1d0feeab65504eb79e48b6a929665de59
ORIGINAL_HUMAN_AUTHORITY_RAW_SHA256 = e165fa2945ce0cf0c8fc230cb5faf5f65d7ce3021af8817bd0830168a61a3f5d
RESUME_HUMAN_REQUEST_RAW_SHA256 = c47ce37acfe287fa87b082da9152f0e232cf7906df40a97320f165dc39064ac0
W04_SPRINT_FINAL_REVIEW = ACCEPTED BY HUMAN
W04_SPRINT_CLOSEOUT_AUTHORIZATION = APPROVED
PR7_READINESS_AUTHORIZATION = APPROVED
PR7_MERGE_AUTHORIZATION = NOT GRANTED
```

The original Human request remains the verbatim authority source. The resume request continues that authorization and replaces neither its text nor its authority. The supplied GPT review is copied byte-identically. Human prose is preserved verbatim with repository LF line endings; original CRLF bytes and their raw SHA-256 remain in the consolidated evidence ZIP.

## Recovered exact Prep boundary

```text
C10_FINAL_SHA = 232bfb390babce30417b8cdb9a6660663eb3c3f1
C10_FINAL_CI = #145 / 38709171796 / SUCCESS / attempt 1
LOCAL_HEAD = TRACKING_HEAD = DIRECT_ORIGIN_HEAD = PR7_HEAD = c8b29cbcffe1886412de4a31b75905f6397043fb
PREP_PARENT = 232bfb390babce30417b8cdb9a6660663eb3c3f1
PREP_SUBJECT = ci(w04): admit sprint closeout lifecycle
PREP_CI = #146 / 38735686969 / SUCCESS / attempt 1
PREP_CLASS = C / FULL_EXACT_SHA
PREP_LIFECYCLE = W04_SPRINT_CLOSEOUT_PREP_01
MAIN_BASE = af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
AHEAD_BEHIND = 0/0
WORKTREE_INDEX = CLEAN
PR7_ENTRY = OPEN / DRAFT / UNMERGED / MERGEABLE TRUE
PREP_TREE = c60ba988e4dbe45ac2510934ba4d102758b6d996
PREP_VERIFIER_BLOB = 788a9dd54fcf6784d0e336a4f360ded8470b7e4a
PREP_VERIFIER_RAW_SHA256 = 0d2e14640b8eaa5583f97bd5e2a89d6e9df57a0aeb6129087db0f95a6c23aeff
SOURCE_EVOLUTION_MANIFEST_RAW_SHA256 = d22a12306f8fe98952b9e35a5f166f29fee968c9aedcff27511da59889c20c2d
EXTERNAL_CONTEXT_LOCK_RAW_SHA256 = b8d4f32457ae492de636f854e8d4ebd0db2b7557b8c73aa5e6202ae758280afa
```

All 519 existing tracked files and their Git tree were locked before authoring. Prep changed only the verifier, with 430 additions / 3 deletions. Phase 1 is complete: no second Prep, verifier modification, Prep push or #146 rerun is permitted. The prior interruption was an automatic approval-review quota failure; source and CI were not repaired during recovery.

## Independently reconstructed Prep proof

Original GitHub run/job metadata, three original gate/classifier logs, seven shard logs and eleven original ZIPs were read. Every ZIP matches its GitHub SHA-256 digest and exact head/run binding. Original JUnit/receipts were independently reaggregated.

```text
NONINTEGRATION = 2997 selected / 2994 passed / 3 accepted Linux skips
FAILED / ERROR / XFAIL / XPASS = 0
ENTRY_NO_LOSS = PASS
EXACT_UNION = PASS
EXACT_ONCE = PASS
INTEGRATION = 70 PASS
W03 = 38 selectors / 85 cases PASS
W04 = 9 families / 67 selectors / 81 cases PASS
NODE_DIGEST = 9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a
WEIGHTS_DIGEST = a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851
W04_GATE_MANIFEST_RAW_SHA256 = d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1
W04_GATE_MANIFEST_CONTENT_SHA256 = 937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad
PLAN_SHA256 = 9f145374056901cc1caeb1a1dde54bf80a0b0a2625bf857a08423221b1db1a28
C10_DEVELOPMENT_CONTROLS = 32 PASS
C10_CLOSEOUT_CONTROLS = 60 PASS
SPRINT_CONTROLS = 60 PASS
LEGACY_ADVERSARIAL_CONTROLS = 172 PASS
ACTUAL_SHELL_TRUTH_CASES = 223 PASS
LONGEST_SHARD_LOG_ELAPSED = 1836.751s
LONGEST_SHARD_API_ELAPSED = 1839s
LONGEST_PYTEST_SUITE = 1805.959s
ALL_SHARD_JOB_AND_PYTEST_LT_3300S = PASS
```

The API measures job start-to-completion including setup outside the first/last native log timestamps; both measures and every JUnit suite/testcase-time sum are below 3300 seconds. Seven shards, max parallel 7, weights, node identities and the 65-minute ceiling remain unchanged.

The repeated read-only security audit covered 163 reachable commits / 751 blobs: no tracked sensitive file, private key or live external credential identified. Three matches are the same synthetic Human-note test sentinel and its baseline copies. All 103 credential-style URIs are local/test defaults or mocked redaction fixtures. The local PostgreSQL fallback is DEVELOPMENT_TEST_DEFAULT / NON-EXTERNAL; values are not reproduced here. No dependency or history change was made.

## Exact Phase-2 delta

Modify only:

```text
README.md
AGENTS.md
docs/CURRENT_STATE.md
```

Add only:

```text
docs/w04/W04_GPT_INDEPENDENT_DEEP_REVIEW_R1.md
docs/w04/W04_SPRINT_HUMAN_ACCEPTANCE_AND_AUTHORIZATION.md
docs/w04/W04_SPRINT_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/W04_SPRINT_FINAL_CLOSEOUT_REPORT.md
docs/w04/W04_PR7_READINESS_REPORT.md
```

Parent must be the exact successful Prep SHA. Subject must be `docs(w04): close sprint and prepare PR #7 review`. A fresh full-history LF candidate must prove exact statuses, identical review bytes, original Human prose, unchanged verifier/source evolution/all other tracked objects, whitespace, Ruff, strict mypy, security and committed-head `W04_SPRINT_FINAL_CLOSEOUT`. Any failed candidate gate means STOP; no automatic repair or primary mutation.

Freeze all src, tests, workflows, scripts/ci, dependencies/lock, migrations/schema, C01-C10 checkpoint evidence, C10 closeout records, source-evolution manifest and .gitattributes. No runtime/product change is authorized.

## Final evidence and readiness boundary

```text
SPRINT_FINAL_SHA = GENERATED POST-COMMIT / NOT YET CREATED
SPRINT_FINAL_NATIVE_CI = GENERATED POST-COMMIT / PENDING
EXPECTED_FINAL_CLASS = UNKNOWN / FULL_EXACT_SHA
EFFECTIVE_SPRINT_CLOSURE = ONLY AFTER OWN-SHA ATTEMPT-1 FULL SUCCESS AND FRESH FOUR-HEAD SYNC
PR7_READY = ONLY AFTER THAT PROOF AND AUTHORIZED TITLE/BODY UPDATE
PR7_MERGE = NOT AUTHORIZED
AUTO_MERGE / MERGE_QUEUE / BRANCH_DELETION / MAIN_WRITE = NOT AUTHORIZED
POST-W04_IMPLEMENTATION / W05 = NOT AUTHORIZED
FLOWLENS_V1_0 = NOT RELEASED
```

Actual Final SHA/run belong in the post-CI handoff and PR body. This immutable pre-commit lock does not invent them. Carry NB-C09-01, NB-C10-ENV-01, NB-W04-CI-01, NB-W04-GOV-01, NB-W04-PR-SIZE-01 and NB-W04-CI-02 without repair.
