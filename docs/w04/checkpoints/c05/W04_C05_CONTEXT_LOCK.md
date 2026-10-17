# W04-C05 implementation context lock

Locked before implementation on 2026-10-07 (Asia/Shanghai).
The current Human request explicitly authorizes the supplied Task V1 and frozen
Design Master V1 after GPT Deep Design Review R1 PASS. It is the current task
contract under the repository authority hierarchy. Historical W03 router/state
text does not override this exact W04 authorization. W1/W2/W03 invariants remain
frozen. Development authorization and fixtures never become runtime evidence.

## Entry evidence

- HEAD/local tracking/direct remote/PR #7 head: `783234ac0ca1ba5c2b33d46f8576a12c2184114c`.
- Entry tree: `5a2589b1622a6e336aeaf75aca722a91e4438883`.
- Branch: `feat/w04-evidence-investigation`; worktree/staging clean before writes.
- PR #7: OPEN / DRAFT / UNMERGED; base main `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`.
- Native CI #107 / 37573283883: SUCCESS; refreshed via GitHub connector.
- Classify log: C / FULL_EXACT_SHA; exact source checkout and source delta confirmed.
- Classify, Quality, Docker Compose, W03 AI loop, Verification PASS; Publication SKIPPED.
- Manifest C01/C02/C03/C04 CLOSED, DEVCTRL CLOSED; C05 absent; C06 not authorized.

## Handoff materials

The ZIP is read directly without adding extracted package files to the repository.
Task/design/review are used only because the current Human request explicitly
selects them. Supplied approval is copied byte-for-byte into the authorized C05
Human authorization path.

| Material | Bytes | SHA-256 |
|---|---:|---|
| `W04_C05_CODEX_PROMPT_V1.md` | 17053 | `f538007accfbb93da47619b6a14f4492f86465a2ce9238069c201aa655997822` |
| `W04_C05_CODEX_TASK_V1.md` | 12691 | `cd9d80ecfb870d76147159d2405293b80dad0b00af4c0af7cccf10d5316d79a6` |
| `W04_C05_GPT_DEEP_REVIEW_R1.md` | 3962 | `7c398c80a908f43eed1f4225b7252238f9d20de9f658e8691553ad1cfce9bc1f` |
| `W04_C05_GPT_DESIGN_MASTER_V1.md` | 24453 | `407cd253dac26d74881c331de529b1c0e3a4cfdb0daf824df75786990e93bc81` |
| `W04_C05_HUMAN_AUTHORIZATION_APPROVED.md` | 1320 | `d4ef8b5ac348d40b2a5be0cc7f756c0060edbb92ef087c00df3102071324281f` |
| `W04_C05_PACKAGE_MANIFEST.md` | 937 | `5857f1509a017b4d63a8778230333411a6370e2f7316e0ed96b27646b1e6b127` |

## Exact entry Git blobs

| Path | Git blob |
|---|---|
| `AGENTS.md` | `173a9a8c3f3ac3e2c964f52fd8a7551bc48d5241` |
| `LOOP.md` | `7276d50e499bc48b67c5619aaa26f09c46bb7b7e` |
| `docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json` | `7099baf9fbac81df3c50cfd9148e1fe60896b360` |
| `src/flowlens/investigation/__init__.py` | `c23929f85dccd78bc72ef3b2b1415c6e8eaf0452` |
| `src/flowlens/investigation/contracts.py` | `0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e` |
| `src/flowlens/investigation/enums.py` | `9c818780423f32f144b18666784ebc9ea3abdccc` |
| `src/flowlens/investigation/c02_binding.py` | `5f0af237ed465fa83e5a3b84954512b1f3125551` |
| `src/flowlens/investigation/c03_planning.py` | `21d0055e12d86e6333a836d363d6e266cb0fcbd7` |
| `src/flowlens/investigation/c04_registry.py` | `fbe6f0603d7b0634426ac0034033089eb55af4d7` |
| `src/flowlens/investigation/c04_queries.py` | `dc22c7e532a4b62ccfffec2210bc2a6306d97234` |
| `src/flowlens/investigation/c04_navigation.py` | `98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4` |
| `src/flowlens/decision/contracts.py` | `44a742b7420a1c1e595b4dbeedd0249c9417e545` |
| `src/flowlens/decision/enums.py` | `ed6facf95de4d05ef6c917f4122162c10c23a68c` |
| `src/flowlens/decision/primitives.py` | `cbfdf81b4305f805ee865664d1652fd6d3bc8b4d` |
| `src/flowlens/decision/serialization.py` | `306742a2e6cd546288c20fdc82d15d075168235e` |
| `src/flowlens/decision/signals.py` | `60c29030c5e54d036d8e5ecb50a6f44d5e9cf1a3` |
| `src/flowlens/decision/c03_policy.py` | `cda8d73e32afaaf201c2c4532b76b9f2636b9757` |
| `src/flowlens/decision/c03_validation.py` | `aa3db33fc808a0ef251a2265e2b866c2534da5bd` |
| `src/flowlens/decision/c06_validation.py` | `9fabdf1ed67a02b768db9ecfaf4e84f5ddd67bb4` |
| `src/flowlens/decision/temporal.py` | `70ae018f4b50ac6ed45e894d6726e9ccee345c8a` |
| `src/flowlens/decision/trust.py` | `f216d22f1d6862e1eef886dfbe4c3af16f396ec1` |
| `docs/w03/checkpoints/c03/specs/signal_policy.json` | `42701d7db45d8a632801bb5f4e187734fc974502` |
| `docs/w03/AI_LOOP_CONSTITUTION.md` | `83bdae9c6511237397811b604d9562420ec40c0f` |
| `docs/w03/SEMANTIC_TRUST_CONTRACT.md` | `e120f4a8cd2f37e0f6084b86e6e606958c6ba68b` |
| `scripts/ci/classify_change.py` | `fd9e99c6b55b85f184198c51f0f97ba16323ce32` |
| `scripts/ci/verify_w04_source_evolution.py` | `4efaefed505e24796a0c2fa545ce4b7eb252d70a` |
| `scripts/ci/verify_publication.py` | `8f97a117f936d9dce91957f7b44551acb5d5c2b6` |
| `scripts/ci/run_w03_ai_loop_gate.py` | `c533928e584335437ae8a902fcab4faab64ae8ef` |
| `.github/workflows/ci.yml` | `14c826b122b7103953e8b4539981004241205ba4` |
| `pyproject.toml` | `318bbc0a858f760e6c4d7a2d3fdbfcc111febb77` |
| `uv.lock` | `619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a` |
| `docker-compose.yml` | `5a0b6e8486edc69f9f79c7e1345a842aa412983c` |
| `tests/test_investigation_contracts.py` | `9c28e84e3ee1ea7b2e5fa92ee01d3f07f05f149f` |
| `tests/test_investigation_case_binding.py` | `1de8de47568c7df789cde60d7ffa079721fe5147` |
| `tests/test_investigation_planning.py` | `2f326879b87fffcd1385a9188cf92ac40f4779b8` |
| `tests/test_investigation_evidence_queries.py` | `54f43e27ce42c0ae6ea903d7b278b916748f40ed` |
| `tests/test_investigation_evidence_navigation.py` | `74e15223abc0accdfd3cb569764f9f94d5f3d70e` |
| `tests/integration/test_investigation_evidence_navigation_database.py` | `fab7e9180e19635eb886624d98c759a669ded5ec` |
| `tests/test_w04_source_evolution.py` | `7d8df8f6b63925ebe22ce22220d67c4891e3be38` |
| `tests/test_c09_ci_gate.py` | `543a3f67a0bba867c4b092b0d64fb415b61e1400` |
| `docs/w04/checkpoints/c04/W04_C04_FINAL_CLOSEOUT_REPORT.md` | `5cc6c9cee1567cb07a91ffc62ac416623d578b62` |

## Exact protected tree identities

| Path | Git tree |
|---|---|
| `src` | `fee1b88425b461a6266685a80faa39165a5ef7e5` |
| `src/flowlens/investigation` | `1fd4ee320afb72c4a53754ceaaf56c79ae072bd0` |
| `src/flowlens/decision` | `71eddb93cfee5c5e5822d6598ef2f4a1f63648df` |
| `src/flowlens/db` | `a3b774f3bcc322ee19951c92948501315b0e7cb2` |
| `src/flowlens/data` | `d5679d706ed19b0802441b1002af5e5e23513edc` |
| `scripts/ci` | `b8ded9847fa8c23309bbd1af11847c8b27666685` |
| `.github` | `978501bf7003ab05e903e22d3930ee5c97470974` |
| `docs/w03` | `cb81e388c6c44a9900575ef2e72161dc0205be94` |
| `migrations` | `c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433` |
| `apps` | `597399c7919982e9b2d54fc8b58fe6784cfe8585` |

## Frozen implementation semantics

C05 consumes exact DecisionPacket/case/questions/plan/queries/slices. Admission
order is frozen W03 packet validation, C02 binding, C03 planning, C04 exact query
projection, original/nested slice structure and identities, bindings, temporal
admission, FreshnessStatus and exact C04 provenance digest recomputation. C05
has no DB argument and does not import or execute C04 navigation. C04 database
replay remains the upstream replay boundary; provenance validates an artifact
envelope rather than establishing database truth.

Exactly one finding per question in C03 question order, bound through exact
signal_id in trigger_refs, never question_code parsing. Exactly eight frozen
finding codes and eleven conflict codes. No causal/root-cause/probability/remedy/
action finding. Inherited UNKNOWN has empty support/contradiction refs; disposition
and capacity remain UNKNOWN. Missing rows/fields never become zero, false or
negative proof. Absent actual fields are distinct from explicit None timestamps.
Only DIRECT_FACT/ASSOCIATIVE_EVIDENCE with FRESH/NOT_APPLICABLE can participate in
support/contradiction; association can support only the two ASSOCIATED codes and
always retains ASSOCIATIVE_ONLY uncertainty. Conflicts remain unresolved without
majority vote or confidence. Preserve exact C03 forbidden codes for every question.

Closed field-specific scalar decoding only: aware datetimes, finite Decimal without
float conversion, exact int, exact identifier/result/material strings. Typed C04
runtime and canonical C01 wire reparse must have identical C05 canonical outputs.
Original nested claims must be structurally checked before detached reconstruction
and canonical comparison; validator rebuilds exact complete outputs. Stable errors
are only the eleven Design Master C05 codes. All output references remain within
the exact question scope or frozen forbidden-inference codes.

Runtime has no DB/SQL/network/filesystem/subprocess/model/LLM/HGT/tool/Human-event/
summary/operational authority, dynamic import/eval/exec/random/secrets/time-now.
Policy is immutable private Python constants; no runtime repository lookup.

## Authorized stage deltas and gates

A: exactly manifest + Human authorization + this context lock. Append only C05
AUTHORIZED/null source freeze/one c05_findings.py path with null blob. Source/test
must not exist. Commit `docs(w04-c05): authorize findings source`; normal push;
wait for exact-SHA Verification PASS before any Stage B file.

B: exactly src/flowlens/investigation/c05_findings.py and
tests/test_investigation_findings.py; Stage A paths frozen. K01-K48 direct proofs,
actual function/parameterized/expanded counts, C04/C03/C02/C01/DEVCTRL regressions,
W03 core/F01-F10, full native non-integration/integration, Ruff, strict mypy, lock,
Compose and Verification. Commit `feat(w04-c05): derive bounded findings conflicts
uncertainty`; normal push; exact-SHA Classify/Quality/Compose/W03/Verification PASS.

C: exactly W04_C05_R_DEVELOPMENT_ROUND_REPORT.md after B PASS. Actual evidence only;
C05 remains AUTHORIZED/null/null. Commit `docs(w04-c05): publish findings proof`;
normal push; exact-SHA Publication/Verification PASS. Actual classifier controls.

Exactly six total repository paths; no seventh. No C01-C04/W03 runtime or existing
test, schema/migration/data/hash/scenario/control/workflow/dependency mutation.
No main write/force push/history rewrite/reset/rebase/amend/stash/restore/discard.
No C05 closeout, C06/C07, PR merge or branch deletion. Stop REVIEW_READY with GPT
independent implementation review and Human acceptance PENDING.

## Local environment and evidence limits

Existing .venv Python 3.12.14 is retained without dependency changes. Sandbox
process setup fails; authorized commands use reviewed sandbox fallback. Existing
pytest temp/cache directories have Windows permission errors: use new task-owned
temporary directories outside the repository and disable pytest cache provider.
Native Linux CI remains authoritative for PostgreSQL/Compose and the two inherited
Windows CRLF-sensitive raw-byte selectors; do not change their implementation.
