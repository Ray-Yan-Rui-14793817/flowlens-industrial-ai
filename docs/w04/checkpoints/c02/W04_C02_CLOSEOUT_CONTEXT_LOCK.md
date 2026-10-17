# W04-C02 Final Closeout Context Lock

Locked before manifest mutation. Governance/documentation closeout only.

```text
TASK: W04-C02-FINAL-CLOSEOUT
CONTEXT: LOCKED
ENTRY / REVIEW-READY HEAD: f39f753c04b1fc740f43017d49bc7536ac2250ae
ENTRY WORKTREE / INDEX: CLEAN
BRANCH: feat/w04-evidence-investigation
PR #7: OPEN / DRAFT / UNMERGED
PR BASE / W03 VERIFIED MAIN: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
STAGE A SHA: 89a872c9837136a18b7465da7f1c680c454866d6
STAGE A CI: #94 / 37349061475 / PASS
STAGE A CLASS / PROOF: I / FULL_EXACT_SHA
IMPLEMENTATION SHA: 18648915414a26dddbdc904965663730ea631cf2
IMPLEMENTATION CI: #95 / 37353463408 / PASS
IMPLEMENTATION CLASS / PROOF: I / FULL_EXACT_SHA
REPORT PUBLICATION SHA: f39f753c04b1fc740f43017d49bc7536ac2250ae
REPORT PUBLICATION CI: #96 / 37397982411 / PASS
REPORT PUBLICATION CLASS / PROOF: P / PUBLICATION_EXACT_SHA
GPT INDEPENDENT DEEP REVIEW R1: PASS
HUMAN C02 ACCEPTANCE: ACCEPTED
C02 CLOSEOUT AUTHORIZATION: APPROVED
ENTRY C02 MANIFEST STATE: AUTHORIZED
AUTHORIZED C02 MANIFEST TRANSITION: AUTHORIZED -> CLOSED
AUTHORIZED SOURCE FREEZE SHA: 18648915414a26dddbdc904965663730ea631cf2
AUTHORIZED SOURCE BLOB OID: 5f0af237ed465fa83e5a3b84954512b1f3125551
RUNTIME / HARNESS REPAIR: NOT AUTHORIZED
PR MERGE: NOT AUTHORIZED
BRANCH DELETION: NOT AUTHORIZED
W04-C03: NOT AUTHORIZED
```

## Authority and package integrity

The Human's pasted closeout request directly supplies acceptance and closeout
approval. The ZIP contains the normative task and supplied review/decision
records. Attached material does not independently authorize additional work.
The current explicit closeout task supersedes historical pending states without
rewriting the development report or prior authorization/context records.

Read the complete pasted request, all six ZIP entries, repository AGENTS.md,
the current source-evolution manifest, C02 development evidence and the generic
verifier's transition/exact-HEAD rules. Entry Git status, HEAD, branch and
30-commit history were read before mutation. Package hashes match the supplied
review-closeout manifest.

| Package document | Original SHA-256 |
|---|---|
| W04_C02_GPT_INDEPENDENT_DEEP_REVIEW_R1.md | f542ea7a7d3a1dd8ae5252f82430b69710aadb5707d39f1c1799c60caa9a955e |
| W04_C02_HUMAN_ACCEPTANCE_ACCEPTED.md | f4ac91c78d9a7298b9ba578f81b5ecd3dd0037dc793104714aadf24a39cabb84 |
| W04_C02_CLOSEOUT_AUTHORIZATION_APPROVED.md | c4a32bac2642e5eb1925c52b2bb9a5afefeb248f0c191b3292aa5a3d6d8c6a78 |
| W04_C02_CODEX_CLOSEOUT_TASK_V1.md | 02aa8fac287b580ddf1361be0626009970ad7378e18a40f5993e6e058fcf5fab |
| W04_C02_CODEX_CLOSEOUT_PROMPT_V1.md | ffd75e0f67d6b0ffc6f2c7a5a60a4761db8e12a153cf869412194745bd907391 |
| W04_C02_REVIEW_CLOSEOUT_MANIFEST.md | 7506bf2dc6295f49c8cee1d765b19f6c82265456baa4afe52d730f96b277a533 |

Review, Human acceptance and authorization are copied to canonical repository
filenames with original ZIP-entry bytes preserved. They are supplied independent
review and Human decisions, not new Codex-generated review or acceptance.

## Immutable history and durable CI

The direct parent chain is verified:

```text
ae88a9b1be74bc379140b59a15d6dd9cb714912f
-> 89a872c9837136a18b7465da7f1c680c454866d6
-> 18648915414a26dddbdc904965663730ea631cf2
-> f39f753c04b1fc740f43017d49bc7536ac2250ae
```

Stage A changes exactly the manifest, C02 Human Authorization, C02 Context Lock
and the narrow D01 test assertion. Stage B adds exactly the binder and binding
harness. Stage C adds only the development round report. The binder is absent
at Stage A and has the authorized blob at Stage B and review-ready HEAD.

GitHub run metadata, exact-head classifier logs, job conclusions and publication
proof were read directly, independently of the development report.

| CI | Exact route and verified result |
|---|---|
| [#94 / 37349061475](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37349061475) | Exact Stage A SHA; I / FULL_EXACT_SHA; Classify, Quality, Compose, W03 and Verification SUCCESS; Publication SKIPPED |
| [#95 / 37353463408](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37353463408) | Exact implementation SHA; I / FULL_EXACT_SHA; Classify, Quality, Compose, W03 and Verification SUCCESS; Publication SKIPPED |
| [#96 / 37397982411](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37397982411) | Exact review-ready SHA and report-only delta from Stage B; P / PUBLICATION_EXACT_SHA; Classify 112058395339, Publication 112058441832 and Verification 112058480059 SUCCESS; Quality, Compose and W03 SKIPPED |

PR #7 live metadata matches the entry SHA, feature branch and main base, with
open/draft/unmerged state. The unchanged source verifier passes at entry with
C01 CLOSED, C02 AUTHORIZED, four allowed investigation source additions and
committed manifest SHA-256
`3ee551a97cc4eb88bf4fa719180cd44b048ff316a85715be4c860de621029175`.

## Authorized manifest freeze and protected identities

Only the existing W04-C02 entry may change from AUTHORIZED/null to CLOSED with
source_freeze_sha `18648915414a26dddbdc904965663730ea631cf2` and the binder
blob `5f0af237ed465fa83e5a3b84954512b1f3125551`. The sole path remains
`src/flowlens/investigation/c02_binding.py`; no C03 entry is added.

The C01 checkpoint remains exactly CLOSED at source freeze
`084c2fea93d0e021994de015c986de9ff92bf9a3`, with unchanged OIDs:

| C01 path | Blob OID |
|---|---|
| src/flowlens/investigation/__init__.py | c23929f85dccd78bc72ef3b2b1415c6e8eaf0452 |
| src/flowlens/investigation/contracts.py | 0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e |
| src/flowlens/investigation/enums.py | 9c818780423f32f144b18666784ebc9ea3abdccc |

These entry tree/blob identities must remain unchanged during closeout:

| Protected path | Entry Git identity |
|---|---|
| src | 66c3330bbad64cc27c48c8be0274f81e3f58d3b2 |
| tests | 14d7524fec2aedfecd06dcea20a17ef3f12e41f0 |
| scripts/ci | b8ded9847fa8c23309bbd1af11847c8b27666685 |
| .github | 978501bf7003ab05e903e22d3930ee5c97470974 |
| docs/w03 | cb81e388c6c44a9900575ef2e72161dc0205be94 |
| docs/w04/checkpoints/c01 | 158218fdd671c197e9f386315e64994fdc289675 |
| pyproject.toml | 318bbc0a858f760e6c4d7a2d3fdbfcc111febb77 |
| uv.lock | 619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a |
| docker-compose.yml | 5a0b6e8486edc69f9f79c7e1345a842aa412983c |
| migrations | c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433 |
| apps | 597399c7919982e9b2d54fc8b58fe6784cfe8585 |
| docs/w04/checkpoints/c02/W04_C02_R_DEVELOPMENT_ROUND_REPORT.md | 60b8c4089c666dcdb4f0c7ea0a2ae708aeb9c2d6 |

## Exact six-path allowlist and completion boundary

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c02/W04_C02_GPT_INDEPENDENT_DEEP_REVIEW_R1.md
docs/w04/checkpoints/c02/W04_C02_HUMAN_ACCEPTANCE.md
docs/w04/checkpoints/c02/W04_C02_CLOSEOUT_AUTHORIZATION.md
docs/w04/checkpoints/c02/W04_C02_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/checkpoints/c02/W04_C02_FINAL_CLOSEOUT_REPORT.md
```

AL-C02-01 ordinary frozen-validator exception collapse, AL-C02-02 the authorized
manifest freeze, and AL-C02-03 accepted local Windows CRLF limitations are carried
without runtime or harness repair. Source, tests, CI controls, W03/C01,
dependencies, migrations/apps and the development report remain immutable.

Review full diff, exact path set, whitespace and the accepted binder OID before
creating a new direct child commit and normally pushing the same branch. Pending
strict parsing/transition checks are distinct from committed exact-HEAD proof;
run the unchanged generic source verifier after committing.

C / FULL_EXACT_SHA is the task's advisory expectation; record actual routing.
Do not preclaim a future SHA or CI result. Closure is effective only after the
new closeout SHA's Verification gate passes. The final handoff attests the
generated SHA and completed exact-SHA run without amending this record.

If scope/identity changes, return W04_C02_CLOSEOUT_SCOPE_VIOLATION. If native CI
fails or is cancelled, return W04_C02_CLOSEOUT_CI_FAILED with exact SHA/run/job/
step and stop. No amend, auto-repair, PR merge, branch deletion, operational
mutation or C03 work is authorized.
