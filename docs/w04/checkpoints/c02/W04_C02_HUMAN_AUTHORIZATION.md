# W04-C02 Human and Repair Authorization — V2

```text
HUMAN AUTHORIZATION: APPROVED
REPAIR AUTHORIZATION: APPROVED
AUTHORIZED TASK: W04-C02 V2 IMPLEMENTATION + W04-C02-CLARIFICATION-01
ENTRY SHA: ae88a9b1be74bc379140b59a15d6dd9cb714912f
BRANCH: feat/w04-evidence-investigation
PR #7: OPEN / DRAFT / UNMERGED
DEVCTRL CLOSEOUT CI: #93 / 37321990473 / PASS
C02 CLOSEOUT: NOT AUTHORIZED
W04-C03: NOT AUTHORIZED
```

Authority is the Human's pasted V2 resume request and supplied normative
`W04_C02_CODEX_TASK_V2.md` (SHA-256
`b5e23dffbbf044f87919efbb72fa95f6d5cab9279740096b83a3ce85d564e148`).
The separate `W04_C02_CODEX_PROMPT_V2.md` has SHA-256
`623a48bf21d9c075b0aee03747b62fba80a2f45eaa70c93c4293e3ac360e216c`.
V2 overrides the three conflicting V1 requirements; unchanged V1 requirements
remain normative. The previous clarification stop made no repository change.

The authorized scope is deterministic DecisionPacket to InvestigationCase
binding, exact binding validation, B01–B36, exact-SHA implementation proof and
development report publication. CL-01 additionally authorizes only replacing
D01's whole-manifest/bootstrap equality with exact equality of checkpoint zero.
CL-02 preserves the four canonical frozen C05 dispositions and rejects the
reserved CANDIDATE_RECOMMENDED disposition. CL-03 preserves W03 validation
first: its failures map to C02_INVALID_DECISION_PACKET; observational/source
future information surviving that boundary maps to C02_FUTURE_INFORMATION.

The complete path allowlist is:

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c02/W04_C02_HUMAN_AUTHORIZATION.md
docs/w04/checkpoints/c02/W04_C02_CONTEXT_LOCK.md
tests/test_w04_source_evolution.py
src/flowlens/investigation/c02_binding.py
tests/test_investigation_case_binding.py
docs/w04/checkpoints/c02/W04_C02_R_DEVELOPMENT_ROUND_REPORT.md
```

Stage A includes only the first four paths, with C02 runtime source absent.
Stage B may create the two new source/test paths only after Stage A exact-SHA
Verification PASS. Stage C may publish only the development report after Stage
B exact-SHA Verification PASS. The manifest remains AUTHORIZED throughout.

W03 source, C01 source, the DEVCTRL verifier, classifier/workflow, other existing
tests, dependencies, migrations and apps remain frozen. PR merge and branch
deletion are not authorized. Independent GPT review and Human acceptance remain
pending; this authorization does not close C02 or advance C03.
