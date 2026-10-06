# W04-C03 Final Closeout Context Lock

Locked before manifest mutation, after repair CI #101 and all resume gates passed.
This final phase changes governance documents and the authorized manifest only.

```text
TASK: W04-C03-FINAL-CLOSEOUT / RESUME-AFTER-QUOTA-V1
CONTEXT: LOCKED
REVIEW-READY STAGE C: 3b38e95affd1847c73b5ce719775a20c8b4ae3e0
CLOSEOUT EXECUTION BASELINE / REPAIR SHA: 0ff0f6b929e4134483e07ba6bd1577bbc2a77ca1
ENTRY WORKTREE / INDEX: CLEAN
BRANCH: feat/w04-evidence-investigation
PR #7: OPEN / DRAFT / UNMERGED
W03 VERIFIED MAIN / PR BASE: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
GPT INDEPENDENT DEEP REVIEW R1: PASS
HUMAN C03 ACCEPTANCE: ACCEPTED
C03 CLOSEOUT AUTHORIZATION: APPROVED
P40 CLOSEOUT REPAIR AUTHORIZATION: APPROVED
REPAIR CONTINUATION: APPROVED
REPAIR CI: #101 / 37436732985 / SUCCESS / Verification PASS
REPAIR ACTUAL CLASS / PROOF: I / FULL_EXACT_SHA
REPAIR SCOPE: tests/test_investigation_planning.py only; +13 / -3
RUNTIME SOURCE CHANGE DURING REPAIR: NONE
PRODUCTION VERIFIER CHANGE: NONE
ENTRY C03: AUTHORIZED / null source_freeze_sha / null blob_oid
AUTHORIZED TRANSITION: W04-C03 AUTHORIZED -> CLOSED
C03 RUNTIME FREEZE SHA: 42047bcfe6591f7c9ed9b0034bd94467401ba72f
C03 RUNTIME BLOB: 21d0055e12d86e6333a836d363d6e266cb0fcbd7
FINAL CLOSEOUT TEST/HARNESS CHANGE: NOT AUTHORIZED
PR MERGE / BRANCH DELETION: NOT AUTHORIZED
W04-C04: NOT AUTHORIZED
```

## Authority and preserved supplied records

The Human's direct pasted acceptance, closeout, repair and current resume requests
supply authorization. The attached task defines the bounded procedure; attached
material does not independently expand the Human's request. The current resume
continues the existing approved closeout and forbids repeating the P40 repair.

The supplied R1 review and Human acceptance are copied byte-for-byte to their
canonical repository paths. R1 describes the original Stage B harness blob
`3b54b9e84f717ca841f8707855c97772c340da3d`, review-time acceptance PENDING,
and closeout NOT YET ISSUED. Those historical statements are preserved; later
Human acceptance and closeout/repair approvals are recorded here and in the
supplied authorization plus its explicitly sourced continuation addendum.
The original development report remains immutable.

| Input | Original SHA-256 |
|---|---|
| W04_C03_GPT_INDEPENDENT_DEEP_REVIEW_R1.md (Human-supplied Downloads file) | e2db8710eeec53fa86d4bc6c1815b183f8d520e8ef897845fc6625c406069987 |
| W04_C03_HUMAN_ACCEPTANCE_ACCEPTED.md (original closeout ZIP) | bfc4fd3f20f3c3f87e869d18a15afa1282e46f3350d3622be37a2be8ca9ea260 |
| W04_C03_CLOSEOUT_AUTHORIZATION_APPROVED.md (original 803-byte prefix) | 25eb97350894da9ad4d239b73a59c0be56b0cd37019ae8913a7106198d60836d |
| W04_C03_CLOSEOUT_REPAIR_01_TASK_V1.md | 2a2ca51d55dabff4b14fca59aa26ccab5a5badcc51dc590a4a54e842d3d67835 |
| W04_C03_CLOSEOUT_REPAIR_01_PROMPT_V1.md | e9039286d8c1be8ec6f70650fa950ff00a41a118cf676be9204803449fd9d42f |
| W04_C03_CLOSEOUT_RESUME_AFTER_QUOTA_TASK_V1.md | 25c1aeb11a1e1ea101bf2e3e3a329d22a1c54cc31af65027c15aad1c5101e267 |
| W04_C03_CLOSEOUT_RESUME_AFTER_QUOTA_PROMPT_V1.md | a42512bdf84a2f29bcd6e98ee5af08bb41b6ff766ad2e663a974897356252be1 |

Package hashes match their manifests. Original authorization bytes remain the
exact prefix of the canonical authorization file. Its appended addendum records
the later separately authorized repair and resume, without retroactively changing
the original closeout's prohibition on test changes.

## Immutable history and exact-SHA evidence

```text
dd21e238e6047ed8181d8aaa3636eb4feca2763a (C02 CLOSED)
-> c7995c11e78dab9d69a0cfe2ef400f0d8b88357e (Stage A)
-> 42047bcfe6591f7c9ed9b0034bd94467401ba72f (Stage B)
-> 3b38e95affd1847c73b5ce719775a20c8b4ae3e0 (Stage C)
-> 0ff0f6b929e4134483e07ba6bd1577bbc2a77ca1 (P40 repair)
```

Direct parents and exact deltas are verified: Stage A three control paths;
Stage B runtime and harness only; Stage C development report only; repair P40
harness only. AST comparison confirms all other tests and P40's C01/C02 frozen
checks, exact C03 path and generic verifier invocation are unchanged.

| Stage / CI | Actual route and result |
|---|---|
| [A / #98 / 37409873083](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37409873083) | C / FULL_EXACT_SHA / SUCCESS |
| [B / #99 / 37424416486](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37424416486) | I / FULL_EXACT_SHA / SUCCESS |
| [C / #100 / 37428956715](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37428956715) | P / PUBLICATION_EXACT_SHA / SUCCESS |
| [Repair / #101 / 37436732985](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37436732985) | I / FULL_EXACT_SHA / SUCCESS |

Native GitHub metadata and logs were read independently of the development
report. Repair classifier proves exact Stage C-to-repair delta and repair HEAD.
Quality proves 48 integration cases and 1830 non-integration cases PASS, Ruff PASS,
strict mypy 149 files PASS and 43-package dependency lock PASS. Compose PASS.
Frozen W03 F01-F10 PASS: 38 selectors / 85 cases at exact repair SHA, manifest
SHA-256 `bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990`.
Verification 112194384694 PASS; Publication skipped under unchanged policy.

After normal fetch, local HEAD, origin branch and live PR head equal repair SHA.
Repaired P40 and unchanged full source verifier pass at this clean entry. C01/C02
remain CLOSED, C03 remains AUTHORIZED/null/null, five allowed source additions;
entry manifest SHA-256
`e96108099437cff158415ad23c6cc01661756daf3170bf7ded3a73d94858ac25`.

## Authorized freeze and protected identities

Only the existing C03 state, source_freeze_sha and c03_planning.py blob_oid may
change. The sole path remains `src/flowlens/investigation/c03_planning.py`.
Runtime freeze is Stage B; repair SHA is execution/evidence baseline only.
C01/C02 entries, top-level fields and all path lists remain byte-equivalent.
No C04 entry is added.

| Protected path | Repair-baseline Git identity |
|---|---|
| src | 8a517088a9be09756a3a7cd622423e6846eaeb81 |
| tests | 6a33bfef0ad23d9ab6fdcd3dabe3915f84d5b929 |
| scripts/ci | b8ded9847fa8c23309bbd1af11847c8b27666685 |
| .github | 978501bf7003ab05e903e22d3930ee5c97470974 |
| docs/w03 | cb81e388c6c44a9900575ef2e72161dc0205be94 |
| docs/w04/checkpoints/c01 | 158218fdd671c197e9f386315e64994fdc289675 |
| docs/w04/checkpoints/c02 | 2645a039994d69535e465d3534cfd0ede72e09ca |
| docs/w04/checkpoints/c03/W04_C03_R_DEVELOPMENT_ROUND_REPORT.md | 44d94fc21a971298c0c7d99dabcd3d08f7de1daa |
| pyproject.toml | 318bbc0a858f760e6c4d7a2d3fdbfcc111febb77 |
| uv.lock | 619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a |
| docker-compose.yml | 5a0b6e8486edc69f9f79c7e1345a842aa412983c |
| migrations | c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433 |
| apps | 597399c7919982e9b2d54fc8b58fe6784cfe8585 |

## Exact six-path allowlist and completion boundary

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c03/W04_C03_GPT_INDEPENDENT_DEEP_REVIEW_R1.md
docs/w04/checkpoints/c03/W04_C03_HUMAN_ACCEPTANCE.md
docs/w04/checkpoints/c03/W04_C03_CLOSEOUT_AUTHORIZATION.md
docs/w04/checkpoints/c03/W04_C03_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/checkpoints/c03/W04_C03_FINAL_CLOSEOUT_REPORT.md
```

No seventh path, runtime/test edit, CI-policy edit, dependency change, C04
EvidenceQuerySpec/adapter/traversal, operational mutation, merge or branch deletion.
The branch remains retained. Accepted local Windows CRLF limitations and the
locked Starlette TestClient/httpx warning are carried without repair.

The verifier requires the worktree manifest to match committed HEAD. Pending
CLOSED parsing/transition/source checks and disposable committed-copy full proofs
are distinct from actual repository exact-HEAD proof, which runs immediately
after the final commit and before its normal push. No production verifier is
changed to bypass that rule.

Create one new direct child of repair SHA. Expected C / FULL_EXACT_SHA is advisory;
report actual native routing. Closure becomes effective only after the new
closeout SHA's Verification gate passes. The final handoff attests that generated
SHA and completed run without amending these pre-commit records.

If final CI fails/cancels, STOP W04_C03_CLOSEOUT_CI_FAILED with exact SHA/run/job/
step/evidence. No amend or auto-repair. Do not begin W04-C04.
