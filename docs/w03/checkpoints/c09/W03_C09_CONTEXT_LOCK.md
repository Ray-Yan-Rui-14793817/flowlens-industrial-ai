# FlowLens Industrial AI — W03-C09 Context Lock

```text
context_lock_status = LOCKED
checkpoint = W03-C09
task = W03-C09-I/H/R
contract_version = W03-C09-A-v1.1
base_contract = W03-C09-A-v1
clarification = W03-C09-CONTRACT-CLARIFICATION-01
entry_branch = feat/w03-ai-decision-loop
entry_sha = d71d5baeb0862f2706358c26e182554b3807e8f6
main_sha = 9d18ddde9fe933952a2661ee1419f13c8577605d
pr = 6 / OPEN / DRAFT / NOT MERGED / AUTO-MERGE ABSENT
entry_ci = Run #77 / 37212002075 / SUCCESS
entry_class = P / PUBLICATION_EXACT_SHA
human_authorization = W03-C09 HUMAN AUTHORIZATION: APPROVED
clarification_approval = W03-C09 CONTRACT CLARIFICATION-01: APPROVED
```

## 1. Mandatory read-only entry preflight

Before writing any repository file, Codex must fetch and prove:

```text
current branch = feat/w03-ai-decision-loop
local HEAD = d71d5baeb0862f2706358c26e182554b3807e8f6
tracking HEAD = d71d5baeb0862f2706358c26e182554b3807e8f6
direct remote HEAD = d71d5baeb0862f2706358c26e182554b3807e8f6
PR #6 HEAD = d71d5baeb0862f2706358c26e182554b3807e8f6
worktree = CLEAN
ahead/behind = 0/0
main = 9d18ddde9fe933952a2661ee1419f13c8577605d
PR #6 = OPEN / DRAFT / NOT MERGED / AUTO-MERGE ABSENT
Run #77 / 37212002075 = SUCCESS on the entry SHA
```

If any value differs, stop. Do not reset, rebase, amend, cherry-pick, merge,
force-push, or silently adapt the contract.

## 2. Frozen repository material identities at GPT review

Git blob SHAs observed on `feat/w03-ai-decision-loop@d71d5...`:

| Material | Git blob SHA |
|---|---|
| `docs/sprints/W03_ai_decision_loop.md` | `380f85c8b4da729c12e016651f744bac626a125d` |
| `docs/w03/AI_LOOP_CONSTITUTION.md` | `83bdae9c6511237397811b604d9562420ec40c0f` |
| `docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md` | `e45ed2ebb7df97ddae4ead18097df8f9e9f8de07` |
| `docs/w03/SEMANTIC_TRUST_CONTRACT.md` | `e120f4a8cd2f37e0f6084b86e6e606958c6ba68b` |
| `docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md` | `b49e749e8159214fb6624a2a5e2b904ef096fcd8` |
| `docs/w03/LOOP_EXECUTION_STATE_MACHINE.md` | `b82df602bb8cff414647e6ea5f61390031c31e63` |
| `docs/w03/FAILURE_AND_DEGRADATION_POLICY.md` | `b57c867197d000271286cb81f8230de003779bd7` |
| `.github/workflows/ci.yml` | `19a9cd575f000ed7ddf7681b1ccc05578316de3a` |
| `scripts/ci/classify_change.py` | `353df45732e77831a3ad92bf6f9a072db7ce3425` |
| `scripts/ci/verify_publication.py` | `8f97a117f936d9dce91957f7b44551acb5d5c2b6` |
| `docs/w03/reports/W03_C08_C1_FINAL_CLOSEOUT.md` | `622bdeb58e9451276cb70a15ad7ffa9c68d2ecdc` |
| `docs/w03/reports/W03_C08_GPT_INDEPENDENT_REREVIEW_R2.md` | `a975c8f9e8dccd248bb685a7fb009e623c13cc2d` |
| `docs/CURRENT_STATE.md` | `d07ad2a897a7b5f16d256ff80356356cfc97e78a` |
| `AGENTS.md` | `2e8e20f4cccbb85e327ca561005a9bff4e631a5f` |
| `LOOP.md` | `7276d50e499bc48b67c5619aaa26f09c46bb7b7e` |
| `docs/context/CONTEXT_INDEX.md` | `ec6ac233ed5b39ce777b3cf605475e9e41ebc725` |
| `docs/context/MATERIAL_REGISTRY.md` | `01f22882e0fc328e9e2af7327c4a7c8bc2160bf6` |

C08 frozen runtime prompt remains:

```text
prompt_version = w03-c08-runtime-prompt-v1
prompt_sha256 = 426b061d79d2a8dfa4ac2959a604e77e6ef8dbcc04759bf7860ec9f012d185fc
context_schema = w03-c08-context-v1
output_schema = w03-c08-output-v1
provider = OpenAI
requested_model = gpt-5.6-terra
openai_sdk = 2.54.0
max_provider_calls = 2
sdk_automatic_retries = 0
```

C09 must not change any of those runtime values.

## 3. Authorized implementation paths

The canonical list is supplied in `specs/authorized_paths.json`.

Implementation-phase mutable paths are limited to:

```text
.github/workflows/ci.yml
scripts/ci/run_w03_ai_loop_gate.py
tests/test_c09_ci_gate.py
docs/w03/checkpoints/c09/**
docs/sprints/W03_ai_decision_loop.md
```

Post-exact-SHA report publication paths are limited to:

```text
docs/w03/reports/W03_C09_R_DEVELOPMENT_ROUND_REPORT.md
docs/CURRENT_STATE.md
```

No implementation source under `src/` is authorized.

## 4. Frozen expected delta

C09 may:

```text
publish the C09 checkpoint contract package
add the clarified frozen semantic gate manifest (38 selectors / 85 expanded cases)
add one development-plane semantic gate runner
add one C09 CI-contract test module
add one named W03 AI loop gate GitHub Actions job
wire that job into the existing Verification gate
normalize the W03 Sprint current-status surface to the authorized C09 state
publish the C09 Round Report and CURRENT_STATE only after exact implementation proof
```

C09 may not:

```text
change runtime semantics
change existing checkpoint contract meaning
change test expectations to make a failure pass
skip/xfail/delete accepted critical tests
change classifier P/C/I/F semantics
weaken Publication proof
weaken Quality or Compose
change GitHub trigger scope
add dependencies/actions/images
make live model calls
read secrets
change operational data
start C10
```

## 5. Entry lock transition

After Product Owner approval and successful preflight, Codex shall publish this
file with:

```text
context_lock_status = LOCKED
human_authorization = W03-C09 HUMAN AUTHORIZATION: APPROVED
clarification_approval = W03-C09 CONTRACT CLARIFICATION-01: APPROVED
```

before the first CI/script/test implementation write.

## 6. Observed Codex entry evidence

Both exact Product Owner approval lines were supplied in the active request.
Read-only preflight observed the required branch, local/tracking/direct-remote/PR
heads, main, clean staging/worktree, 0/0 synchronization, and successful Run #77.
PR #6 is open/draft/unmerged; the authenticated GitHub merge panel reports
`Draft pull requests cannot be merged` with the merge action disabled and no
enabled auto-merge notice. C08 closure is effective after its successful
publication gate; that historical closeout did not authorize C09.

Collection: 38 exact function selectors / 85 expanded cases, all per-selector
and family counts match. All 16 package SHA-256 entries and all 17 published
entry Git blob identities match. No runtime evidence or dataset is added.
Dataset/scenario/tool-registry versions and accepted C01-C08 controls are inherited.
Development sources: approved V1.1 package, frozen repository controls, existing
tests and Git/CI evidence. Forbidden sources: live provider secrets/calls,
operational datasets outside guarded test fixtures, runtime HGT.

Additional immutable Git identities:

| Material | Entry Git identity |
|---|---|
| `docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md` | `aa6f87be102c5bc6b5ebb17384ec7aefeab1b697` |
| `src` | `cb53e0a3f008c1000e00ff0340e8b197cc878b35` |
| `migrations` | `c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433` |
| `pyproject.toml` | `318bbc0a858f760e6c4d7a2d3fdbfcc111febb77` |
| `uv.lock` | `619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a` |
| `docker-compose.yml` | `5a0b6e8486edc69f9f79c7e1345a842aa412983c` |
| `apps` | `597399c7919982e9b2d54fc8b58fe6784cfe8585` |

Package manifest SHA-256: `bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990`.
Local Docker daemon unavailable at entry; F09 remains mandatory in remote CI.
