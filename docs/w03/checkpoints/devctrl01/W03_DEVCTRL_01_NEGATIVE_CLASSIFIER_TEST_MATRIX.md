# W03-DEVCTRL-01 Negative Classifier Matrix

Required deterministic cases:

```text
only docs/w03/reports/**
→ P

only docs/CURRENT_STATE.md
→ P

report + CURRENT_STATE
→ P

report + src/flowlens/decision/signals.py
→ I / FULL

CURRENT_STATE + .github/workflows/ci.yml
→ C / FULL

report + docs/sprints/W03_ai_decision_loop.md
→ C / FULL

report + docs/w03/AI_LOOP_CONSTITUTION.md
→ C / FULL

report + tests/test_x.py
→ I / FULL

report + pyproject.toml
→ F / FULL

unknown/new path
→ UNKNOWN / FULL

empty/invalid current-delta boundary
→ UNKNOWN / FULL

commit message begins docs: but source changed
→ I / FULL

*.md under authoritative control path
→ C / FULL
```

Required failure behavior:

```text
classifier exception
→ FULL / fail closed

invalid Git SHA
→ FULL / fail closed

base not ancestor where required
→ FULL / fail closed

publication verifier receives non-P delta
→ FAIL
```
