# FlowLens Industrial AI — W03-C05 Development-Control Integration Contract

The authorized sequence is:

```text
implementation commit
→ normal push
→ I / FULL_EXACT_SHA PASS
→ W03_C05_R_DEVELOPMENT_ROUND_REPORT.md + docs/CURRENT_STATE.md
→ report commit
→ normal push
→ P / PUBLICATION_EXACT_SHA PASS
→ final Git/GitHub synchronization
→ REVIEW_READY
→ STOP
```

Implementation proof requires Classify, Quality, Docker Compose and Verification
success with Publication skipped. Report proof requires Classify, Publication
and Verification success with Quality and Compose skipped.

Before implementation commit, verify a locked C05 Context Lock, authorized paths
only, no forbidden path, intact C04 closeout and no C06 source. Before final
handoff, local/tracking/direct-remote/PR heads must match, the tree must be clean
and 0 ahead/behind, `main` must remain frozen, and PR #6 must remain open, draft
and unmerged with auto-merge absent.

No amend, rebase, squash, force-push, merge, draft-to-ready, CI/control-plane
edit, self-review, Human acceptance, C05 closeout or C06 work is authorized.
