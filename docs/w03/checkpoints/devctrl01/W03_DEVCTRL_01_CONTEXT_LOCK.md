# W03-DEVCTRL-01 Context Lock

**Task:** W03-DEVCTRL-01-I/H/R

**Plane:** development control only

**Authorization:** `W03-DEVCTRL-01 HUMAN AUTHORIZATION: APPROVED` in Product Owner chat

**Pre-implementation status:** `context_lock_status = LOCKED`

## Baseline and input integrity

| Item | Locked value |
|---|---|
| Branch | `feat/w03-ai-decision-loop` |
| Local, tracking, direct remote and PR #6 head | `28173582661bc4bba5f254928ab8a9bbb5de63a0` |
| Local, tracking and direct remote main | `9d18ddde9fe933952a2661ee1419f13c8577605d` |
| Working tree before contract publication | Clean; 0 ahead / 0 behind; no Git operation in progress |
| PR #6 | Open, draft, unmerged; merge disabled in draft UI; no auto-merge enabled state shown |
| C02 final CI | Run #45 / `36022615573` / success on the locked W03 head |
| Master SHA-256 | `1fbcd9371f92015dabb5f000e35b9f32f7c69a49df4dc5dfc2ca3203f9d85bc8` |
| Authorization ZIP SHA-256 | `61ca4fecab0112531fc4bfc059ba0cb3945bca1118b0226b199eb3405aa9611e` |
| Separate Execution Prompt SHA-256 | `0c27f98189582ea86c27a6b6f4328ff12464a12cd41e90c8f1cfaeab792c7d82` |

All 16 payloads listed by the ZIP manifest matched their declared SHA-256 hashes.
The Master contains every ZIP document. The separate Execution Prompt is byte for
byte identical to the ZIP copy. The ZIP's `PACKAGE_MANIFEST.md` is self-describing
and has no self-hash entry. The nine `repo_docs` files were published in this
checkpoint directory; only the Human Authorization template was then updated to
record the Product Owner's actual approval.

## Frozen file hashes before implementation

SHA-256 values are over repository file bytes, after contract publication and
before the CI implementation edit.

| File | SHA-256 |
|---|---|
| `.github/workflows/ci.yml` | `47dab64346830927a0215e8d6e590abfead5c12ed7d775b407e6eff974658401` |
| `AGENTS.md` | `ceb3c166e2d4d2782688d668121bfb1de6ec69bd9d3513cb4d63bc4d9f165c76` |
| `LOOP.md` | `1850365277f65bbba1637381c37474a853e07b1c1510b6ce30293395cd949e99` |
| `docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md` | `74dcc0552595c3c0d368fa527c1b85b34f299ba943bdf16b75407c0a71e1a82a` |
| `docs/CURRENT_STATE.md` | `2fe295be2ef0ce22b367cda768fcc975917bbbe585ead22321ca2647186cc609` |
| `docs/sprints/W03_ai_decision_loop.md` | `aed067e6532effe434ab0338fdc2ec9a8455dca761385f78bcce51298617410a` |
| `W03_DEVCTRL_01_AUTHORIZATION_CONTRACT.md` | `6e968ba528fcaafa78c0eb96cb9c2ef495342b272e5df8619b63f4aed06fbe8a` |
| `W03_DEVCTRL_01_C03_TRANSITION_NOTICE.md` | `427feb973772ae030095f3c11ce57184836ebf4b7b87c45b816cbb67731eaa34` |
| `W03_DEVCTRL_01_CHANGE_CLASS_CONTRACT.md` | `12c6b9aee299fe1ba0f3c18e7cde235169cb675818d95bfb7e8e144f578ab1a4` |
| `W03_DEVCTRL_01_CI_ARCHITECTURE_CONTRACT.md` | `449c3e52bf8a358cc17230dc78200f00d6b2f6828e68634b457788eecf13c28c` |
| `W03_DEVCTRL_01_GPT_REVIEW_CHECKLIST.md` | `47effbba8b7b8f3f4d883a6fc5892193a45240b630a3f9fdabf5b8480d83c090` |
| `W03_DEVCTRL_01_HARNESS_ACCEPTANCE_SPEC.md` | `04c853ddaf82dac224a08f125946b85b05109509a7062d045cb797935621cb78` |
| `W03_DEVCTRL_01_HISTORICAL_REPLAY_MATRIX.md` | `6b26370054ab051dd7d98e162f31ef3cf512cc0bcff282ac9d5a09e58dc94aff` |
| `W03_DEVCTRL_01_HUMAN_AUTHORIZATION.md` | `7488fa25646d55f417cd6c7abc78a2710afe5eb72d60378192790936a55cad74` |
| `W03_DEVCTRL_01_NEGATIVE_CLASSIFIER_TEST_MATRIX.md` | `36c2f943281abb16ed9b8d413b03ee40ea1f620f0308b164098b66b788fb67a6` |

The checkpoint file names in the second half of this table are relative to this
directory. This Context Lock is excluded from its own hash list.

## Frozen runtime and foundation evidence

| Path | Baseline evidence |
|---|---|
| `src/` Git tree | `07b2c6c47fce38cd1ada2e924afbc60ece944ab6` |
| `migrations/` Git tree | `c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433` |
| `pyproject.toml` SHA-256 | `4bfc06642202359ea80ef957453f58a89e0ebbb9b864d7d83c3a1917e67f93ad` |
| `uv.lock` SHA-256 | `634bfcb426bd0028a775951fc6cb8643ee16944f3f7c88f709a61b4af70ee8be` |
| `docker-compose.yml` SHA-256 | `45b361923ded25ea8c02ba8f574eed3d925c50ba28d73018d25f1f4397e8666c` |
| `apps/api/Dockerfile` SHA-256 | `dad613115e1bff701369616c9f8c32bdab84cf5a5cba478e08bf981024acbada` |
| `apps/worker/Dockerfile` SHA-256 | `6055fbe63f2eb3c3dacd9a4356c31fefedb1f8840a58bf1ca3572e5f6ed2afc3` |

Runtime dataset version/hash, scenario configuration, prompt version and tool
registry are inherited unchanged from the closed C02 baseline. This task builds
no runtime DecisionContext, opens no runtime HGT, and changes no runtime tool.

## Authorized delta

Implementation commit may modify only `.github/workflows/ci.yml` and
`docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md`, and add
`scripts/ci/classify_change.py`, `scripts/ci/verify_publication.py`,
`tests/test_ci_change_classifier.py`, `tests/test_ci_publication_gate.py`,
`tests/fixtures/w03_ci_history.json`, and this checkpoint's control documents.
The later report commit may add only
`docs/w03/reports/W03_DEVCTRL_01_R_DEVELOPMENT_ROUND_REPORT.md` and update
`docs/CURRENT_STATE.md`.

All paths forbidden by the Authorization Contract remain frozen, including
runtime source, W1/W2 baselines, schema, dependencies, Docker/Compose, Sprint
semantics, AGENTS.md, LOOP.md, and skills/. C03 implementation is unauthorized.

Expected context delta:

```text
runtime semantics: NONE
runtime tools: NONE
CI proof scheduling: UPDATED
change classifier: NEW
publication proof: NEW
full gate: PRESERVED
C03: NOT IMPLEMENTED
context_lock_status = LOCKED
```
