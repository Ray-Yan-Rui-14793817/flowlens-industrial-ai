# W03-C04 Authorization Contract

```text
checkpoint_id = W03-C04
contract_version = W03-C04-A-v1
implementation_authorization = APPROVED
product_mode = OFFLINE / SHADOW / HUMAN-IN-THE-LOOP
operational_mutation = PROHIBITED
runtime_hgt = PROHIBITED
```

## Authorized outcome

C04 may implement only the deterministic four-family intervention registry, canonical
`CandidateSet`, frozen W2 stress-probe mappings, a conservative closed-observation simulation
gate, an HGT-free in-memory scenario adapter, independent business diff, frozen raw
measurements, `SimulationResult` / `SimulationBundle`, and the corresponding isolation,
determinism, compatibility and adversarial harness.

The three non-`NO_ACTION` simulations are stress probes for human investigation. They are not
modeled intervention efficacy and must not claim improvement, probability, confidence, root
cause, recommendation or operational benefit. W2 scenario scope is not guaranteed to target
the current order.

## Hard boundaries

- Recommendation, scoring, ranking, `RecommendationRecord`, `DecisionPacket`, C05 capability,
  operational mutation and runtime HGT are outside scope.
- C04 performs no post-C02 database read and has no filesystem, network, model, subprocess,
  random or wall-clock capability.
- Non-`NO_ACTION` simulation is available only when the full baseline satisfies the frozen
  closed-observation gate; otherwise it is `UNAVAILABLE` without a scenario-engine call.
- Legacy W2 business semantics, public API, dataset identity/content behavior and HGT
  identity/hash/payload behavior remain unchanged.
- Direct C04 runtime use of legacy `apply_scenario()` is forbidden.

## Lifecycle

Implementation and harness success may advance C04 only to `REVIEW_READY`. GPT C04 review and
Human C04 acceptance remain pending. C04 is not closed and C05 is not authorized.
