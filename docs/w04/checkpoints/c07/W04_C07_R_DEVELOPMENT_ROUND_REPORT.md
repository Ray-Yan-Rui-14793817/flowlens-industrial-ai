# W04-C07 Development Round Report — Grounded Investigation Summary

Report date: 2026-10-08 (Asia/Shanghai). Evidence cutoff for this immutable publication: Stage B native CI #118 overall SUCCESS, observed 2026-10-08 14:28:17 UTC. Stage B is frozen.

Implementation and its required native full route are complete. This report is the single authorized Stage C addition. Its publication SHA and native CI do not yet exist at authoring time; REVIEW_READY requires this report commit's own successful native proof. The final handoff records those generated values without amending this report.

## 1. Human authority and continuation

The Human request explicitly selected W04_C07_CODEX_TASK_V1.md for implementation and W04_C07_RESUME_AFTER_QUOTA_TASK_V1.md for continuation. Attached documents do not independently grant Human authority. The quota-recovery request requires read-only resume preflight, waiting for #118, no automatic CI repair, report-only Stage C, and its own native proof.

| Selected normative material | Bytes | SHA-256 |
|---|---:|---|
| W04_C07_CODEX_TASK_V1.md | 28280 | 42cd91fb4ead32c6db3d3d1b3d09573dedaf75f10d0fb35e0102ed7c545ba058 |
| W04_C07_RESUME_AFTER_QUOTA_TASK_V1.md | 13987 | ab97f4c634e58cd07aafd2e03e3a42d4273d56fc272cc9e34451fdd7890b9b61 |

GPT C07 architecture / contract design review R1: PASS. Human C07 implementation, DETERMINISTIC and BOUNDED_LLM: APPROVED. DEGRADED_FALLBACK: REQUIRED / APPROVED. Scope is C07 implementation through REVIEW_READY. Independent implementation review and Human acceptance remain pending. No closeout, C08, PR merge or branch deletion is authorized.

The existing Stage A Human authorization and context lock materialize the original approval; neither was recreated or edited during continuation. Current task authority supersedes historical checkpoint stop text only within this explicitly approved scope. Accepted W1/W2/W03 and C01-C06 contracts and evidence remain frozen.

## 2. Immutable anchors and exact-SHA native runs

Repository: Ray-Yan-Rui-14793817/flowlens-industrial-ai. Branch: feat/w04-evidence-investigation. PR #7 remains [OPEN / DRAFT / UNMERGED](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/pull/7). Main / PR base: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509.

| Anchor/stage | Exact SHA | Native run | Actual class / proof | Conclusion |
|---|---|---|---|---|
| C06 accepted closeout | 145ac72626899dc30bcff437685b4698b8edacb4 | [#115 / 37735563458](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37735563458) | C / FULL_EXACT_SHA | SUCCESS |
| C07 entry | e372b0d8ab038eda936d3a3b9ce4d77bfc8fce29 | [#116 / 37749570874](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37749570874) | UNKNOWN / FULL_EXACT_SHA | SUCCESS |
| Stage A governance | a44e06bed9c3a0ce0ef1ec360777f067e68e26a9 | [#117 / 37759205132](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37759205132) | C / FULL_EXACT_SHA | SUCCESS |
| Stage B implementation | c86f7af2370f315b8b7310008521f08ceade6d97 | [#118 / 37773147744](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37773147744) | I / FULL_EXACT_SHA | SUCCESS |

C06 closeout is an ancestor of entry. The sole closeout-to-entry change is README.md, commit `docs(v1): refresh product-centered README`. Entry classifier reason is `unknown_or_empty_delta`; its actual UNKNOWN full route is retained, not reinterpreted.

Entry #116 measured native non-integration: 2457 passed / 3 skipped / 70 deselected / 1 warning, 3988.25s. Integration: 70 passed / 2460 deselected / 1 warning, 276.11s. Ruff PASS; strict mypy PASS / 162 files; lock PASS / 43 packages; Compose, W03 and Verification SUCCESS; Publication SKIPPED.

Stage A measured native non-integration: 2457 passed / 3 skipped / 70 deselected / 1 warning, 3960.85s. Integration: 70 passed / 2460 deselected / 1 warning, 258.40s. Ruff PASS; strict mypy PASS / 162 files; lock PASS / 43 packages; Compose, W03 and Verification SUCCESS; Publication SKIPPED. Stage A and entry W03 gate each passed F01-F10 / 38 selectors / 85 cases.

### Read-only resume and Stage B freeze

Resume preflight at 2026-10-08 13:04:19 UTC reverified branch, clean index/worktree, local HEAD, origin tracking ref, direct remote feature head and PR head, all at Stage B. Parent was exactly Stage A; both exact commit subjects and five-path Stage B delta matched. PR was open/draft/unmerged. Stage C file was absent. #118 was still running; no repository file was mutated while waiting.

At 2026-10-08 14:28 UTC, after overall #118 SUCCESS, the same local/tracking/direct-remote/PR heads, parent, clean status and absent report were reverified. Direct remote main remained af61bdfd5f7cf7961811c4c2dc8e554dd7eed509. The run was obtained by querying the exact Stage B commit; classifier base/head, Quality EXPECTED_HEAD and W03 implementation_sha independently bind that SHA. Stage B has not been amended, rewritten, recreated or repaired after commit. No CI rerun/cancel/configuration mutation occurred.

## 3. Exact stage deltas and source identities

Stage A is a direct child of entry. Exact subject:

```text
docs(w04-c07): authorize grounded investigation summary
```

Exactly three paths:

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c07/W04_C07_HUMAN_AUTHORIZATION.md
docs/w04/checkpoints/c07/W04_C07_CONTEXT_LOCK.md
```

Stage B is a direct child of Stage A. Exact subject:

```text
feat(w04-c07): render grounded investigation summaries
```

Exactly five added paths; no sixth path, 2549 insertions:

```text
src/flowlens/investigation/c07_policy.py
src/flowlens/investigation/c07_provider.py
src/flowlens/investigation/c07_summary.py
tests/test_investigation_summary.py
tests/test_investigation_summary_provider.py
```

| Stage B runtime source | Actual Git blob |
|---|---|
| src/flowlens/investigation/c07_policy.py | c969c4bbf33910fab6ffb36c3bfe184fd42c74c9 |
| src/flowlens/investigation/c07_provider.py | 56ecb9f3d7b5a1917a2354572e8c946f07eb759d |
| src/flowlens/investigation/c07_summary.py | 3d561da7ab625421bbcf2dcb3785f8fae792cbff |

Stage A appends only C07 to the source-evolution manifest. C01-C06 entries remain CLOSED and identical to entry; C08 is absent. C07 state remains AUTHORIZED, source_freeze_sha null, and its exact three source paths each have blob_oid null. The measured Stage B blobs above are evidence, not a manifest closeout.

Entry manifest Git blob: 86bc83aed3405b4cc236f78dbcb2487d11bd32d0; accepted Git-byte SHA-256: fae0b063ce3b29a7ff7408bd10cadf9abd541010b42a331162fd46a3a8927947.

Stage A/B manifest Git blob: c11759236c6382b4cad1766092f11cf8bd20ce5c; accepted Git-byte SHA-256: 4096431ab26b3a3a58e91a469fa3da4d23478ef9a7ad9e94f951d73fb6354a6e.

The unchanged production source-evolution verifier passed at committed Stage A and Stage B and again during resume: expected_head is Stage B, w03_baseline_sha is the accepted main anchor, closed_checkpoints C01-C06, authorized_checkpoints exactly C07, overall PASS. S52 also exercises AUTHORIZED/CLOSED lifecycle against disposable modeled manifests using the unchanged verifier. That test does not transition the real C07 manifest.

## 4. Deterministic summary semantics

`render_investigation_summary` accepts the exact ten-element frozen context: DecisionPacket, InvestigationCase, tuple of InvestigationQuestion, InvestigationPlan, tuple of EvidenceQuerySpec, tuple of EvidenceSlice, tuple of FindingRecord, tuple of ConflictRecord, UncertaintyRegister and a nonempty exact tuple of exact HumanInvestigationEvent values. It first calls unchanged C05 `validate_findings_conflicts_uncertainty` on the first nine arguments, then unchanged C06 `validate_human_investigation_event` for every supplied event in parent-chain order with its exact previous event. It does not rebuild replacement upstream context or read a Human journal.

Output uses unchanged C01 SummarySectionRecord / InvestigationSummaryRecord and identity conventions. The top-level case, plan and uncertainty-register IDs are exact; finding, conflict and Human event IDs are sorted unique exact sets. Human chain order determines the latest event independently of the sorted Human ID set.

| Fixed section | Deterministic text content | System-generated grounding refs |
|---|---|---|
| CASE_SCOPE | Only subject_type, subject_id, as_of_time, plan step count | Case and plan |
| FINDINGS | All finding code / exact status pairs, ordered by code and artifact ID | All finding IDs |
| CONFLICTS | All conflict code / exact type pairs, same ordering; explicit empty state | All conflict IDs |
| UNCERTAINTY | All uncertainty code / exact type pairs, same ordering; explicit empty state | Register and every uncertainty-item ID |
| HUMAN_REVIEW | Event count, latest outcome, latest occurred_at and fixed NON_EVIDENCE boundary | All Human event IDs |
| AUTHORITY_BOUNDARY | Fixed presentation-only, association != causality, unresolved-state, Human-note and no-operational-authority text | Empty |

Every ref tuple is sorted and unique. Finding status/type bindings and every conflict/uncertainty row survive rendering. UNKNOWN, UNRESOLVED, MISSING_EVIDENCE and forbidden inference remain their frozen source states. The summary neither resolves them nor adds causal, confidence, trust or remedy conclusions.

Human note_text is never quoted, paraphrased, classified, analyzed, rendered as facts, given to the provider or used as a grounding ref. Its only involvement is opaque validation through the unchanged C06 admission path. Human metadata and the fixed HUMAN_NOTE_NON_EVIDENCE boundary do not upgrade an event into operational authority.

The pure renderer and policy have no SDK, environment, filesystem, DB, network, journal, HGT, current-clock or random capability. Same-process, fresh-process and multiple PYTHONHASHSEED tests compare actual canonical wire bytes and identities.

Supplied-summary validation checks the ORIGINAL top-level C01 identity/hash and every ORIGINAL child identity/hash before any detached `replace` reconstruction. This is necessary because a top-level C01 digest does not bind a child's separately supplied derived identity/hash claim. Exact types reject subclass/foreign-enum/collection substitutions. Validation then enforces context IDs, source refs, section shape/order, version, effective modes, deterministic authority and bounded wording. Deterministic and fallback texts must reconstruct exactly; mixed effective modes are rejected.

## 5. Frozen provider policy and bounded presentation

| Policy | Frozen value |
|---|---|
| Summary contract | w04-c07-summary-v1 |
| Deterministic renderer | w04-c07-deterministic-v1 |
| Bounded renderer | w04-c07-bounded-llm-v1 |
| Provider policy | w04-c07-openai-v1 |
| Provider output schema | w04-c07-provider-output-v1 |
| Exact ASCII prompt-byte SHA-256 | 011e2284cf97c84bf47f0638130b6b6381cc413cde509c403e40be3e0e4ba07e |
| Provider section characters | 1 through 1600, trimmed |
| Total provider section characters | At most 3000 |
| Raw provider output | At most 65536 bytes |
| Provider runtime JSON | At most 262144 bytes |
| SDK request timeout / output tokens / retries | 15.0 seconds / 2000 / 0 |
| Static model / endpoint | gpt-5.6-terra / https://api.openai.com/v1 |
| Own adapter authentication read | Only FLOWLENS_OPENAI_API_KEY |
| Provider calls per render | At most one; no repair call |

The task's 800-character per-section value is a recommendation, not a mandatory contract limit. The frozen 1600-character choice preserves every row of the admitted 21-item uncertainty fixture; measured baseline UNCERTAINTY text lengths for normal/unknown/conflict shapes are 904/1148/1200 characters. The recommended 3000-character total remains enforced. Deterministic/fallback source facts are not truncated to provider budgets. An input or output that cannot satisfy provider bounds degrades safely.

The provider is explicitly caller-injected, never automatically created by the pure renderer. Runtime data is canonical JSON for deterministic sections 1-5 only. Each has exactly section_code, deterministic_text and grounding_refs. It contains no raw investigation graph, Human note_text, query/SQL payload, tool instructions, DB connection, HGT or secrets. References originate in admitted frozen artifacts and are validated; the provider has no authority to select references. Section 6 is never sent for rewriting.

A positive finite grammar accepts exact baseline wording and only the frozen equivalent labels/headings/row delimiters. It preserves all rows, their order, each code/status/type binding and every field-bound number/time value. A token's presence elsewhere in the context never permits rebinding it to another field. Free paraphrases, omitted/deduplicated rows, extra claims or unsupported source-state resolution fail closed. This deliberately conservative accepted vocabulary is a presentation limitation.

Output must be UTF-8 strict JSON with exactly schema_version and sections; sections must be exactly the first five ordered codes and each must contain only section_code and text. Duplicate keys, extra/missing fields, wrong version/order/type, whitespace, length/byte failures and invented artifact/numeric/time facts are rejected. Causal/probability/confidence/guarantee/remedy/trust/operational/capability/injection claims are rejected.

The official Responses adapter uses the existing locked OpenAI 2.54.0 SDK: explicit api_key, empty admin key/organization/project/webhook settings, static base URL, bounded timeout, max_retries=0 and DefaultHttpxClient(trust_env=False, follow_redirects=False). It clears the locked SDK's ambient custom-header field before sending. The request has tools=[], tool_choice=none, stream=false, store=false, background=false, reasoning effort none, output token limit 2000 and a fresh strict JSON schema dictionary. It requires completed/no-error response and exactly one trimmed output_text chunk; refusal, tool/other output or unexpected shape fails. Opaque reasoning metadata is not evidence or summary text.

The own adapter's only environment read is the approved key. The locked SDK has transitive logging/custom-header behavior; the capability claim is about C07's own code and explicit request boundary, not blanket transitive SDK purity. Explicit constructor values and discarded custom headers prevent ambient auth/routing overrides. No SDK, dependency, global environment, system ACL or machine setting was modified.

API/schema/model configuration was checked against [official Structured Outputs documentation](https://developers.openai.com/api/docs/guides/structured-outputs) and the [official model reference](https://developers.openai.com/api/docs/models/gpt-5.6-terra). That documentation check and fake request proof do not verify live account/model availability.

Stable public errors are exactly:

```text
C07_INVALID_SUMMARY_CONTEXT
C07_HUMAN_CHAIN_REQUIRED
C07_HUMAN_CHAIN_INVALID
C07_RENDERER_MODE_INVALID
C07_SUMMARY_REFERENCE_MISMATCH
C07_SUMMARY_SECTION_MISMATCH
C07_SUMMARY_RECORD_MISMATCH
C07_PROVIDER_OUTPUT_INVALID
C07_PROVIDER_POLICY_VIOLATION
```

### Whole-summary fallback and honest limitations

LLM wording is not byte-deterministic.

The deterministic renderer is the mandatory authoritative presentation path.

Accepted LLM wording is presentation-only. Grounding refs are deterministic/system-controlled, never provider-controlled. The provider receives deterministic baseline summary data, not Human note_text.

Provider absence, missing/invalid authentication, failure, refusal, invalid/unsafe output or unexpected provider-validation exception degrades to deterministic fallback. All first-five sections use their exact baseline texts/refs with DEGRADED_FALLBACK. AUTHORITY_BOUNDARY remains byte-identical DETERMINISTIC with empty refs. No mixed partial success and no second call are allowed. Error details, raw response and secrets never enter the summary artifact.

No provider output changes findings, conflicts, uncertainty or Human events. No provider output creates operational authority.

CI/tests use fake provider/client proof; no live provider call is required for C07 implementation proof, and none was performed. Network/service reliability, actual model output distribution, account authorization and model availability are not proven. The optional adapter remains bounded and fail-closed when those conditions fail.

## 6. Direct S01-S52 proof and measured C07 counts

Every matrix requirement has direct selectors in the two authorized test files. All 52 are PASS at Stage B locally and within its own native complete-suite run. Function counts are measured from the committed test AST; expanded counts come from pytest collection/execution, not from the number of matrix rows.

| Test file | Test functions | Parameterized functions | Expanded cases | Exact Stage B local | Exact Stage B native |
|---|---:|---:|---:|---|---|
| tests/test_investigation_summary.py | 37 | 22 | 128 | PASS | 128 passed |
| tests/test_investigation_summary_provider.py | 22 | 15 | 138 | PASS | 138 passed |
| Total | 59 | 37 | 266 | 266 passed, 1351.54s | 266 passed, no skips |

The final exact-Stage-B local invocation includes both committed source-lifecycle cases; no case remains pending. It supersedes precommit focused proof of 259 passed / 2 deselected (1121.69s) plus five added exact-type cases passed (46.54s), which covered 264 cases before the two commit-dependent lifecycle cases could execute.

The S51 audits include negative controls that demonstrate forbidden capabilities are detected, fresh pure imports, live capability traps, explicit one-auth-read transport inspection and input immutability. S52 checks frozen source blobs, protected trees/dependencies/control bytes and the unchanged production verifier.

| Requirement | Direct proof | Result | Committed selector(s) |
|---|---|---|---|
| S01 | Exact full C05 context admission | PASS | `tests/test_investigation_summary.py::test_s01_every_exact_c05_argument_is_admitted`<br>`tests/test_investigation_summary.py::test_s01_upstream_failure_is_detail_free_and_precedes_other_input` |
| S02 | Nonempty exact Human event tuple | PASS | `tests/test_investigation_summary.py::test_s02_nonempty_exact_human_tuple_required` |
| S03 | Unchanged C06 full Human chain validation | PASS | `tests/test_investigation_summary.py::test_s03_each_human_event_uses_unchanged_validator_in_parent_order` |
| S04 | Exact top-level summary references | PASS | `tests/test_investigation_summary.py::test_s04_exact_top_level_references_and_sorted_human_id_set`<br>`tests/test_investigation_summary.py::test_s04_s33_rehashed_top_reference_tamper_rejected` |
| S05 | Exact six-section order and codes | PASS | `tests/test_investigation_summary.py::test_s05_s13_frozen_six_sections_and_deterministic_authority` |
| S06 | Deterministic CASE_SCOPE | PASS | `tests/test_investigation_summary.py::test_s06_case_scope_only_four_frozen_values` |
| S07 | Deterministic FINDINGS | PASS | `tests/test_investigation_summary.py::test_s07_s08_findings_preserve_exact_code_status_order_and_refs` |
| S08 | Exact finding status; no causal upgrade | PASS | `tests/test_investigation_summary.py::test_s07_s08_findings_preserve_exact_code_status_order_and_refs`<br>`tests/test_investigation_summary_provider.py::test_s08_s16_s17_s18_actual_status_type_bindings_and_row_coverage_cannot_change` |
| S09 | Deterministic CONFLICTS | PASS | `tests/test_investigation_summary.py::test_s09_conflicts_preserve_exact_code_type_order_and_all_refs` |
| S10 | Deterministic UNCERTAINTY | PASS | `tests/test_investigation_summary.py::test_s10_s18_uncertainty_preserves_every_type_and_forbidden_inference` |
| S11 | Deterministic HUMAN_REVIEW | PASS | `tests/test_investigation_summary.py::test_s11_latest_human_metadata_is_chain_tail_without_authority_upgrade` |
| S12 | Human note_text never rendered | PASS | `tests/test_investigation_summary.py::test_s12_human_note_is_opaque_never_rendered_or_referenced` |
| S13 | Deterministic AUTHORITY_BOUNDARY | PASS | `tests/test_investigation_summary.py::test_s05_s13_frozen_six_sections_and_deterministic_authority`<br>`tests/test_investigation_summary.py::test_s13_s32_rehashed_deterministic_text_and_fallback_text_tamper_rejected` |
| S14 | Explicit zero-conflict semantics | PASS | `tests/test_investigation_summary.py::test_s14_s15_zero_conflicts_and_uncertainty_are_explicit` |
| S15 | Explicit zero-uncertainty semantics | PASS | `tests/test_investigation_summary.py::test_s14_s15_zero_conflicts_and_uncertainty_are_explicit` |
| S16 | UNKNOWN remains UNKNOWN | PASS | `tests/test_investigation_summary.py::test_s16_s17_unknown_and_unresolved_remain_explicit`<br>`tests/test_investigation_summary_provider.py::test_s08_s16_s17_s18_actual_status_type_bindings_and_row_coverage_cannot_change` |
| S17 | UNRESOLVED remains UNRESOLVED | PASS | `tests/test_investigation_summary.py::test_s16_s17_unknown_and_unresolved_remain_explicit`<br>`tests/test_investigation_summary_provider.py::test_s08_s16_s17_s18_actual_status_type_bindings_and_row_coverage_cannot_change` |
| S18 | FORBIDDEN inference never becomes support | PASS | `tests/test_investigation_summary.py::test_s10_s18_uncertainty_preserves_every_type_and_forbidden_inference`<br>`tests/test_investigation_summary_provider.py::test_s08_s16_s17_s18_actual_status_type_bindings_and_row_coverage_cannot_change` |
| S19 | Original input bytes unchanged | PASS | `tests/test_investigation_summary.py::test_s19_original_input_bytes_unchanged_for_every_mode` |
| S20 | Same-process deterministic identity | PASS | `tests/test_investigation_summary.py::test_s20_same_process_byte_determinism` |
| S21 | Fresh-process deterministic identity | PASS | `tests/test_investigation_summary.py::test_s21_s22_actual_wire_fresh_process_and_hash_seed_determinism` |
| S22 | Multiple PYTHONHASHSEED deterministic identity | PASS | `tests/test_investigation_summary.py::test_s21_s22_actual_wire_fresh_process_and_hash_seed_determinism` |
| S23 | Canonical serialization round trip | PASS | `tests/test_investigation_summary.py::test_s23_canonical_serialization_round_trip` |
| S24 | Packet/case mismatch rejection | PASS | `tests/test_investigation_summary.py::test_s24_s25_s26_s27_s28_foreign_valid_context_envelopes_rejected` |
| S25 | Plan mismatch rejection | PASS | `tests/test_investigation_summary.py::test_s24_s25_s26_s27_s28_foreign_valid_context_envelopes_rejected` |
| S26 | Finding-set mismatch rejection | PASS | `tests/test_investigation_summary.py::test_s24_s25_s26_s27_s28_foreign_valid_context_envelopes_rejected` |
| S27 | Conflict-set mismatch rejection | PASS | `tests/test_investigation_summary.py::test_s24_s25_s26_s27_s28_foreign_valid_context_envelopes_rejected` |
| S28 | Uncertainty-register mismatch rejection | PASS | `tests/test_investigation_summary.py::test_s24_s25_s26_s27_s28_foreign_valid_context_envelopes_rejected` |
| S29 | Original Human identity tamper rejection | PASS | `tests/test_investigation_summary.py::test_s29_human_original_identity_tamper_rejected` |
| S30 | Human parent-chain mismatch rejection | PASS | `tests/test_investigation_summary.py::test_s30_human_parent_chain_is_complete_and_exact` |
| S31 | Human case/time-chain mismatch rejection | PASS | `tests/test_investigation_summary.py::test_s31_human_case_and_chronology_mismatches_rejected` |
| S32 | Original summary and child identity tamper rejection | PASS | `tests/test_investigation_summary.py::test_s32_original_top_and_child_identity_checked_before_any_replace`<br>`tests/test_investigation_summary.py::test_s32_exact_summary_and_child_collection_types_required`<br>`tests/test_investigation_summary.py::test_s13_s32_rehashed_deterministic_text_and_fallback_text_tamper_rejected` |
| S33 | Grounding-ref tamper rejection | PASS | `tests/test_investigation_summary.py::test_s04_s33_rehashed_top_reference_tamper_rejected`<br>`tests/test_investigation_summary.py::test_s33_rehashed_section_grounding_ref_tamper_rejected` |
| S34 | Missing/extra/reordered section rejection | PASS | `tests/test_investigation_summary.py::test_s34_rehashed_section_shape_tamper_rejected` |
| S35 | Mixed renderer-mode rejection | PASS | `tests/test_investigation_summary.py::test_s35_mixed_effective_renderer_modes_rejected`<br>`tests/test_investigation_summary.py::test_s35_renderer_request_requires_exact_frozen_enum` |
| S36 | Wrong summary contract version rejection | PASS | `tests/test_investigation_summary.py::test_s36_rehashed_wrong_summary_contract_version_rejected` |
| S37 | Valid fake provider: first five sections only | PASS | `tests/test_investigation_summary_provider.py::test_s37_valid_fake_provider_is_bounded_only_for_first_five_sections`<br>`tests/test_investigation_summary_provider.py::test_s37_alternate_row_separator_keeps_every_row_and_binding` |
| S38 | Provider receives deterministic baseline only | PASS | `tests/test_investigation_summary_provider.py::test_s38_provider_receives_only_exact_deterministic_baseline_section_data`<br>`tests/test_investigation_summary_provider.py::test_s38_s39_s51_adapter_rejects_unsafe_runtime_before_auth_or_transport` |
| S39 | Provider context excludes Human note_text | PASS | `tests/test_investigation_summary_provider.py::test_s39_human_notes_are_absent_from_provider_data_and_result`<br>`tests/test_investigation_summary_provider.py::test_s38_s39_s51_adapter_rejects_unsafe_runtime_before_auth_or_transport` |
| S40 | Provider cannot control grounding refs | PASS | `tests/test_investigation_summary_provider.py::test_s40_provider_cannot_choose_even_allowlisted_grounding_refs` |
| S41 | Provider absence/auth failure: fallback | PASS | `tests/test_investigation_summary_provider.py::test_s41_absent_provider_and_explicit_fallback_do_not_call_transport`<br>`tests/test_investigation_summary_provider.py::test_s41_missing_or_invalid_auth_key_degrades_without_sdk_or_request` |
| S42 | Transport failure/refusal: fallback | PASS | `tests/test_investigation_summary_provider.py::test_s42_transport_failure_details_never_enter_fallback`<br>`tests/test_investigation_summary_provider.py::test_s42_s49_sdk_refusal_failure_or_unexpected_shape_has_no_retry` |
| S43 | Invalid UTF-8/JSON/schema/order: fallback | PASS | `tests/test_investigation_summary_provider.py::test_s43_all_malformed_json_schema_and_order_fail_closed` |
| S44 | Section/total/raw output budgets | PASS | `tests/test_investigation_summary_provider.py::test_s44_frozen_section_total_and_raw_output_budgets` |
| S45 | Invented artifact token: fallback | PASS | `tests/test_investigation_summary_provider.py::test_s45_invented_w03_w04_artifact_tokens_are_rejected` |
| S46 | Invented/rebound numeric/time facts: fallback | PASS | `tests/test_investigation_summary_provider.py::test_s46_invented_numeric_or_temporal_facts_fail_closed`<br>`tests/test_investigation_summary_provider.py::test_s46_existing_number_and_time_cannot_be_rebound_to_another_field` |
| S47 | Causal/probability/remedy/trust/resolution claims: fallback | PASS | `tests/test_investigation_summary_provider.py::test_s47_causal_probability_remedy_trust_and_resolution_claims_fail_closed` |
| S48 | Operational/tool/DB/web/HGT/injection claims: fallback | PASS | `tests/test_investigation_summary_provider.py::test_s48_operational_capability_and_prompt_injection_claims_fail_closed` |
| S49 | At most one call; no repair/retry | PASS | `tests/test_investigation_summary_provider.py::test_s49_unexpected_validation_error_degrades_without_second_call`<br>`tests/test_investigation_summary_provider.py::test_s49_s50_official_adapter_exact_bounded_request_and_one_call`<br>`tests/test_investigation_summary_provider.py::test_s42_s49_sdk_refusal_failure_or_unexpected_shape_has_no_retry` |
| S50 | Exact bounded official provider request | PASS | `tests/test_investigation_summary_provider.py::test_s49_s50_official_adapter_exact_bounded_request_and_one_call` |
| S51 | Pure/transport capability isolation | PASS | `tests/test_investigation_summary.py::test_s51_frozen_versions_prompt_bytes_schema_and_error_vocabulary`<br>`tests/test_investigation_summary.py::test_s51_pure_capability_audit_negative_controls`<br>`tests/test_investigation_summary.py::test_s51_pure_source_ast_and_fresh_import_have_no_transport_or_journal`<br>`tests/test_investigation_summary.py::test_s51_live_capability_traps_preserve_inputs_and_authority`<br>`tests/test_investigation_summary_provider.py::test_s38_s39_s51_adapter_rejects_unsafe_runtime_before_auth_or_transport`<br>`tests/test_investigation_summary_provider.py::test_s51_transport_capability_audit_negative_controls`<br>`tests/test_investigation_summary_provider.py::test_s51_actual_transport_source_has_only_bounded_sdk_and_single_auth_read` |
| S52 | Unchanged upstream/W03/source-evolution proof | PASS | `tests/test_investigation_summary.py::test_s52_committed_source_lifecycle_and_unchanged_production_verifier`<br>`tests/test_investigation_summary.py::test_s52_frozen_upstream_w03_dependencies_and_control_bytes_unchanged` |

## 7. Exact Stage B regression evidence

### Final local focused regressions

One fresh exact-Stage-B invocation collected 1511 cases across the existing eight C01-C06 files, DEVCTRL and six W03 core files. Result: 1505 passed / 6 skipped, 2791.40s (46:31), no failures.

| Scope | Passed | Skipped | Collected cases |
|---|---:|---:|---:|
| C01-C06 | 1313 | 6 | 1319 |
| DEVCTRL / source evolution | 127 | 0 | 127 |
| W03 core | 65 | 0 | 65 |
| Total | 1505 | 6 | 1511 |

C01-C06 + DEVCTRL subtotal: 1440 passed / 6 skipped. Local skips are unchanged tests/test_investigation_human_store.py:496, `host does not permit symlink creation: OSError`. Fresh short system temporary paths and `-p no:cacheprovider` were used; no accepted harness was weakened.

The 65-case W03 core consists of test_decision_contracts (23), serialization (16), temporal (14), context (3), snapshot (2), evidence (7). Final local Ruff and strict mypy also passed; mypy checked 167 source files.

### Native complete-suite regression groups

The following counts are measured from each filename's dot/skip groups in Stage B's native COMPLETE non-integration suite log. They are subsets of that same native invocation, not separate native focused runs, and must not be added to the complete-suite totals.

| Native file / scope | Passed | Skipped |
|---|---:|---:|
| C01 test_investigation_contracts.py | 426 | 0 |
| C02 test_investigation_case_binding.py | 76 | 0 |
| C03 test_investigation_planning.py | 187 | 0 |
| C04 test_investigation_evidence_queries.py | 92 | 0 |
| C04 test_investigation_evidence_navigation.py | 124 | 0 |
| C05 test_investigation_findings.py | 188 | 0 |
| C06 test_investigation_human.py | 115 | 0 |
| C06 test_investigation_human_store.py | 108 | 3 |
| C01-C06 subtotal | 1316 | 3 |
| DEVCTRL test_w04_source_evolution.py | 127 | 0 |
| C01-C06 + DEVCTRL subtotal | 1443 | 3 |
| W03 core six files | 65 | 0 |
| C07 two files | 266 | 0 |

Native skip reason: tests/test_investigation_human_store.py:508, `Windows junction surface`, three cases. Local and native platform skips differ; the C01-C06 collection remains 1319 cases.

## 8. Stage B actual native route, logs and gate proof

Actual classifier reason: verified_source_head_delta; base_sha Stage A; head_sha Stage B; changed_paths exactly the five Stage B additions. Class I / FULL_EXACT_SHA. Every required job completed successfully; Publication was skipped under the unchanged full-route policy.

| Native job | Job ID / evidence | Actual conclusion |
|---|---|---|
| Classify change | [113297405160](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37773147744/job/113297405160) | SUCCESS, I / FULL_EXACT_SHA |
| Docker Compose smoke | [113297467818](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37773147744/job/113297467818) | SUCCESS |
| Quality gate | [113297467864](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37773147744/job/113297467864) | SUCCESS |
| Publication proof | 113297469611 | SKIPPED |
| W03 AI loop gate | [113359985933](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37773147744/job/113359985933) | SUCCESS |
| Verification gate | [113362686662](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37773147744/job/113362686662) | SUCCESS |

| Native Quality proof | Actual measurement |
|---|---|
| Collected items per invocation | 2796 |
| Non-integration | 2723 passed / 3 skipped / 70 deselected / 1 warning; 8308.68s (2:18:28) |
| Integration | 70 passed / 2726 deselected / 1 warning; 345.02s (0:05:45) |
| Ruff | All checks passed |
| Strict mypy | Success: no issues found in 167 source files |
| Dependency lock | Resolved 43 packages; unchanged lock check PASS |

Native log evidence (pytest banner padding omitted):

```text
2026-10-08T11:54:48.5077848Z EXPECTED_HEAD: c86f7af2370f315b8b7310008521f08ceade6d97
2026-10-08T12:00:50.9597368Z 70 passed, 2726 deselected, 1 warning in 345.02s (0:05:45)
2026-10-08T14:19:21.6520940Z SKIPPED [3] tests/test_investigation_human_store.py:508: Windows junction surface
2026-10-08T14:19:21.6521974Z 2723 passed, 3 skipped, 70 deselected, 1 warning in 8308.68s (2:18:28)
2026-10-08T14:19:23.7833013Z All checks passed!
2026-10-08T14:19:44.6758238Z Success: no issues found in 167 source files
2026-10-08T14:19:44.7467813Z Resolved 43 packages in 1ms
```

Native Quality also passed exact-head verification, locked dependency restore, PostgreSQL readiness, migrations, isolated Week 2 smoke database/profile generation and validation, public artifact/HGT isolation and cleanup. Those are isolated native validation actions, not operational production mutation.

Compose passed exact-head checkout, configuration, application image build, stack startup, PostgreSQL readiness, API health contract, Worker running check and teardown. The optional failure-diagnostic step was skipped; job result SUCCESS.

Verification's actual environment at 2026-10-08T14:25:28Z was CHANGE_CLASS=I, CLASS_RESULT=success, QUALITY_RESULT=success, COMPOSE_RESULT=success, W03_RESULT=success, PUBLICATION_RESULT=skipped; `Enforce class-specific exact-SHA proof` completed SUCCESS.

### Frozen W03 F01-F10 gate

Gate version: w03-c09-ai-loop-gate-v1. Schema: w03-c09-gate-summary-v1. Native summary implementation_sha: c86f7af2370f315b8b7310008521f08ceade6d97. Frozen manifest SHA-256: bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990. Overall PASS.

| Frozen family | Selectors | Expanded cases | Result |
|---|---:|---:|---|
| F01 CORE_CONTRACTS | 3 | 3 | PASS |
| F02 TEMPORAL_SEMANTIC_TRUST | 3 | 7 | PASS |
| F03 SIGNAL_DIAGNOSIS_FAIL_CLOSED | 4 | 10 | PASS |
| F04 COUNTERFACTUAL_ISOLATION | 3 | 5 | PASS |
| F05 RECOMMENDATION_ABSTENTION | 4 | 11 | PASS |
| F06 HUMAN_AUTHORITY_AUDIT | 4 | 6 | PASS |
| F07 PROTECTED_EVALUATION_REPLAY | 3 | 11 | PASS |
| F08 LLM_GROUNDING_SCHEMA_INJECTION | 6 | 6 | PASS |
| F09 REAL_DATASET_BINDING_DIRECTION | 3 | 6 | PASS |
| F10 RUNTIME_CAPABILITY_ISOLATION | 5 | 20 | PASS |
| Total | 38 | 85 | PASS |

These are the unchanged native W03 gate selections, including its protected offline evaluation plane; no W03 implementation or W04-C08 replay was added.

## 9. Failures, recovery and limits of evidence

The initial local DEVCTRL invocation hit existing pytest temporary/cache ACL restrictions: 6 passed / 121 setup errors / 2 warnings, 20.85s. The unchanged suite rerun with fresh temporary storage and cache disabled passed all 127 cases in 220.26s. This was a local execution-path issue, not a source-evolution repair.

The initial local C01-C06 baseline on a long proof-root temporary path produced 1243 passed / 70 failed / 6 skipped in 1645.48s. All 70 failures were unchanged Human-store IO FileNotFound paths; a measured event path was 288 characters and machine LongPathsEnabled was 0. The entire unchanged Human-store suite rerun under a fresh short system temporary path produced 105 passed / 6 skipped in 830.30s. All 70 failures disappeared with only the temporary-path change. The resulting initial baseline union was 1313 passed / 6 skipped (1319 cases); it was not one fresh whole-suite invocation. The final exact-Stage-B single regression invocation in section 7 provides the complete fresh focused proof.

Ordinary precommit typing/lint defects were corrected only within the five authorized Stage B paths before the implementation commit. No CI repair, accepted semantic change or source/test modification occurred after Stage B commit.

Local execution used the existing .venv Python 3.12.14. gh and uv were absent locally; no tool/dependency installation was performed. Native Linux supplies the full suite, database integration, uv lock check, Compose and W03 gate proof. No complete native-equivalent Windows suite result is claimed. The two historical accepted CRLF-sensitive Windows selectors, test_c06_harness::test_frozen_c01_and_c05_sources_match_context_lock and test_c09_ci_gate::test_frozen_manifest_schema_families_counts_and_content, remain unchanged and pass in the native Linux full route.

Sandbox helper process setup returned helper_unknown_error. Required commands used scoped auto-reviewed escalation; no request was rejected. An auxiliary browser CI read encountered the same helper startup failure and performed no UI action; GitHub connectors supplied native logs/status. Temporary ACLs, long-path registry settings and SDK/global configuration were not changed.

While Quality was active, its log download returned 404 BlobNotFound. That was log unavailability, not a CI conclusion. Completed logs were subsequently extracted. The long complete suite was allowed to finish without timeout/worker/workflow mutation or native rerun.

## 10. Frozen boundaries and no scope expansion

Entry-to-Stage-B tracked delta is exactly three Stage A governance paths plus five Stage B additions. Runtime delta is exactly the three new C07 sources; test/harness delta exactly the two new C07 test files. No package export or accepted runtime/harness file changed.

| Protected area | Change |
|---|---|
| C01-C06 runtime sources, schemas/enums, canonical identities and accepted evidence | NONE |
| Existing C01-C06/W03 tests and harness | NONE |
| W03 sources, contracts, gate runner, frozen manifest and docs | NONE |
| DB/data model/schema/migrations; W1/W2 hashing/generator/scenario semantics | NONE |
| Production source-evolution verifier, classifier, CI workflow and Verification policy | NONE |
| Dependency metadata / lock / installed SDK | NONE |
| Operational truth, scheduling, procurement, quality release or supplier replacement | NONE |
| Runtime HGT access, future leakage, causal/trust/operational upgrade | NONE |
| W04-C08 replay or other next-checkpoint implementation | NONE |
| Main write, amend/rebase/reset/history rewrite/force push/PR merge/branch deletion | NONE |

Source/blob/tree comparisons and S52 prove frozen upstream/control retention; runtime capability/admission/provider tests prove the bounded C07 surfaces. No test or development material becomes runtime evidence. Frozen artifacts are the only admitted truth; Human decision authority remains intact.

## 11. Stage C publication and completion condition

Only after Stage B #118 overall SUCCESS, create this single path:

```text
docs/w04/checkpoints/c07/W04_C07_R_DEVELOPMENT_ROUND_REPORT.md
```

Commit exact subject `docs(w04-c07): publish investigation summary proof` as a direct child of c86f7af2370f315b8b7310008521f08ceade6d97. Before commit, the staged/HEAD delta must contain only that report. Push normally to the retained feature branch.

This immutable report cannot contain its own not-yet-generated SHA/run. At authoring, Stage C commit/native proof are PENDING. Expected likely route is P / PUBLICATION_EXACT_SHA; actual classifier controls. The completion handoff must verify the new SHA's own Publication/Verification and overall SUCCESS and record actual SHA/run/class. Stage A/B proof cannot substitute for Stage C proof. A non-success terminal Stage C result requires W04_C07_STAGE_C_CI_FAILED with exact job/step/log evidence and no automatic Stage B repair.

The target stop status becomes effective only after that native Stage C proof: W04-C07 IMPLEMENTATION COMPLETE — REVIEW_READY. It does not close the checkpoint.

## Final governance state

```text
C07 MANIFEST STATE:
AUTHORIZED

GPT INDEPENDENT IMPLEMENTATION REVIEW:
PENDING

HUMAN C07 ACCEPTANCE:
PENDING

C07 CLOSEOUT:
NOT AUTHORIZED

W04-C08:
NOT AUTHORIZED

PR #7:
OPEN / DRAFT / UNMERGED

CHECKPOINT CLOSED:
NO

STOP — REVIEW_READY AFTER STAGE C NATIVE PROOF
```
