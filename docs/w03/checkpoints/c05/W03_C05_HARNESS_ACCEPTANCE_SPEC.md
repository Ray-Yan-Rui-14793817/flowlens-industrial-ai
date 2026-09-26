# FlowLens Industrial AI — W03-C05 Harness Acceptance Specification

The C05 harness must detect, enforce and evidence all of the following.

1. **H1 canonical upstream validation:** independently reject tampered C03
   Signals/Diagnosis, C04 CandidateSet/SimulationBundle, binding/hash/result
   relations, NO_ACTION semantics and result payload schemas.
2. **H2 disposition matrix:** prove strict-neutral `NO_ACTION`, every required
   `NO_RECOMMENDATION`, single-family `INVESTIGATION_ONLY`, unique stress
   sensitivity, ties, partial/all-unavailable active comparisons and
   nonmonotonic deferral.
3. **H3 reserved disposition:** `CANDIDATE_RECOMMENDED` is never emitted.
4. **H4 ties:** neither candidate ID nor enum order resolves a semantic tie.
5. **H5 candidate order:** all four IDs occur once; selection/top groups and
   exact-tie serialization behavior match policy.
6. **H6 stress direction:** every metric boundary and all five aggregate classes
   are proven; spread/count measurements have no decision influence.
7. **H7 stress is not efficacy:** `MIXED`/`IMPROVED` active results defer and no
   output claims action benefit, causality, probability or permission.
8. **H8 strict neutral:** capacity UNKNOWN alone is allowed; each specified
   delivery/relevance/material/simulation/uncertainty condition blocks
   `NO_ACTION`; malformed NO_ACTION is a hard failure.
9. **H9 partial degradation:** inactive failure does not block valid active
   selection; partial active comparison defers; all active unavailable/failed
   yields no recommendation.
10. **H10 grounding:** exact reasons, Evidence IDs, uncertainties and limitations
    for every disposition; all Evidence IDs exist in the bundle.
11. **H11 evaluation envelope:** exact component names/categories/order; reject
    missing/extra/duplicate/float/forbidden aggregate semantics.
12. **H12 recommendation replay:** same/fresh-process canonical bytes, identity
    and SHA-256 are stable.
13. **H13 packet assembly:** exact nested objects, references, uncertainty and
    limitation unions, deterministic ID and forbidden-artifact absence.
14. **H14 packet replay:** same/fresh-process canonical bytes, identity and
    SHA-256 are stable.
15. **H15 isolation:** no HGT, future data, DB/SQLAlchemy creation, filesystem,
    network/HTTP, model/LLM, runtime subprocess, random, clock, scenario engine
    or mutation. Test subprocess is only for fresh-process replay.
16. **H16 upstream limitations:** supplier association, quality finality,
    queue/capacity, C03 capacity UNKNOWN, stress-probe and scenario-scope limits
    remain visible.
17. **H17 wording:** fixed bounded wording contains no unsupported causal,
    guarantee, probability, confidence, execution or benefit assertion.
18. **H18 import purity:** fresh `import flowlens.decision` loads no DB,
    SQLAlchemy, scenario, HGT or C05 side-effect capability.
19. **H19 regression:** accepted C01–C04 behavior remains green without weakened,
    skipped or rewritten upstream assertions.

The adversarial pack must cover every attack listed in the standalone task,
including canonical artifact forgery, simulation-shape drift, evaluation
envelope tampering, arbitrary tie breaking, partial/nonmonotonic comparisons,
grounding/limitation removal, capability access and forbidden packet contents.

Required local gates are the focused C05 suite; C04, C03 and C01/C02 decision
regressions; accepted W2/C04 regressions; complete non-integration suite; Ruff;
strict mypy; diff check; and Compose configuration. Guarded PostgreSQL
regression runs only when its existing safety variables are available.
