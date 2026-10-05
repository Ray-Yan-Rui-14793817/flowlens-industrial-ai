# FlowLens Industrial AI — W03-C08 Harness Specification

Each gate defines detection, enforcement, and evidence. Failures reject the LLM
result or fail closed according to the frozen fallback policy.

```text
H01 canonical DecisionPacket acceptance
H02 noncanonical/tampered packet rejection
H03 packet immutability before/after explanation
H04 C07 evaluation/HGT exclusion
H05 deterministic context reduction
H06 prompt hash exactness
H07 exact section vocabulary/order
H08 successful structured model output
H09 evidence ID allowlist enforcement
H10 reason-code allowlist enforcement
H11 invented evidence rejection
H12 invented candidate rejection
H13 recommendation drift rejection
H14 associative-to-causal upgrade rejection
H15 UNKNOWN resolution rejection
H16 unsupported numeric claim rejection
H17 probability/confidence/guarantee rejection
H18 simulation-efficacy overclaim rejection
H19 quality-release forbidden inference rejection
H20 procurement-allocation forbidden inference rejection
H21 prompt injection resistance
H22 tool/database/filesystem/network request resistance
H23 provider timeout fallback
H24 provider refusal fallback
H25 provider exception fallback
H26 schema-invalid first call -> one repair
H27 schema-invalid repair -> degraded fallback
H28 grounding failure -> no repair, degraded fallback
H29 model disabled -> deterministic template
H30 API key absent -> deterministic template
H31 max provider calls <= 2
H32 SDK automatic retries disabled
H33 no provider tools configured
H34 final C01 ExplanationRecord identity valid
H35 referenced evidence/source provenance complete
H36 packet limitations preserved
H37 human_review_boundary deterministic
H38 same input fallback byte deterministic
H39 same input successful LLM semantically reproducible contract
H40 C01-C07 regressions
H41 W2 regressions
H42 Ruff
H43 strict mypy
H44 dependency lock
H45 Docker Compose configuration
H46 no operational/database/schema/migration change
```

Fake providers expose call count and received request payload so the harness can
prove no tools, hidden inputs, or unbounded retries. No live provider call is
required for CI.
