# W03-C01 Context Lock

checkpoint_id: W03-C01
context_lock_status: LOCKED
human_authorization: APPROVED
authorization_source: Product Owner message, 2026-09-24

## Verified baseline

baseline_branch: feat/w03-ai-decision-loop
baseline_sha: 08c8d62b635ae5162ecbfed8be308b93006ac94d
tracking_sha: 08c8d62b635ae5162ecbfed8be308b93006ac94d
direct_remote_sha: 08c8d62b635ae5162ecbfed8be308b93006ac94d
pr_number: 6
pr_head_sha: 08c8d62b635ae5162ecbfed8be308b93006ac94d
pr_state: OPEN / DRAFT / NOT MERGED
main_sha: 9d18ddde9fe933952a2661ee1419f13c8577605d
initial_working_tree: CLEAN
tracking: 0 ahead / 0 behind
g0_ci_run: 33 / 35953463455 / SUCCESS

## Authoritative repository document SHA-256

ceb3c166e2d4d2782688d668121bfb1de6ec69bd9d3513cb4d63bc4d9f165c76  AGENTS.md
1850365277f65bbba1637381c37474a853e07b1c1510b6ce30293395cd949e99  LOOP.md
1b617ce032cbdf33b8bbf49e6515a0e8d47b7696f499ca729e33af7709a45da1  docs/CURRENT_STATE.md
aacd1c9372b0799896974dede15f724fd79d9ccaa2031770ca5d78e2df860e40  docs/sprints/W03_ai_decision_loop.md
48702680c6403e3cabfb7e774db72f88cdaabb165899d78d1893cf0373a0ceed  docs/w03/AI_LOOP_CONSTITUTION.md
184d4bbd1ca26f37887525bef0417295da4ddeff6eb7db3b25e0ddabb5fc646d  docs/w03/SEMANTIC_TRUST_CONTRACT.md
cb4a0de4d0fe2ef9231cf6e579c1a557129ab097572e29a0addb43172a52dd8a  docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md
6eaec8e2a918665ac6b21b22a83e6133bd2e827288433d451e0b8beb4381c9b4  docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md
aa291f3d3a8c273a5c8175b9ae5fe58471bd3cba8662c1253de499cd3e5f860d  docs/w03/LOOP_EXECUTION_STATE_MACHINE.md
164afc436c4f00104690d02a4b7b7cea223e7ebe7b74d4a3a164159ee22223ad  docs/w03/FAILURE_AND_DEGRADATION_POLICY.md
74dcc0552595c3c0d368fa527c1b85b34f299ba943bdf16b75407c0a71e1a82a  docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md
86ab221d6ccc967b0c6419b1a024430740a2bda4bb16e8c42aebbd1c98f43a35  docs/context/CONTEXT_INDEX.md
a3d721c65f4a3142596ed2109c54f23818efb85748ffed9015dd2bf9ce951e11  docs/context/MATERIAL_REGISTRY.md
59ae4bfb60c4f8a0136b7dc3256f0dbfe30283d83f9013a1fb600b35273974fc  docs/w03/checkpoints/c01/W03_C01_AUTHORIZATION_CONTRACT.md
1f8cd7644eaad261a709a5f2e0136b48721c239f5b2059b9e04ad48e16784747  docs/w03/checkpoints/c01/W03_C01_CORE_ARTIFACT_CONTRACTS.md
a926ecc4269796982cea98685b58fbc0134f4b05a2bc3707ceb9d494637ea800  docs/w03/checkpoints/c01/W03_C01_GPT_REVIEW_CHECKLIST.md
13003e78d9a97db08062e5ce1346f8a461f0865348f0c74a0bff9c498f19b459  docs/w03/checkpoints/c01/W03_C01_HARNESS_ACCEPTANCE_SPEC.md
2f381833660e4b23aabf917d8f7457c82e96d0f09c223eb8938928f8c0a6a347  docs/w03/checkpoints/c01/W03_C01_HUMAN_AUTHORIZATION.md
2d11d187ff74ade577e7a23a38375911f8b6a8b4181ee4e54f10a2aabe5c7bbe  docs/w03/checkpoints/c01/W03_C01_IDENTITY_PROVENANCE_SERIALIZATION.md

## Input package SHA-256

4109eff7f1b57f134ae4e51272e13d36156477569ab8ae9a155994b49cdd1266  C:\Users\C\Desktop\Flowlens_Industrail_AI\Week3\W3-C01\FlowLens_W03_C01_GPT_COMPLETE_MASTER.md
8ba1c81f7c7c6ce575b61639491df4694030c597c110a2907809a7205b28b4a8  C:\Users\C\Desktop\Flowlens_Industrail_AI\Week3\W3-C01\FlowLens_W03_C01_GPT_Authorization_Package.zip
c09d2c3dcb9ad8f603f24b8723f155b6fccc72af2bb9f847f7e449c9fc4c6fa4  C:\Users\C\Desktop\Flowlens_Industrail_AI\Week3\W3-C01\W03_C01_CODEX_EXECUTION_PROMPT.md

## Runtime and tool boundary

dataset_version: NOT_APPLICABLE_TO_C01_IMPLEMENTATION
dataset_hash: NOT_APPLICABLE_TO_C01_IMPLEMENTATION
scenario_version: NOT_APPLICABLE_TO_C01_IMPLEMENTATION
scenario_config: NOT_APPLICABLE_TO_C01_IMPLEMENTATION
runtime_DecisionContext: NOT_PRESENT
runtime_HGT: FORBIDDEN
model_config: NOT_APPLICABLE
runtime_prompt_version: NOT_APPLICABLE
runtime_prompt_hash: NOT_APPLICABLE
runtime_tool_registry_version: G0_POLICY_ONLY / NO_C01_RUNTIME_TOOL
LLM_tool_access: NONE

Allowed sources: current repository; G0 control documents; C01 authorization package; frozen W1/W2 source and tests for compatibility; PR #6 metadata; GitHub Actions evidence.
Forbidden sources: protected HGT material; scenario truth as runtime input; test oracle answers in runtime artifacts; historical chat as authority; external research; secrets; production databases; unrelated local files.
Development tools: repository filesystem, pytest, Ruff, mypy, safe local PostgreSQL regression, Docker/Compose, Git/GitHub, existing CI.

## Authorized paths

Source: src/flowlens/decision/__init__.py, enums.py, primitives.py, contracts.py, serialization.py.
Tests: tests/test_decision_contracts.py, tests/test_decision_serialization.py.
Governance: docs/w03/checkpoints/c01/*, docs/w03/reports/W03_C01_R_DEVELOPMENT_ROUND_REPORT.md, docs/CURRENT_STATE.md.

Forbidden changes: src/flowlens/data/**; src/flowlens/db/**; src/flowlens/api/**; src/flowlens/worker/**; migrations/**; pyproject.toml; uv.lock; .github/workflows/**; Docker/Compose files; AGENTS.md; LOOP.md; G0 contracts; W1/W2 sprint history.

## Expected context delta

changed_contracts: C01 package publication only
changed_sources: new decision contract/type package only
changed_assumptions: NONE
changed_tool_permissions: NONE
changed_context_materials: C01 lock, Round Report, CURRENT_STATE
changed_runtime_inputs: NONE
schema_or_migration_change: NONE
dependency_change: NONE
operational_mutation: NONE

Lock completed before first source implementation write.
