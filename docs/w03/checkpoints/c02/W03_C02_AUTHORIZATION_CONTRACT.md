# FlowLens Industrial AI — W03-C02-A Implementation Authorization Contract

**Task:** `W03-C02-A`  
**Checkpoint:** `W03-C02 — StateSnapshot + DecisionContext + Semantic Trust`  
**GPT decision:** `PASS FOR HUMAN IMPLEMENTATION AUTHORIZATION`  
**Human implementation authorization:** `PENDING`

## 1. Objective

Implement the trusted observation layer over the frozen C01 contract kernel.

Authorized runtime result:

```text
DecisionRun
→ read-only PostgreSQL source projection
→ StateSnapshot
→ EvidenceBundle
→ Semantic Trust
→ deterministic C02 observation-state derivations
→ EvidenceConflict
→ DecisionContext
```

## 2. Frozen baseline

```text
branch:
feat/w03-ai-decision-loop

C01 closeout SHA:
c626126a81fe07b5d1f670deaeaadc809f6bea55

main:
9d18ddde9fe933952a2661ee1419f13c8577605d

Draft PR:
#6 / OPEN / DRAFT / NOT MERGED / AUTO-MERGE DISABLED

C01 final publication CI:
Run #38 / 35987268646 / SUCCESS
```

Any starting drift requires a safe stop.

## 3. Frozen contracts

Authoritative C02 contracts:

```text
W03_C02_ARCHITECTURE_SEMANTIC_FREEZE.md
W03_C02_SOURCE_FIELD_SNAPSHOT_MATRIX.md
W03_C02_EVIDENCE_TRUST_FRESHNESS_MATRIX.md
W03_C02_DECISION_CONTEXT_DERIVATION_CONTRACT.md
W03_C02_POSTGRES_SNAPSHOT_ISOLATION_CONTRACT.md
W03_C02_HARNESS_ACCEPTANCE_SPEC.md
```

Higher authority remains the G0 Constitution/Sprint/Semantic Trust/Context/Tool/Harness
contracts and the frozen C01 kernel.

## 4. Important architecture split

C01 has an explicit regression guard that importing/scanning `flowlens.decision`
must not introduce SQLAlchemy/database imports.

C02 therefore freezes:

```text
PURE DECISION CORE
!=
POSTGRESQL ADAPTER
```

Pure decision modules:

```text
src/flowlens/decision/snapshot.py
src/flowlens/decision/temporal.py
src/flowlens/decision/evidence.py
src/flowlens/decision/trust.py
src/flowlens/decision/derivations.py
src/flowlens/decision/context.py
```

PostgreSQL adapter:

```text
src/flowlens/db/decision_snapshot.py
```

`flowlens.decision` MUST remain importable without loading:

```text
flowlens.db
sqlalchemy
flowlens.data.scenarios
openai
```

The DB adapter may import SQLAlchemy and the pure decision contracts.

The pure decision package may NOT import the DB adapter.

## 5. Authorized source files

Create:

```text
src/flowlens/decision/snapshot.py
src/flowlens/decision/temporal.py
src/flowlens/decision/evidence.py
src/flowlens/decision/trust.py
src/flowlens/decision/derivations.py
src/flowlens/decision/context.py
src/flowlens/db/decision_snapshot.py
```

May modify:

```text
src/flowlens/decision/__init__.py
```

only for additive DB-free C02 exports.

Forbidden C01 kernel modification:

```text
src/flowlens/decision/contracts.py
src/flowlens/decision/enums.py
src/flowlens/decision/primitives.py
src/flowlens/decision/serialization.py
```

If these prove insufficient:

```text
STOP
C01_CONTRACT_BLOCKER
```

Do not patch them silently.

## 6. Authorized tests

Create:

```text
tests/test_decision_snapshot.py
tests/test_decision_temporal.py
tests/test_decision_evidence.py
tests/test_decision_context.py
tests/integration/test_decision_snapshot_database.py
```

Existing C01 tests are regression gates and MUST NOT be edited to accommodate C02.

## 7. Authorized repository documentation

Publish under:

```text
docs/w03/checkpoints/c02/
```

the supplied C02 authoritative documents, Context Lock and Human authorization record.

After exact implementation-SHA CI succeeds, create:

```text
docs/w03/reports/W03_C02_R_DEVELOPMENT_ROUND_REPORT.md
```

`docs/CURRENT_STATE.md` may be updated only in the separate report/evidence commit.

## 8. Runtime tool permissions

C02 adds exactly one DB-capable runtime capability:

```text
PostgreSQL Snapshot Reader
side effect = READ_ONLY
transaction = REPEATABLE READ / READ ONLY
```

Pure deterministic capabilities:

```text
Snapshot Assembler
Temporal Projector
Evidence Builder
Semantic Trust Classifier
C02 Derivation Engine
DecisionContext Builder
```

Runtime:

```text
LLM ACCESS = NONE
HGT ACCESS = NONE
FILESYSTEM ACCESS = NONE
NETWORK ACCESS = NONE
OPERATIONAL WRITE = NONE
```

## 9. Required behavior

Implement exactly the frozen:

```text
source-field whitelist
available_at rules
observed_at rules
raw-status exclusion
SQL future masking
order-centric graph
associative material/PO/inventory semantics
inventory freshness
quality unknown policy
uncertainty registry
derivation registry
conflict registry
DecisionContext schema/identity/partition rules
future-tail normalized metamorphic harness
```

## 10. No-go boundary

Do not implement:

```text
signal thresholds
Signal Engine
Diagnosis Engine
risk scoring
route anomaly
candidate registry
scenario runtime adapter
counterfactual simulation
recommendation/scoring
HumanDecision persistence
HGT evaluator
LLM
RAG
agent
tool-calling model
API/worker behavior
schema/migration
dependency changes
W2 hash/scenario changes
```

## 11. Additional current-W2 assumption

Current W2 generated Product/Customer/Supplier/WorkCenter rows use `active_to=None`.

C02 v1 does not freeze historical semantics for a non-null `active_to`.

If implementation/testing discovers a current authorized dataset in which relevant
non-null `active_to` materially changes decision-time semantics:

```text
STOP
TYPE_C_SEMANTIC_DECISION
```

Do not invent an effective-end knowledge policy.

## 12. Failure classes

### Type A — engineering defect

Examples:

```text
typing
query construction
sorting
serialization
validation
fixture defect
lint
```

Codex may auto-repair within authorized scope.

### Type B — contract conflict

Examples:

```text
C01 schema cannot represent frozen C02 behavior
W2 schema contradicts source matrix
C02 contract documents materially disagree
```

Stop.

### Type C — semantic/product decision

Examples:

```text
new freshness threshold
new relationship type
new trust upgrade
new unknown policy
active_to historical meaning
new derivation
```

Stop and ask GPT/Human.

### Type D — safety violation

```text
HGT runtime access
future leakage
operational mutation
unauthorized DB/tool access
protected material exposure
```

Abort; not review-ready.

## 13. Acceptance

C02 can reach `REVIEW_READY` only when:

```text
Context Lock PASS
focused C02 tests PASS
C01 regression PASS
non-integration regression PASS
PostgreSQL C02 integration PASS on CI
Ruff PASS
strict mypy PASS
git diff --check PASS
Compose config PASS
schema/migrations unchanged
dependencies unchanged
W1/W2/C01 frozen sources preserved
HGT runtime access NONE
operational mutation NONE
future-tail metamorphic PASS
exact implementation SHA CI PASS
Development Round Report created
```

Maximum status:

```text
GPT REVIEW = PENDING
HUMAN ACCEPTANCE = PENDING
C02 CLOSED = NO
C03 AUTHORIZED = NO
STATUS = REVIEW_READY
```
