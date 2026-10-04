# FlowLens Industrial AI — W03-C09 Harness Specification

Each C09 gate requires detection, enforcement, and evidence.

```text
H01 entry branch/head/main/PR/run preflight exact
H02 Human Authorization exact before mutation
H03 C09 manifest schema/version exact
H04 required family set complete and unique
H05 exact pytest function selector existence + frozen expanded-case collection
H06 no critical skip/xfail/xpass
H07 C01 immutable artifact/cross-reference contract proof
H08 C01 runtime HGT/side-effect exclusion proof
H09 C02 future-tail / temporal leakage proof
H10 C02 association/unknown/conflict preservation proof
H11 C03 critical conflicts fail closed
H12 C03 future-tail replay and forbidden-surface proof
H13 C04 HGT-free scenario adapter proof
H14 C04 baseline mutation hard-fail proof
H15 C04 NO_ACTION neutral stability proof
H16 C05 insufficient/unknown abstention proof
H17 C05 tie/partial/nonmonotonic deterministic policy proof
H18 C05 capability/input immutability proof
H19 C06 ACCEPT/REJECT/DEFER remain review-only proof
H20 C06 append-only audit/history proof
H21 C07 real-dataset replay matrix proof
H22 C07 family/HGT-blind packet construction proof
H23 C07 fresh-runtime evaluation/HGT isolation proof
H24 C08 exact bounded provider request proof
H25 C08 prompt injection cannot change behavior proof
H26 C08 grounding failure receives no repair proof
H27 C08 numeric/time/evidence exact-binding proof
H28 PostgreSQL snapshot read-only/replay proof
H29 PostgreSQL C03 handoff zero-mutation proof
H30 scenario-direction smoke proof
H31 W03 AI loop gate emits exact-SHA machine summary
H32 P skips W03 gate; non-P requires W03 gate
H33 Verification gate enforces the W03 gate result
H34 full Quality engineering proof preserved
H35 Docker Compose smoke proof preserved
H36 dependency lock verification preserved
H37 no C01-C08 runtime semantic/source change
H38 no schema/migration/dependency/Docker/runtime change
H39 no live model/provider call or secret read
H40 no operational mutation
H41 no PR merge/draft-to-ready/auto-merge
H42 no C10 work or authorization
```

## Critical regression families

The exact function selectors and expected expanded case counts are frozen in
`specs/c09_gate_manifest.json`: 38 selectors, 10 parameterized selectors, 85
expanded cases total. Parameterized expansion is required; expanded-count drift
is a hard failure.

A successful C09 implementation must show every family PASS on the exact
implementation SHA and then show full Quality + Compose + Verification PASS.

## Adversarial expectations

C09 does not invent new runtime adversarial semantics. It consolidates already
accepted adversarial proofs including:

```text
future evidence
critical conflicts
association -> causality protection
unknown preservation
forbidden runtime surfaces
baseline mutation
candidate/simulation tampering
abstention/tie/partial comparison
Human record overwrite/delete attempts
HGT pre-freeze access
synthetic/circular replay proof
prompt injection
unsupported claims
numeric/temporal rebinding
unrelated-prose evidence misbinding
grounding-repair bypass
```

## Report evidence

The Development Round Report must include:

```text
exact implementation SHA
exact CI run ID and run number
change class
W03 AI loop gate result
per-family summary and test counts
manifest SHA-256
Quality result
Compose result
Verification result
full pytest partition results
Ruff/mypy/lock results
changed-path audit
forbidden-path audit
Git/PR synchronization
known limitations
GPT reviewer questions
```
