# W03-C04 Development-Control Integration Contract

The authorized sequence is:

```text
implementation commit
  -> normal push
  -> I / FULL_EXACT_SHA PASS
  -> Development Round Report + CURRENT_STATE
  -> report commit
  -> normal push
  -> P / PUBLICATION_EXACT_SHA PASS
  -> final local/tracking/direct-remote synchronization
  -> REVIEW_READY
  -> STOP
```

The implementation exact-SHA proof must execute the complete focused C04 harness, frozen C03,
C01/C02 decision and W2 scenario regressions, full non-integration tests, Ruff, mypy,
`git diff --check`, Compose validation, and the authorized guarded PostgreSQL regression when
safely available.

The report commit may modify only:

```text
docs/w03/reports/W03_C04_R_DEVELOPMENT_ROUND_REPORT.md
docs/CURRENT_STATE.md
```

No amend, rebase, squash, force-push, merge, ready-for-review transition, CI/control-plane edit,
Human acceptance, checkpoint closeout or C05 work is authorized.
