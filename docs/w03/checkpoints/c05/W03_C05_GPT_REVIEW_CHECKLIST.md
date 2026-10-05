# FlowLens Industrial AI — W03-C05 GPT Review Checklist

Use only after Codex reports `STATUS: REVIEW_READY`.

Verify:

- exact implementation and report SHAs bind to `I / FULL_EXACT_SHA` and
  `P / PUBLICATION_EXACT_SHA` success respectively;
- only authorized implementation/report paths changed and `main` is unchanged;
- C01–C04 artifacts are rebuilt/validated canonically and tampering fails closed;
- no aggregate numeric score/confidence/probability/utility/benefit exists;
- `CANDIDATE_RECOMMENDED` is never emitted;
- strict neutral, abstention, active-family availability, nonmonotonic and tie
  policies match the frozen matrix;
- candidate order contains all four IDs and never resolves a semantic tie;
- stress direction uses only the seven frozen target-order metrics;
- supporting Evidence IDs, uncertainties and limitations are exact and complete;
- RecommendationRecord and DecisionPacket replay in same/fresh processes;
- packet contains exactly the authorized immutable pre-human artifacts;
- no HGT, future leak, post-C02 DB access, scenario execution, IO, model/tool,
  random/clock, mutation or C06+ capability exists;
- all H1–H19 and accepted upstream regressions pass;
- PR #6 remains open, draft and unmerged with auto-merge absent.

Allowed independent-review outcomes are `PASS FOR HUMAN ACCEPTANCE`, `REPAIR
REQUIRED` or `BLOCKED`. The review must not Human-accept, close C05 or authorize
C06.
