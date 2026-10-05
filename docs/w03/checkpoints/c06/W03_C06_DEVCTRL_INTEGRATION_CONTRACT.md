# FlowLens Industrial AI — W03-C06 Development-Control Integration Contract

The implementation-stage delta is restricted to the exact 21 paths in
`specs/authorized_paths.json`. It must classify `I / FULL_EXACT_SHA` and pass:

```text
Classify change
Quality gate
Docker Compose smoke
Verification gate
```

Publication proof must be skipped for that implementation SHA.

Only after the implementation SHA passes may the report phase change exactly:

```text
docs/w03/reports/W03_C06_R_DEVELOPMENT_ROUND_REPORT.md
docs/CURRENT_STATE.md
```

That commit must classify `P / PUBLICATION_EXACT_SHA`; Publication proof and
Verification must pass while Quality and Compose are skipped.

The workflow uses one normal implementation commit and one normal report
commit, each normally pushed to `origin/feat/w03-ai-decision-loop`. Amend,
rebase, squash, force-push, PR merge, ready transition and auto-merge are
forbidden. No checkpoint auto-advance follows a green gate.
