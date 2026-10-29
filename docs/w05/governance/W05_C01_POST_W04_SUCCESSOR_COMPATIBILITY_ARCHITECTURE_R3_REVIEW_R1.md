# W05-C01 R3 Contract Amendment A1 — Review Binding

```text
REVIEW_ID = W05_C01_POST_W04_SUCCESSOR_COMPATIBILITY_ARCHITECTURE_R3_A1_REVIEW_R1
AUDIT_RESULT = PASS_FOR_STATIC_CONTRACT_SATISFIABILITY
A1_DESIGN = PASS
A1_DEEP_CHECK = PASS
A1_DEEP_REVIEW = PASS
UNRESOLVED_VALID_P1 = 0
UNRESOLVED_VALID_P2 = 0
IMPLEMENTATION_PROOF = NOT_RUN
NATIVE_PROOF = NOT_RUN
```

The previous R3 architecture PASS is revoked where it claimed that current R46 could remain
fully unchanged. The discovered pre-authoring contradiction is valid:

- pull_request/opened -> UNKNOWN / FULL_EXACT_SHA / ambiguous_event;
- the current R46 helper `_check_native_metadata` accepts only I/C;
- measured original native evidence cannot truthfully satisfy both.

A1 resolves only this lifecycle seam:

- classifier remains unchanged;
- verification full-route behavior remains unchanged;
- historical R46 remains unchanged at the historical anchor;
- current `test_r46_stage_b_exact_sha_full_native_ci` body remains unchanged;
- only current `_check_native_metadata` is allowed one bounded successor evolution:
  accepted classifier classes become I/C/UNKNOWN while FULL_EXACT_SHA remains mandatory;
- P and F remain rejected by R46;
- all remaining native evidence checks remain unchanged.

The W04 C09 contract verifier already treats `_check_native_metadata` as an authorized replay
symbol whose body may evolve while name/signature/decorators/annotation remain stable.

Human request for design -> deep check/review -> task/prompt authorizes this exact amended R3 task.

```text
HUMAN_DISPOSITION = PASS
R3_A1_HUMAN_ACCEPTANCE = ACCEPTED
R3_A1_EXECUTION_AUTHORIZATION = APPROVED_FOR_THIS_TASK_ONLY

C01_RECOVERY_EXECUTION = NO
C01_CLOSEOUT_AUTHORIZATION = NO
C02_AUTHORIZATION = NO
MERGE_AUTHORITY = NO
W06_AUTHORIZATION = NO
FLOWLENS_V1_0_RELEASE = NO
```
