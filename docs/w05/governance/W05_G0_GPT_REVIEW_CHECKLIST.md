# W05-G0 Independent GPT Review Checklist

TASK_ID = W05_G0_SUCCESSOR_GOVERNANCE_RECOVERY_R2

Implementation evidence is not independent acceptance. Verify each item against
the final exact SHA, original native evidence and the external Development Report.

- [ ] Entry main is exactly 2f1627342ff2b04d8324fbffec3db2e230b302e0.
- [ ] PR #8 is merged/closed; head bd29242 and first merge CI #153 attempt 1 match.
- [ ] Exactly two normal commits exist with the authorized subjects and scopes.
- [ ] Commit A changes exactly README.md, AGENTS.md and docs/CURRENT_STATE.md.
- [ ] Commit B has no unauthorized path or product runtime change.
- [ ] Historical baseline derives from exact historical collection, not G0 HEAD.
- [ ] Historical 2997-node/63-file lists and digests, seven shards and weights match.
- [ ] Canonical seals plus pinned identities reject recomputed unauthorized baselines.
- [ ] No docs/w03, historical docs/w04, manifest, runtime or frozen runner was edited.
- [ ] Historical governance replays unchanged at exact anchor with 172/223/93/95/98.
- [ ] G0-P1-01: dependency sync runs inside the historical tree against its own
      pyproject.toml/uv.lock, with an isolated environment and historical interpreter.
- [ ] Shell controls reject sync failure, verifier failure, and dirty replay output.
- [ ] Current W03 38/85 and W04 9/67/81 are current-HEAD semantic regressions.
- [ ] New test file and added node in a historical file are positively admitted.
- [ ] Historical deletion/rename, duplicates and collection errors are rejected.
- [ ] Current node/file counts and digests are dynamic evidence.
- [ ] Current collection cannot be mislabeled as the immutable W04 baseline.
- [ ] Unchanged historical files retain positive measured weights; both historical
      zeros use the Human-authorized active conservative fallback without changing history.
- [ ] New/changed files use derived maximum historical weight, never zero.
- [ ] Seven file-atomic LPT shards and both deterministic tie-breaks are verified.
- [ ] Wrong seal/anchor/digest/shard count, missing shard and duplicate execution fail.
- [ ] Receipts bind exact HEAD, current plan, assigned nodes and terminal outcomes.
- [ ] JUnit consistency, zero adverse outcomes and explicit skip policy remain enforced.
- [ ] Aggregate proves historical no-loss and exact current union/once.
- [ ] G0 dependency/lock/Compose/migration/app surfaces match exact entry.
- [ ] Future surface changes require explicit versioned successor admission.
- [ ] Protected source, HGT and future-leakage protections remain effective.
- [ ] Three legacy meta-test transitions preserve historical test IDs and runtime traps.
- [ ] No skip/xfail/deletion was used to make CI green.
- [ ] Publication/classifier behavior, major jobs and pinned actions remain intact.
- [ ] Actual Verification shell requires W05 success for every full route.
- [ ] Historical replay failures cannot be hidden by a successful tee or later step.
- [ ] First exact Commit-B native CI attempt 1 passes every required job.
- [ ] Native evidence and local simulation are clearly distinguished.
- [ ] Report covers all required positive/negative controls with executed evidence.
- [ ] Any NOT_RUN remains NOT_RUN; no planned result is presented as established.
- [ ] External ZIP includes the Development Report and a complete SHA-256 manifest.
- [ ] PR is OPEN / READY / UNMERGED, auto-merge absent, branches retained.
- [ ] No C01/C02, W06, release or merge authorization is inferred.
