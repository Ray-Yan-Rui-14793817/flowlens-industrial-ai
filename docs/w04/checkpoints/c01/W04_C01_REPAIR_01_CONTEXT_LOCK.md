# W04-C01 Repair-01 Context Lock

```text
TASK: W04-C01-REPAIR-01
HUMAN AUTHORIZATION: AUTHORIZED — direct Human reply 确认授权
AUTHORIZATION RECORD: W04_C01_REPAIR_01_HUMAN_AUTHORIZATION.md (read back)
GPT AUTHORITY: W04-C01-CLARIFICATION-01
W03 MAIN ANCHOR: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
ENTRY / ORIGINAL IMPLEMENTATION SHA: 084c2fea93d0e021994de015c986de9ff92bf9a3
BRANCH: feat/w04-evidence-investigation
ENTRY TRACKED WORKTREE: CLEAN
ENTRY UNTRACKED DELTA: prior C01 development round report only
CONTEXT LOCK: PASS
RUNTIME / SRC MUTATION: PROHIBITED
W04-C02+: NOT AUTHORIZED
```

Normative package entry hashes verified:

- `W04_C01_GPT_CLARIFICATION_01.md`: `0362682d1b52f641ccfeac6512709a6dca1fe50109b054423bc670479b357b62`
- `W04_C01_CODEX_COMPATIBILITY_REPAIR_TASK_V1.md`: `f41e6fb6c6519fe4cea3dc2ece915be1c3ae43fa7fca5bc4256d3d1f29787336`

Affected file: `tests/test_c09_ci_gate.py`.
Affected selector:
`tests/test_c09_ci_gate.py::test_classifier_publication_and_runtime_frozen_materials_unchanged`.
Entry assertion line: 522. Selector is not in the frozen 38-selector manifest;
its name is preserved. Existing control-file comparisons and migrations/apps
freeze are retained.

Repair source semantics use exact Git `--name-status --no-renames -z` output
against the W03 main anchor. Every delta must be one of exactly these additions:

```text
src/flowlens/investigation/__init__.py
src/flowlens/investigation/contracts.py
src/flowlens/investigation/enums.py
```

Tracked index/worktree changes and non-ignored untracked source additions are
also rejected. No `src/**`, gate manifest, gate runner, classifier, workflow,
dependency, lockfile or migration changes are allowed in this repair.

The original Linux CI Quality job proves the two CRLF-only failures did not
reproduce: 1360 passed, one failure in the stale selector, 48 deselected; database
integration 48 passed. Original CI Run #87 final aggregate is to be recorded in
the development report once complete. The unrelated byte-digest checks remain
unchanged. Full proof uses the same frozen F01-F10 / 38 selectors / 85 cases and
the existing repository-native exact-SHA CI workflow.
