# W04-C04 Closeout Authorization

Recorded on 2026-10-07 from the Human's current final-closeout request and
`W04_C04_CLOSEOUT_TASK_V1.md` in the supplied final-closeout handoff package.

```text
PROJECT: FlowLens Industrial AI
TASK: W04-C04-FINAL-CLOSEOUT
CHECKPOINT: W04-C04 — Authorized Evidence Navigation
GPT INDEPENDENT IMPLEMENTATION REVIEW R1: PASS
HUMAN C04 ACCEPTANCE: ACCEPTED
C04 CLOSEOUT AUTHORIZATION: APPROVED
DECISION: APPROVED
C04 CLOSEOUT: AUTHORIZED TO EXECUTE
AUTHORIZED MANIFEST TRANSITION: W04-C04 AUTHORIZED -> CLOSED
AUTHORIZED SOURCE FREEZE SHA: 6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1
EXECUTION BASELINE / STAGE D: cc7b378ee105a6adf4b155d2ebc83f846b116ad3
BRANCH: feat/w04-evidence-investigation
PR #7: OPEN / DRAFT / UNMERGED
W04-C05: NOT AUTHORIZED
```

The Human's conditional instruction to proceed when GPT finds C04 complete is
satisfied by supplied GPT Review R1 PASS. The current request explicitly supplies
acceptance and closeout authorization for this exact scope. No additional Human
decision is needed to execute these six paths.

## Authorized manifest delta

Only C04 changes: state becomes CLOSED, `source_freeze_sha` becomes the accepted
Stage C SHA, and its three existing source entries receive these exact OIDs:

| Existing source path | Frozen Git blob OID |
|---|---|
| `src/flowlens/investigation/c04_navigation.py` | `98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4` |
| `src/flowlens/investigation/c04_queries.py` | `dc22c7e532a4b62ccfffec2210bc2a6306d97234` |
| `src/flowlens/investigation/c04_registry.py` | `fbe6f0603d7b0634426ac0034033089eb55af4d7` |

C01/C02/C03 entries, manifest schema/policy/W03 baseline/root, source paths and
ordering remain frozen. No C05 entry is authorized.

## Exact six-path closeout allowlist

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c04/W04_C04_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md
docs/w04/checkpoints/c04/W04_C04_HUMAN_ACCEPTANCE.md
docs/w04/checkpoints/c04/W04_C04_CLOSEOUT_AUTHORIZATION.md
docs/w04/checkpoints/c04/W04_C04_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/checkpoints/c04/W04_C04_FINAL_CLOSEOUT_REPORT.md
```

No seventh tracked path. No source, test/harness, production verifier/classifier/
workflow, dependency, migration, C01/C02/C03/W03 or operational change is
authorized. Existing C04 context lock, implementation Human authorization and
development round report remain frozen.

The authorized publication is one new direct child of Stage D, with message
`docs(w04-c04): close authorized evidence navigation`, followed by normal push
to `feat/w04-evidence-investigation`. No amend, history rewrite, force push,
merge or branch deletion is authorized. PR #7 remains OPEN/DRAFT/UNMERGED.

Run the frozen CLOSED lifecycle/source gates. The accepted C03 disposable
committed-copy proof method preserves the verifier's committed-HEAD invariant;
repeat actual HEAD proof after the real commit and before normal push. Native
classification controls the route. Effective closure requires the new closeout
SHA's own exact-SHA Verification PASS, with Classify, Quality, Compose and W03
PASS and Publication SKIPPED on the full route.

If the intended CLOSED state fails a frozen gate, STOP
`W04_C04_CLOSEOUT_REQUIRES_GPT_CLARIFICATION`. If closeout CI fails or cancels,
STOP `W04_C04_CLOSEOUT_CI_FAILED` with exact SHA/run/class/job/step/evidence.
Do not repair tests, runtime or production controls, amend, or begin C05.
