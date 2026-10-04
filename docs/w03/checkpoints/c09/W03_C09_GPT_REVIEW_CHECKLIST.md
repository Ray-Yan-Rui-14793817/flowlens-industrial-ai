# FlowLens Industrial AI — W03-C09 GPT Review Checklist

Independent post-implementation review should verify:

- exact reviewed implementation SHA and exact-SHA GitHub Actions run;
- implementation class is `I / FULL_EXACT_SHA` unless the actual authorized
  delta legitimately classifies higher-risk, never lower-risk;
- `W03 AI loop gate` exists as a separate named job;
- the job runs for non-P and is skipped for P;
- final `Verification gate` requires the W03 job with the frozen truth table;
- existing Quality, Compose, Publication proof and classifier semantics remain
  intact;
- frozen V1.1 family set, exact function selectors, per-selector expanded counts, family counts, and global 85-case total match the amended GPT contract;
- no critical target is missing, renamed, skipped, xfailed, deselected, or
  replaced by a weaker test;
- machine-readable summary is exact-SHA and manifest-hash bound;
- C01-C08 accepted semantic proofs remain PASS;
- PostgreSQL semantic subset proves read-only/replay/zero-mutation behavior;
- no live OpenAI call, provider secret, new dependency, new action, or new image
  is introduced;
- no `src/` runtime change exists;
- C08 prompt/schema/provider/model controls are unchanged;
- no C01-C07 semantic behavior changed;
- no Week 2 scenario/data/HGT behavior changed;
- no schema/migration/API/worker/Docker runtime change exists;
- no operational mutation exists;
- no C10 implementation or business acceptance is claimed;
- Development Round Report follows the frozen W03 reporting boundary;
- Codex ends at `PENDING GPT REVIEW / PENDING HUMAN ACCEPTANCE / C09 CLOSED: NO`.
