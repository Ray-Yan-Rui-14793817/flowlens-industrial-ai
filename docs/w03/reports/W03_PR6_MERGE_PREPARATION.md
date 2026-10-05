# FlowLens Industrial AI — W03 PR #6 Merge Preparation

## 1. Authority and locked context

```text
TASK: POST-W03 PR #6 MERGE / POST-MERGE VERIFICATION
CONTEXT LOCK: LOCKED
context_lock_status = LOCKED
ENTRY BRANCH: feat/w03-ai-decision-loop
ENTRY HEAD: a24e2e0587f11114edd5718eb10081797e303087
MAIN: 9d18ddde9fe933952a2661ee1419f13c8577605d
GPT MERGE REVIEW: PASS FOR HUMAN W03 PR #6 MERGE AUTHORIZATION
HUMAN MERGE AUTHORIZATION: APPROVED
ACTIVE PRODUCT OWNER GATE: W03 PR #6 MERGE AUTHORIZATION: APPROVED
POST-W03 IMPLEMENTATION: NOT AUTHORIZED
```

The active Product Owner request supplies the exact Human gate. The supplied
Context Lock is projected here as LOCKED before any other authorized write.
This is a governance/repository-projection and guarded integration task.
W03 product/runtime semantics and C01-C10 accepted evidence are frozen.

ZIP SHA-256:
`1874e5f04e49178f1c08c88a4cd5b51ed57289a1d89aaa4d9e126d192c8da10f`.
All 13 payload hashes match SHA256SUMS.txt. The standalone execution task is
byte-identical to the checksummed package task. Locked payload identities:

| Package path | SHA-256 |
|---|---|
| `POST_W03_CODEX_MERGE_EXECUTION_PROMPT_V1.txt` | `9da972fa27add43be30d25bea575c85722bc1d1d58f48fcbde2397c1869c7851` |
| `POST_W03_CODEX_MERGE_EXECUTION_TASK_V1.md` | `b38d2d8c2385ec813806b99d9cb124835bbcfd2a1705e79d42342fca391ea92b` |
| `POST_W03_GPT_NEXT_PHASE_MERGE_AUTHORIZATION_REVIEW_R1.md` | `02339c681606f8f272dd3c806af80b6a79633d9e8c91ab52aa1fdd331a308dc6` |
| `POST_W03_HUMAN_MERGE_AUTHORIZATION.md` | `1fee04247bfb240c284a7f3a1d5f7c80d5b4fc03ef638c510ecd6fcb8ff709fe` |
| `POST_W03_MERGE_CONTEXT_LOCK.md` | `58da79c5d0c1fb02d78ce61c05f58c5dae4bcf6405cbf417ccf0df20583e8018` |
| `POST_W03_NEXT_PHASE_SELECTION_FRAMEWORK.md` | `788529f41db62366d002bd6315688c5eec13fbba4e56552d59162542d97b3969` |
| `POST_W03_PACKAGE_INDEX.md` | `0d01f9fd673b74a203272c91f5f51a8765d0a80ea4aca87b9146e5eef4af4752` |
| `POST_W03_PR6_FINAL_BODY_TEMPLATE.md` | `62dde451f76a416b05091356aac49176069670424750040391ff5074b81bab81` |
| `POST_W03_PR6_MERGE_AND_POST_MERGE_VERIFICATION_CONTRACT.md` | `6db2c60ff1db3e30c9a88b52af889159aee44fb90872e625909c66afdce16c46` |
| `POST_W03_PR6_MERGE_PREPARATION_REPORT_TEMPLATE.md` | `de134df6d70655e3322c46593af8bf6afe85e6119aa5554bf8b6e50d445d0e29` |
| `POST_W03_RECOVERY_PROMPT_V1.txt` | `71be474c75ff0bd15dfa8c5ae68adde5fd4c74998897e59aef9842f664f93500` |
| `specs/authorized_paths.json` | `95fe451fd5167140f8545214ab786d3b97baf5a28798d4cbb681b3f06f91973e` |
| `specs/entry_facts.json` | `cf8f18e1e5134c3f61cc0553fb9129aaa402d51696b243e17b9d9dc3882d0320` |

Allowed sources: checksummed merge package, active Human gate, accepted repository
evidence and read-only Git/GitHub observations. Protected boundaries: no source/
tests/workflows/scripts/migrations/apps/dependency/lock/Docker/checkpoint writes,
no C01-C10 semantic changes, no history rewrite, no live provider/secret/runtime
HGT/future leakage/operational mutation, no branch deletion, no next-phase
implementation or phase selection. Main remains read-only until the authorized
GitHub merge commit. Expected delta: exactly Section 5's seven paths plus the
three explicitly authorized PR metadata/integration actions.

## 2. Mandatory read-only entry preflight

Observed on 2026-10-05 (Asia/Shanghai), before any mutation:

| Entry fact | Verified value |
|---|---|
| Repository | Ray-Yan-Rui-14793817/flowlens-industrial-ai |
| Branch | feat/w03-ai-decision-loop |
| Local / tracking / direct remote / PR #6 head | a24e2e0587f11114edd5718eb10081797e303087 |
| Local / tracking / direct remote main; merge base | 9d18ddde9fe933952a2661ee1419f13c8577605d |
| Feature ahead/behind main | 54/0 |
| Worktree / staging | CLEAN / CLEAN |
| Tracking ahead/behind | 0/0 |
| PR #6 | OPEN / DRAFT / NOT MERGED |
| Mergeability | CLEAN; mergeable true; all checks passed; no base conflicts |
| Auto-merge | ABSENT; repository setting disabled |
| Entry CI | Run #84 / 37254705531 / completed / success |
| Merge commits allowed | YES |
| Squash / rebase methods available | YES; use forbidden by this task |
| Automatically delete head branches | DISABLED |

These match specs/entry_facts.json. Repository metadata, exact commit-associated
run, direct remote refs and GitHub PR/settings pages supplied the observations.
No reset, rebase, amend, cherry-pick, local merge, force-push or silent contract
adaptation occurred during preflight.

## 3. Effective W03 closeout evidence

| Accepted evidence | Exact SHA | CI |
|---|---|---|
| C10 implementation | 57dd12db02b5650b5c04e1d1007ffc22810a74a1 | Run #81 / 37224461190 / PASS / C / FULL_EXACT_SHA |
| C10 readiness publication | dade594d3ba67825775577f46408689b733f089d | Run #82 / 37227376986 / PASS / P / PUBLICATION_EXACT_SHA |
| W03 closeout control | 85c5e5ec19eb6db7a2921656138a9c9817702bcc | Run #83 / 37252248950 / PASS / UNKNOWN / FULL_EXACT_SHA |
| W03 final publication | a24e2e0587f11114edd5718eb10081797e303087 | Run #84 / 37254705531 / PASS / P / PUBLICATION_EXACT_SHA |

C10 readiness: A01-A10 10/10 EVIDENCE_READY; H01-H34 34/34 PASS.
GPT C10 Review R1 passed for Human business acceptance review. The Product Owner
supplied W03-C10 HUMAN ACCEPTANCE: ACCEPTED. K01-K20 passed 20/20 on the closeout
control. Final publication and synchronization passed, making C10/W03 closure
effective. W03 is CLOSED / VERIFIED / GITHUB SYNCHRONIZED; C10 is CLOSED.

Accepted v0 limitations remain: synthetic evidence is not a real enterprise outcome;
stress probes do not prove remedy efficacy; investigation/abstention is not action
authority; Human artifact review is not production UX; explanation grammar is
constrained; OutcomeEvaluation, production deployment and operational integration
remain outside W03.

## 4. Current-status normalization

README, AGENTS, Context Index, Sprint current status and CURRENT_STATE project
effective W03/C10 closure, supplied GPT merge review PASS, Human merge authorization
APPROVED, and PR #6 merge AUTHORIZED / PENDING PRE-MERGE FULL PROOF.
Post-W03 implementation remains NOT AUTHORIZED.

W1/W2 content, AGENTS invariant/routing sections, Context Index authority/runtime
rules, Sprint Sections 1-20 and historical Section 22, and CURRENT_STATE historical
Sections 1-60 are preserved. Add CURRENT_STATE Section 61 and publish the supplied
GPT merge review faithfully. Historical pending/unauthorized wording continues to
describe its original checkpoint; only current-status surfaces change.

## 5. Exact seven-path control scope

```text
README.md
AGENTS.md
docs/context/CONTEXT_INDEX.md
docs/sprints/W03_ai_decision_loop.md
docs/CURRENT_STATE.md
docs/w03/reports/POST_W03_GPT_NEXT_PHASE_MERGE_AUTHORIZATION_REVIEW_R1.md
docs/w03/reports/W03_PR6_MERGE_PREPARATION.md
```

Create exactly one normal child commit of the entry head, then push normally.
No other repository path is authorized. Accepted checkpoint packages, reports and
Human acceptance dimension rows are unchanged.

## 6. Pre-merge exact-SHA full CI

```text
MERGE PREPARATION SHA: PENDING ON THIS COMMIT
PRE-MERGE FULL PROOF: PENDING ON THIS COMMIT
EXPECTED CLASS: UNKNOWN / FULL_EXACT_SHA
REQUIRED CLASSIFY / QUALITY / COMPOSE / W03 / VERIFICATION: PASS
REQUIRED PUBLICATION: SKIPPED
```

README is intentionally outside classifier allowlists. UNKNOWN must route to full
proof without classifier/workflow changes. Actual immutable preparation SHA/run/id
are supplied after push in the final handoff. No PR-body or ready-state mutation
may occur before this exact head's full proof passes. Required failure/skip: STOP.

## 7. F01-F10 / 38 / 85 proof

Require all F01-F10, 38 selectors and 85 expanded cases on the exact preparation
SHA and again on the exact merge-commit main SHA. Run #83 proves the accepted
closeout control and cannot substitute for either new full-proof run.
New preparation proof: PENDING ON THIS COMMIT. Gate manifest, families, selectors,
cases and runner remain unchanged.

## 8. PR body, title and ready-state plan

After pre-merge full proof, replace PR #6 body using the frozen final-body template
with its sole SHA placeholder resolved to the actual preparation commit.
Keep title: `feat(w03): build industrial AI decision loop foundation`.

Then mark ready, re-read PR and require exact preparation head, exact old-main base,
OPEN / draft FALSE / NOT MERGED, CLEAN mergeability, absent auto-merge and exact
normalized body. Empty GitHub review lists do not infer reviewer decisions.
Explicit Product Owner authorization is the governing Human decision.

## 9. Merge-commit-only integration

```text
PR #6 MERGE: AUTHORIZED ONLY AFTER FULL PROOF
MERGE METHOD: GITHUB MERGE COMMIT ONLY
EXPECTED MAIN: 9d18ddde9fe933952a2661ee1419f13c8577605d
EXPECTED HEAD: EXACT MERGE-PREPARATION SHA
MERGE SHA: UNKNOWN UNTIL AUTHORIZED MERGE
```

Re-check head and base immediately before merge; guard merge API with exact head.
Verify exactly two parents: old main first, exact preparation head second.
Squash, rebase merge, auto-merge, local merge and branch deletion are forbidden.
No future merge SHA or completion is claimed here.

## 10. Exact post-merge main CI

Require the exact merge commit's own main push CI: UNKNOWN / FULL_EXACT_SHA;
Classify, Quality, Docker Compose, W03 AI loop gate and Verification PASS;
Publication SKIPPED; F01-F10 / 38 / 85 PASS.
Pre-merge/ready-event proof cannot substitute for main push proof.

Failure: STOP and report; no uncontracted main hotfix.
After PASS, require local main = tracking main = direct remote main = PR #6 merge
commit, CLEAN tree/staging, main tracking 0/0 and CLOSED / MERGED PR state.

## 11. Branch retention and next-phase boundary

Retain feature branch at exact preparation head. Post-merge verification is read-only
apart from normal fetch and fast-forward synchronization of local main.
No post-merge publication commit or feature-branch deletion is authorized.

```text
GPT MERGE REVIEW: PASS FOR HUMAN AUTHORIZATION
HUMAN MERGE AUTHORIZATION: APPROVED
PRE-MERGE FULL PROOF: PENDING ON THIS COMMIT
PR #6 MERGE: AUTHORIZED ONLY AFTER FULL PROOF
POST-W03 IMPLEMENTATION: NOT AUTHORIZED
NEXT: PR #6 MERGE COMMIT + POST-MERGE MAIN VERIFICATION
STATUS: W03_MERGE_PREPARATION_PENDING_FULL_PROOF
```

Only after actual merge and successful exact main push proof may final handoff state
W03_MERGED_POST_MERGE_VERIFIED, with next:
GPT POST-W03 CAPABILITY-GAP / SPRINT-SELECTION / ARCHITECTURE CONTRACT REVIEW.
No next product phase is selected or implemented here.
