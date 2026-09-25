# FlowLens W03-C03 GPT Independent Review Checklist V3

After Codex reaches REVIEW_READY, independently verify:

## Scope / baseline

```text
Human C03 implementation authorization existed
Context Lock was LOCKED before source write
starting W03 baseline was the DEVCTRL closeout SHA
runtime source changes are only authorized C03 files + additive exports
no C01/C02/W2 source/test mutation
no CI/scripts/DEVCTRL mutation
no schema/migration/dependency/Docker change
main unchanged
PR #6 open/draft/unmerged
```

## Signal semantics

```text
exactly 8 SignalTypes
C03_POLICY_V1 in every Signal identity reason set
state rules match signal_policy.json
strict time boundary operators preserved
positive + incomplete scope preserves uncertainty
capacity always UNKNOWN
queue is start-slippage proxy only
delivery is fulfilled/overdue/incomplete-plan/UNKNOWN only
route variance has zero standalone effect
```

## Trust / safety

```text
bundle/context bindings exact
trust partitions checked
critical conflicts block
no runtime DB/HGT/filesystem/network/model
no operational mutation
no association-to-causality upgrade
operational text cannot change logic
future-tail invariance passes
```

## Diagnosis

```text
problem_code precedence exact
claims only ACTIVE/UNKNOWN
claim types exact
statements fixed
all 8 supporting signal IDs
uncertainty union preserves C02
root affected_path only
no recommendation/action/root-cause language
replay deterministic
```

## DEVCTRL proof

Implementation SHA:

```text
class I/FULL
Quality PASS
Compose PASS
Publication SKIPPED
Verification PASS
```

Report SHA:

```text
class P/PUBLICATION
Publication PASS
Verification PASS
Quality SKIPPED
Compose SKIPPED
```

## Review outcomes

```text
PASS FOR HUMAN C03 ACCEPTANCE
REPAIR REQUIRED
BLOCKED
```

GPT review cannot Human-accept or close C03.
