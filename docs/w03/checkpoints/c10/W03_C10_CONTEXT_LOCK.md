# FlowLens Industrial AI — W03-C10 Context Lock

```text
context_lock_status = LOCKED
checkpoint = W03-C10
task = W03-C10-I/H/R
contract_version = W03-C10-A-v1
entry_branch = feat/w03-ai-decision-loop
entry_sha = 147cefae890d3a450052298f0a331e1528e1f856
main_sha = 9d18ddde9fe933952a2661ee1419f13c8577605d
entry_ci = Run #80 / 37220934558 / SUCCESS
entry_class = P / PUBLICATION_EXACT_SHA
human_authorization = W03-C10 HUMAN AUTHORIZATION: APPROVED
business_acceptance = PENDING_PRODUCT_OWNER_DECISION
```

When the exact Human implementation-authorization line is present and mandatory
read-only preflight passes, Codex must publish this repository projection as
`context_lock_status = LOCKED`.

## 1. Mandatory read-only entry preflight

Before any repository write, verify:

```text
current branch = feat/w03-ai-decision-loop
local HEAD = 147cefae890d3a450052298f0a331e1528e1f856
tracking HEAD = 147cefae890d3a450052298f0a331e1528e1f856
direct remote HEAD = 147cefae890d3a450052298f0a331e1528e1f856
PR #6 HEAD = 147cefae890d3a450052298f0a331e1528e1f856
worktree/staging = CLEAN
ahead/behind = 0/0
main = 9d18ddde9fe933952a2661ee1419f13c8577605d
PR #6 = OPEN / DRAFT / NOT MERGED
auto-merge = ABSENT / DISABLED
Run #80 / 37220934558 = SUCCESS on entry SHA
Run #80 class = P / PUBLICATION_EXACT_SHA
Publication proof = PASS
Verification = PASS
Quality / Compose / W03 AI loop gate = SKIPPED
```

If any value differs, stop. Do not reset, rebase, amend, cherry-pick, merge,
force-push or silently rebase the contract.

## 2. C09 closure prerequisite

C09 is treated as effectively closed only because the final C09-C1 closeout commit
`147cefae890d3a450052298f0a331e1528e1f856` passed Run #80 and final synchronization was reported PASS.

C10 does not reopen C09.

## 3. Frozen entry identities

| Protected material | Git identity at C10 entry |
|---|---|
| `docs/sprints/W03_ai_decision_loop.md` | `365630e84339436efaa43061a3b04b2a05dcae12` |
| `docs/w03/AI_LOOP_CONSTITUTION.md` | `83bdae9c6511237397811b604d9562420ec40c0f` |
| `docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md` | `e45ed2ebb7df97ddae4ead18097df8f9e9f8de07` |
| `docs/w03/FAILURE_AND_DEGRADATION_POLICY.md` | `b57c867197d000271286cb81f8230de003779bd7` |
| `docs/w03/SEMANTIC_TRUST_CONTRACT.md` | `e120f4a8cd2f37e0f6084b86e6e606958c6ba68b` |
| `docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md` | `b49e749e8159214fb6624a2a5e2b904ef096fcd8` |
| `docs/w03/LOOP_EXECUTION_STATE_MACHINE.md` | `b82df602bb8cff414647e6ea5f61390031c31e63` |
| `.github/workflows/ci.yml` | `14c826b122b7103953e8b4539981004241205ba4` |
| `scripts/ci/classify_change.py` | `353df45732e77831a3ad92bf6f9a072db7ce3425` |
| `scripts/ci/verify_publication.py` | `8f97a117f936d9dce91957f7b44551acb5d5c2b6` |
| `docs/w03/reports/W03_C09_C1_FINAL_CLOSEOUT.md` | `612561da6ef78c75a28d9aabe8ac05ef8ef25a73` |
| `docs/w03/reports/W03_C09_GPT_INDEPENDENT_REVIEW_R1.md` | `510c32c1378bb4b36e8f7d8e272ec0335a269a2a` |
| `docs/w03/reports/W03_C09_R_DEVELOPMENT_ROUND_REPORT.md` | `b5fc30753010e36e65fd2fb06f74e3d47962e5c7` |
| `pyproject.toml` | `318bbc0a858f760e6c4d7a2d3fdbfcc111febb77` |
| `uv.lock` | `619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a` |
| `docker-compose.yml` | `5a0b6e8486edc69f9f79c7e1345a842aa412983c` |
| `src tree` | `cb53e0a3f008c1000e00ff0340e8b197cc878b35` |
| `tests tree` | `5b0493cae5b2b032eb9f70d65041f075bd2e32d9` |
| `migrations tree` | `c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433` |
| `apps tree` | `597399c7919982e9b2d54fc8b58fe6784cfe8585` |

## 4. Frozen C09 technical proof inherited by C10

```text
C09 implementation:
f214b20e54e2ff6ad3c1227ebb53e4aadaa204c9
Run #78 / 37216528805 / PASS
I / FULL_EXACT_SHA

C09 report publication:
330241be4039711e32d631a6d83eb36edd1f2888
Run #79 / 37218374366 / PASS
P / PUBLICATION_EXACT_SHA

C09 closeout:
147cefae890d3a450052298f0a331e1528e1f856
Run #80 / 37220934558 / PASS
P / PUBLICATION_EXACT_SHA

W03 AI loop gate:
F01-F10 PASS
38 selectors / 85 expanded cases PASS

C09 post-CI audit:
H01-H42 / 42 OF 42 PASS
```

C10 must not reinterpret those proofs as Product Owner business acceptance.

## 5. Authorized transitions

Allowed:

```text
C10 checkpoint/control package materialization
C10 acceptance-readiness dossier creation
W03 Sprint current-status normalization
read-only evidence extraction
existing test/CI execution
post-CI H01-H34 audit
C10 readiness report + CURRENT_STATE publication
```

Forbidden:

```text
runtime/source/test/workflow implementation
existing contract semantic weakening
new business threshold
new tool/capability
live provider call
operational write
C10 Human acceptance fabrication
C10 closeout
PR merge / draft-to-ready / auto-merge
```

## Observed entry and package verification

Mandatory read-only entry preflight: PASS before repository mutation. Local, tracking, direct remote and PR #6 source head matched the entry SHA; local/tracking/direct main matched the frozen main SHA. Worktree/staging were clean and ahead/behind 0/0. PR #6 was OPEN / DRAFT / NOT MERGED. The authenticated GitHub draft-state review surface showed merge disabled and no active auto-merge control. Run #80 classification logs bound P / PUBLICATION_EXACT_SHA to the entry SHA, Publication proof and Verification passed, and Quality/Compose/W03 were skipped.

Supplied ZIP SHA-256: 7c952fae08dd1d7a776495000b0f10d49d83fd874a90be33507565b920f8b8be.
All 19 SHA256SUMS.txt entries verified directly from ZIP bytes before copying. All 20 protected Git identities in Section 3 matched entry. Unmodified package projections are byte-identical; only the Human Authorization record and Context Lock receive the authorized state projection.

Lock published before the first dossier or sprint write. C10 context delta is limited to the authorized control/evidence documents. Dataset/scenario/model/prompt/tool registry and runtime inputs are inherited unchanged from accepted C01-C09; no runtime execution or live provider call is part of this round.
