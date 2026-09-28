# FlowLens Industrial AI — W03-C07 GPT Review Checklist

The later independent GPT review must verify at minimum:

1. C01 evaluation schemas, enums, identity and serialization are unchanged.
2. C07 emits `RecommendationEvaluation` only; `OutcomeEvaluation` is deferred.
3. HGT enters only the protected evaluation plane after packet freeze.
4. Runtime imports remain free of evaluation/HGT.
5. Baseline, scenario, packet and HGT identities/hashes fail closed.
6. Affected-order derivation and pairing rules match the frozen mapping.
7. Supplier and Quality cause direction use paired observable signals.
8. Quality-disposition uncertainty alone is not direction proof.
9. `CAPACITY_PRESSURE` remains `UNKNOWN`.
10. Capacity arrival-only truth is non-observable as contracted.
11. Candidate relevance and recommendation coverage are descriptive only.
12. False positives are baseline-delta aware.
13. Neutral stability is semantic and ignores artifact IDs.
14. The exact metric envelope contains no float or aggregate score.
15. Reason codes and limitations match the frozen vocabularies.
16. Provenance and C01 evaluation identity are canonical.
17. Same/fresh-process replay is deterministic.
18. H1-H38 provide detection, enforcement and evidence.
19. The evaluator has no DB/filesystem/manifest/network/model/tool/runtime-
    subprocess/random/clock/operational capability.
20. C01-C06 and W2 sources/tests remain unchanged and regressions pass.
21. C08/LLM explanation is absent.
22. The report stops at `REVIEW_READY`; C07 is not self-accepted or closed.

Allowed outcomes are:

```text
PASS FOR HUMAN C07 ACCEPTANCE
REPAIR REQUIRED
BLOCKED
```

GPT review must not close C07.
