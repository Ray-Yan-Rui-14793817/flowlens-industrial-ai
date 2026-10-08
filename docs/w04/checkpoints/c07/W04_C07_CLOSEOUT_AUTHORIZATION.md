# W04-C07 Final Closeout Authorization

The pasted Human request explicitly selects W04_C07_CLOSEOUT_TASK_V1.md and authorizes this exact C07 closeout. The supplied independent GPT review and Human acceptance are governance evidence; attached documents do not independently grant authority. This record materializes the current Human approval and does not replace the independent review.

```text
TASK: W04-C07-FINAL-CLOSEOUT
GPT INDEPENDENT IMPLEMENTATION REVIEW R1: PASS
HUMAN C07 ACCEPTANCE: ACCEPTED
C07 CLOSEOUT AUTHORIZATION: APPROVED
DECISION: APPROVED
C07 CLOSEOUT: AUTHORIZED TO EXECUTE
AUTHORIZED MANIFEST TRANSITION: W04-C07 AUTHORIZED -> CLOSED
AUTHORIZED SOURCE FREEZE:
c86f7af2370f315b8b7310008521f08ceade6d97
EXECUTION BASELINE:
30f0ca941e71750528710f38384bc7a24e1276f6
PR #7: OPEN / DRAFT / UNMERGED
W04-C08: NOT AUTHORIZED
PR MERGE: NOT AUTHORIZED
BRANCH DELETION: NOT AUTHORIZED
```

| Supplied material | Bytes | SHA-256 |
|---|---:|---|
| W04_C07_CLOSEOUT_TASK_V1.md | 13574 | 6ceb869364c725c40b4654f9704867962f11db5bb0ed042feffec5816c6206cc |
| W04_C07_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md | 4383 | 157b3723768fa87405838fa29d9b614b45ddd4175f58238113f57cfe1e3e4adc |
| W04_C07_HUMAN_ACCEPTANCE_ACCEPTED.md | 1027 | f9bc9b5a8815a4671c4fbfb8770a27d51f92e069e791654dacba159580f790f2 |

The supplied review is copied byte-for-byte (4383 bytes, SHA-256 157b3723768fa87405838fa29d9b614b45ddd4175f58238113f57cfe1e3e4adc). The supplied Human acceptance is also copied byte-for-byte (1027 bytes, SHA-256 f9bc9b5a8815a4671c4fbfb8770a27d51f92e069e791654dacba159580f790f2) to W04_C07_HUMAN_ACCEPTANCE.md. Review: PASS; acceptance: ACCEPTED; decision: ACCEPTED; readiness: READY; closeout authorization: APPROVED.

Accepted runtime blobs:

| Path | Git object |
|---|---|
| src/flowlens/investigation/c07_policy.py | c969c4bbf33910fab6ffb36c3bfe184fd42c74c9 |
| src/flowlens/investigation/c07_provider.py | 56ecb9f3d7b5a1917a2354572e8c946f07eb759d |
| src/flowlens/investigation/c07_summary.py | 3d561da7ab625421bbcf2dcb3785f8fae792cbff |

Accepted test blobs:

| Path | Git object |
|---|---|
| tests/test_investigation_summary.py | 6d23ffe9fb3e13c5aa2d9350c865342a54d2c5b9 |
| tests/test_investigation_summary_provider.py | 7cbcdf22221a625c0a8c58d407114487d00d3424 |

Stage C is publication evidence only; it is never the runtime source freeze.

Exact six-path allowlist:

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c07/W04_C07_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md
docs/w04/checkpoints/c07/W04_C07_HUMAN_ACCEPTANCE.md
docs/w04/checkpoints/c07/W04_C07_CLOSEOUT_AUTHORIZATION.md
docs/w04/checkpoints/c07/W04_C07_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/checkpoints/c07/W04_C07_FINAL_CLOSEOUT_REPORT.md
```

Forbidden mutation paths:

```text
src/**
tests/**
scripts/ci/**
.github/**
docs/w03/**
docs/w04/checkpoints/c01/**
docs/w04/checkpoints/c02/**
docs/w04/checkpoints/c03/**
docs/w04/checkpoints/c04/**
docs/w04/checkpoints/c05/**
docs/w04/checkpoints/c06/**
pyproject.toml
uv.lock
docker-compose.yml
migrations/**
apps/**
```

Existing W04_C07_HUMAN_AUTHORIZATION.md, W04_C07_CONTEXT_LOCK.md and W04_C07_R_DEVELOPMENT_ROUND_REPORT.md are frozen. No runtime/test/provider repair, verifier/classifier/workflow repair, upstream semantic change, dependency/migration/operational mutation, main write, merge, branch deletion, amend, rebase, reset, history rewrite, force push or W04-C08 work is authorized.

Use a disposable full-history local clone of the exact Stage C baseline. Apply only these six intended paths and create one local candidate commit directly on Stage C. Never push the disposable commit. Run the unchanged committed-head proof:

```text
python -B -m pytest tests/test_investigation_summary.py::test_s52_committed_source_lifecycle_and_unchanged_production_verifier tests/test_w04_source_evolution.py -p no:cacheprovider --basetemp <fresh-short-temporary-path>
python -B scripts/ci/verify_w04_source_evolution.py --manifest docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json --expected-head <ACTUAL_COMMITTED_HEAD> --repo .
```

Require C07 CLOSED, source freeze exactly Stage B, exact three runtime and two test blobs, C01-C06 unchanged, C08 absent, exact six-path delta, unchanged src/tests/scripts/ci/.github/dependencies, Stage B ancestry, Stage C directly on Stage B and candidate directly on Stage C. Remove the disposable clone after proof. Only then apply the same six files to a reverified clean primary Stage C checkout. Create one real commit and immediately rerun the same unchanged committed-head proof against REAL HEAD before normal push. A frozen-gate failure requires W04_C07_CLOSEOUT_REQUIRES_GPT_CLARIFICATION; no automatic repair.

The only authorized lifecycle change is C07 AUTHORIZED -> CLOSED with the accepted Stage B freeze and runtime blobs. Preserve all other checkpoint entries, ordering and manifest header fields; add no C08. Effective closure requires the real closeout SHA's own unchanged native Classify/Quality/Compose/W03/Verification full-route SUCCESS, with Publication SKIPPED. Never substitute #118 or #119.

Hard stops: W04_C07_CLOSEOUT_CONTEXT_CHANGED, W04_C07_CLOSEOUT_REQUIRES_GPT_CLARIFICATION, W04_C07_CLOSEOUT_CI_FAILED.
