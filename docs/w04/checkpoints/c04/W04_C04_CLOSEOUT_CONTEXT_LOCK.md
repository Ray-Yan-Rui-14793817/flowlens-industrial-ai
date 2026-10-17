# W04-C04 Final Closeout Context Lock

Prepared on 2026-10-07 before manifest mutation. This lock records the current
Human-authorized governance closeout scope and the read-only baseline checks.

```text
TASK: W04-C04-FINAL-CLOSEOUT / W04_C04_CLOSEOUT_TASK_V1.md
CONTEXT: LOCKED
CURRENT HEAD / STAGE D: cc7b378ee105a6adf4b155d2ebc83f846b116ad3
ORIGIN FEATURE HEAD: cc7b378ee105a6adf4b155d2ebc83f846b116ad3
BRANCH: feat/w04-evidence-investigation
ENTRY WORKTREE / INDEX: CLEAN
PR #7: OPEN / DRAFT / UNMERGED
W03 VERIFIED MAIN / PR BASE: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
STAGE D CI: #106 / 37567839234 / SUCCESS / Verification PASS
STAGE D ACTUAL CLASS / PROOF: P / PUBLICATION_EXACT_SHA
GPT INDEPENDENT IMPLEMENTATION REVIEW R1: PASS
CRITICAL: NONE
HIGH: NONE
BLOCKING MEDIUM: NONE
HUMAN C04 ACCEPTANCE: ACCEPTED
C04 CLOSEOUT AUTHORIZATION: APPROVED
ENTRY C04 STATE: AUTHORIZED
ENTRY C04 FREEZE / THREE BLOB OIDS: null / null
AUTHORIZED TRANSITION: W04-C04 AUTHORIZED -> CLOSED
ACCEPTED SOURCE FREEZE SHA: 6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1
W04-C05: NOT AUTHORIZED
```

The pasted current request supplies Human authorization. The attached task
defines execution scope and the attached GPT review supplies the independent
review decision. Codex preserves that review rather than issuing its own review
or self-approving acceptance. The current authorized task contract governs this
closeout; frozen W1/W2/W03 and C01/C02/C03 invariants remain authoritative.

## Package identity

Input archive: `FlowLens_W04_C04_FINAL_CLOSEOUT_HANDOFF_V1.zip`.
Its supplied review will be copied byte-for-byte into the approved repository
path. Package identities measured before repository mutation:

| Package entry | Bytes | SHA-256 |
|---|---:|---|
| `W04_C04_CLOSEOUT_PROMPT_V1.md` | 12270 | `7cb34fb2916e921fcb39f584f4a748a2d099cbaddb69f894ee56572be99c646f` |
| `W04_C04_CLOSEOUT_TASK_V1.md` | 11596 | `b46cb574409c97d654fa155e67ed734775d8555a56c522d6c99598c44de69370` |
| `W04_C04_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md` | 5060 | `8a3961277eb5364d3087821b9b874a0a9fc3ea195e70916dbbc3594ebb0c443d` |

## Frozen development chain

Entry / C03 final closeout: `ffaba2672de74836c12d4a122352b252785a0897`.

| Stage | Exact SHA | Native CI | Actual class / proof |
|---|---|---|---|
| A — source authorization + P40 | `2f63616c31b542c1bd93981fad4b27ac5bddfdbc` | #103 / 37472062606 / SUCCESS | I / FULL_EXACT_SHA |
| B — registry + query contract | `16aa203aff146fbc2a26c5ce37c82ed1ce287402` | #104 / 37477003142 / SUCCESS | I / FULL_EXACT_SHA |
| C — accepted implementation | `6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1` | #105 / 37497691587 / SUCCESS | I / FULL_EXACT_SHA |
| D — development report publication | `cc7b378ee105a6adf4b155d2ebc83f846b116ad3` | #106 / 37567839234 / SUCCESS | P / PUBLICATION_EXACT_SHA |

The committed history preserves Stage A, Stage B, quota continuation and
DR-C04-01 hardening, Stage C, then Stage D. Stage D changes only the development
round report. Its full source-evolution publication proof passed at exact SHA.

## Accepted source identity

Each identity below was verified with `git rev-parse` at both accepted Stage C
and current Stage D HEAD before mutation; both references returned the exact
listed OID. Stage C is an ancestor of Stage D.

| Source path | Stage C = HEAD Git blob OID |
|---|---|
| `src/flowlens/investigation/c04_navigation.py` | `98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4` |
| `src/flowlens/investigation/c04_queries.py` | `dc22c7e532a4b62ccfffec2210bc2a6306d97234` |
| `src/flowlens/investigation/c04_registry.py` | `fbe6f0603d7b0634426ac0034033089eb55af4d7` |

Manifest entry identity at baseline:
`cb562431242c5c6851aa6bb42f959c8fe7e0a7f3` (Git blob),
`7e6d1b5c8cc86725c399dae7b421076a5cf53af830145dd0b7978058a5ab18eb`
(SHA-256 of committed bytes). Schema `w04-source-evolution-manifest-v1`, policy
`W04-DEVCTRL-01`, W03 baseline `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`
and root `src/flowlens/investigation` remain unchanged.

## Prior CLOSED checkpoints

| Checkpoint | Frozen source SHA | Existing source | Frozen blob OID |
|---|---|---|---|
| C01 CLOSED | `084c2fea93d0e021994de015c986de9ff92bf9a3` | `__init__.py` | `c23929f85dccd78bc72ef3b2b1415c6e8eaf0452` |
| C01 CLOSED | same C01 SHA | `contracts.py` | `0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e` |
| C01 CLOSED | same C01 SHA | `enums.py` | `9c818780423f32f144b18666784ebc9ea3abdccc` |
| C02 CLOSED | `18648915414a26dddbdc904965663730ea631cf2` | `c02_binding.py` | `5f0af237ed465fa83e5a3b84954512b1f3125551` |
| C03 CLOSED | `42047bcfe6591f7c9ed9b0034bd94467401ba72f` | `c03_planning.py` | `21d0055e12d86e6333a836d363d6e266cb0fcbd7` |

All paths are under the unchanged investigation root. The C01/C02/C03 manifest
objects and their documentation trees must remain identical to Stage D.

## Frozen production and harness identities

| Repository path | Stage D Git blob / tree OID |
|---|---|
| `scripts/ci/verify_w04_source_evolution.py` | `4efaefed505e24796a0c2fa545ce4b7eb252d70a` |
| `scripts/ci/classify_change.py` | `fd9e99c6b55b85f184198c51f0f97ba16323ce32` |
| `.github/workflows/ci.yml` | `14c826b122b7103953e8b4539981004241205ba4` |
| `scripts/ci/verify_publication.py` | `8f97a117f936d9dce91957f7b44551acb5d5c2b6` |
| `tests/test_investigation_evidence_queries.py` | `54f43e27ce42c0ae6ea903d7b278b916748f40ed` |
| `tests/test_investigation_evidence_navigation.py` | `74e15223abc0accdfd3cb569764f9f94d5f3d70e` |
| `tests/integration/test_investigation_evidence_navigation_database.py` | `fab7e9180e19635eb886624d98c759a669ded5ec` |
| `tests/test_investigation_planning.py` | `2f326879b87fffcd1385a9188cf92ac40f4779b8` |
| `src/flowlens/decision/temporal.py` | `70ae018f4b50ac6ed45e894d6726e9ccee345c8a` |
| `src/flowlens/decision/trust.py` | `f216d22f1d6862e1eef886dfbe4c3af16f396ec1` |
| `src/flowlens/db/decision_snapshot.py` | `0323ad4ecf0c50abda42a8ab4714d59861ad98c3` |
| `src/flowlens/data/models` | `12a1ec70707ff4644b6d6bccb31eec59fb7230d3` |
| `src` | `fee1b88425b461a6266685a80faa39165a5ef7e5` |
| `tests` | `9f7acfab67d4198a2bdf32e7e29f8136ea8ed6dd` |
| `scripts/ci` | `b8ded9847fa8c23309bbd1af11847c8b27666685` |
| `.github` | `978501bf7003ab05e903e22d3930ee5c97470974` |
| `docs/w03` | `cb81e388c6c44a9900575ef2e72161dc0205be94` |
| `docs/w04/checkpoints/c01` | `158218fdd671c197e9f386315e64994fdc289675` |
| `docs/w04/checkpoints/c02` | `2645a039994d69535e465d3534cfd0ede72e09ca` |
| `docs/w04/checkpoints/c03` | `f62d380d020d04bc99a3fbc04eed93c6bc9123ad` |
| `pyproject.toml` | `318bbc0a858f760e6c4d7a2d3fdbfcc111febb77` |
| `uv.lock` | `619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a` |
| `docker-compose.yml` | `5a0b6e8486edc69f9f79c7e1345a842aa412983c` |
| `migrations` | `c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433` |
| `apps` | `597399c7919982e9b2d54fc8b58fe6784cfe8585` |
| `docs/w04/checkpoints/c04/W04_C04_CONTEXT_LOCK.md` | `ec0f6539987872bc2134505f919ceac7907922ed` |
| `docs/w04/checkpoints/c04/W04_C04_HUMAN_AUTHORIZATION.md` | `ee5d8490e9bfdc5f36d6d21620d953e66131ae1c` |
| `docs/w04/checkpoints/c04/W04_C04_R_DEVELOPMENT_ROUND_REPORT.md` | `084662173bd7968ae8d72adb9adce4d670de12cd` |

## CLOSED lifecycle proof method

The existing N52 harness accepts exactly AUTHORIZED/null or CLOSED/non-null
freeze and three OIDs. CLOSED verifies each source against both `freeze:path`
and `HEAD:path`. P40 preserves C01/C02/C03 identities and invokes the unchanged
production verifier. The production verifier supports the authorized transition,
requires ancestor freeze identity and enforces frozen source blobs/modes and the
worktree manifest's identity with committed HEAD. No harness repair is needed.

The accepted C03 closeout records document a disposable committed Git-copy
method for precommit CLOSED proof because exact-HEAD gates require a committed
manifest. Use that same method: copy only the six authorized pending paths into
an isolated full-history local clone, make a local probe commit there, and run
the actual N52 lifecycle/committed-governance selectors, P40, all source-evolution
tests and unchanged CLI against its exact HEAD. The copy is never pushed; its
probe SHA is not the real closeout SHA or accepted source freeze. The primary
repository receives one final closeout commit only. Immediately after that real
commit, repeat actual CLOSED HEAD governance proof and CLI before normal push.

This method preserves committed-HEAD enforcement; it does not substitute a
dirty-worktree skip, bypass, test edit or modified production verifier. The
precedent is recorded in
[C03 context lock](../c03/W04_C03_CLOSEOUT_CONTEXT_LOCK.md) and
[C03 final closeout report](../c03/W04_C03_FINAL_CLOSEOUT_REPORT.md).

## Exact scope and stop boundary

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c04/W04_C04_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md
docs/w04/checkpoints/c04/W04_C04_HUMAN_ACCEPTANCE.md
docs/w04/checkpoints/c04/W04_C04_CLOSEOUT_AUTHORIZATION.md
docs/w04/checkpoints/c04/W04_C04_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/checkpoints/c04/W04_C04_FINAL_CLOSEOUT_REPORT.md
```

Hard forbidden: `src/**`, `tests/**`, `scripts/ci/**`, `.github/**`, the three
existing C04 records listed above, `docs/w04/checkpoints/c01/**`,
`docs/w04/checkpoints/c02/**`, `docs/w04/checkpoints/c03/**`, `docs/w03/**`,
`pyproject.toml`, `uv.lock`, `docker-compose.yml`, `migrations/**`, `apps/**`.
No seventh tracked path, dependency, migration, runtime/test/control repair,
operational mutation, C05, merge or branch deletion.

Expected C / FULL_EXACT_SHA is advisory; actual native classifier controls.
Effective closure requires the new closeout SHA's own Verification PASS, with
Classify/Quality/Compose/W03 PASS and Publication SKIPPED on the full route.
The immutable final report must retain its future SHA/CI pending markers.

Context change: STOP `W04_C04_CLOSEOUT_CONTEXT_CHANGED`.
Source identity mismatch: STOP `W04_C04_SOURCE_FREEZE_MISMATCH`.
Frozen CLOSED gate failure: STOP `W04_C04_CLOSEOUT_REQUIRES_GPT_CLARIFICATION`.
Final CI failure/cancel: STOP `W04_C04_CLOSEOUT_CI_FAILED` with exact SHA/run/
class/job/step/evidence. No amend or auto-repair. Stop after effective C04
closure; W04-C05 remains NOT AUTHORIZED.
