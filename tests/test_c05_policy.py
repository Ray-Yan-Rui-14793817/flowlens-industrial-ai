"""Golden categorical policy and stress-comparison tests for W03-C05."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from flowlens.decision.c04_registry import build_candidate_set
from flowlens.decision.c04_simulation import build_simulation_bundle
from flowlens.decision.c05_evaluation import (
    aggregate_stress_effect,
    compare_metric,
    evaluate_c05,
)
from flowlens.decision.c05_policy import (
    DECISION_METRIC_DIRECTIONS,
    MetricEffect,
    StressEffect,
)
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import (
    CandidateSet,
    DecisionRun,
    DiagnosisRecord,
    EvidenceBundle,
    SignalBundle,
    SimulationBundle,
    SimulationResult,
    StateSnapshot,
)
from flowlens.decision.diagnosis import evaluate_c03
from flowlens.decision.enums import (
    InterventionFamily,
    RecommendationDisposition,
    SimulationStatus,
)
from flowlens.decision.primitives import ArtifactProvenance, Limitation, NamedValue, ScalarValue
from flowlens.decision.serialization import derive_artifact_id
from test_c03_signals import CASES, Record, _records_for_case, build_c03_fixture
from test_decision_snapshot import AS_OF, make_run


@dataclass(frozen=True, slots=True)
class C05Fixture:
    run: DecisionRun
    snapshot: StateSnapshot
    evidence: EvidenceBundle
    context: DecisionContext
    signals: SignalBundle
    diagnosis: DiagnosisRecord
    candidates: CandidateSet
    simulations: SimulationBundle

    def args(
        self,
    ) -> tuple[
        DecisionRun,
        StateSnapshot,
        EvidenceBundle,
        DecisionContext,
        SignalBundle,
        DiagnosisRecord,
        CandidateSet,
        SimulationBundle,
    ]:
        return (
            self.run,
            self.snapshot,
            self.evidence,
            self.context,
            self.signals,
            self.diagnosis,
            self.candidates,
            self.simulations,
        )


def neutral_records() -> list[Record]:
    queue_inactive = next(case for case in CASES if case["case_id"] == "C03-G21")
    records = [
        (entity, record_id, dict(fields))
        for entity, record_id, fields in _records_for_case(queue_inactive)
        if entity != "fact_rework"
    ]
    for entity, _, fields in records:
        if entity == "fact_purchase_order":
            fields["promised_receipt_at"] = datetime(2026, 1, 14, tzinfo=UTC)
            fields["actual_receipt_at"] = datetime(2026, 1, 14, tzinfo=UTC)
        elif entity == "fact_quality_inspection":
            fields.update(
                passed_quantity=10,
                failed_quantity=0,
                result="PASS",
                defect_category=None,
                severity=None,
            )
        elif entity == "fact_delivery":
            fields["delivered_quantity"] = 10
    return records


def records_for_active(family: InterventionFamily) -> list[Record]:
    records = neutral_records()
    for entity, _, fields in records:
        if entity == "fact_sales_order":
            fields["promised_delivery_at"] = datetime(2026, 1, 18, tzinfo=UTC)
        if entity == "fact_delivery":
            fields["delivered_quantity"] = 4
        if family is InterventionFamily.SUPPLIER_INTERVENTION and entity == "fact_purchase_order":
            fields["promised_receipt_at"] = datetime(2026, 1, 18, tzinfo=UTC)
            fields["actual_receipt_at"] = datetime(2026, 1, 22, tzinfo=UTC)
        if (
            family is InterventionFamily.QUALITY_INTERVENTION
            and entity == "fact_quality_inspection"
        ):
            fields.update(
                passed_quantity=7,
                failed_quantity=3,
                result="FAIL",
                defect_category="SURFACE",
                severity="MEDIUM",
            )
        if family is InterventionFamily.CAPACITY_INTERVENTION and entity == "fact_operation":
            fields["actual_start_at"] = datetime(2026, 1, 20, tzinfo=UTC)
    return records


def make_fixture(
    records: list[Record] | None = None,
) -> C05Fixture:
    snapshot, evidence, context = build_c03_fixture(records)
    run = make_run(
        AS_OF,
        dataset_version=snapshot.dataset_version,
        dataset_hash=snapshot.dataset_hash,
    )
    signals, diagnosis = evaluate_c03(evidence, context)
    candidates = build_candidate_set(evidence, context, signals, diagnosis)
    simulations = build_simulation_bundle(
        run, snapshot, evidence, context, signals, diagnosis, candidates
    )
    return C05Fixture(
        run,
        snapshot,
        evidence,
        context,
        signals,
        diagnosis,
        candidates,
        simulations,
    )


def _measurements(
    baseline: tuple[NamedValue, ...], effect: StressEffect
) -> tuple[NamedValue, ...]:
    changes: dict[str, ScalarValue] = {}
    delivered = next(item.value for item in baseline if item.name == "target_delivered_quantity")
    remaining = next(item.value for item in baseline if item.name == "target_remaining_quantity")
    assert type(delivered) is int and type(remaining) is int
    if effect is StressEffect.WORSENED:
        changes["target_delivered_quantity"] = delivered - 1
    elif effect is StressEffect.IMPROVED:
        changes["target_delivered_quantity"] = delivered + 1
    elif effect is StressEffect.MIXED:
        changes["target_delivered_quantity"] = delivered - 1
        changes["target_remaining_quantity"] = max(remaining - 1, 0)
    elif effect is not StressEffect.UNCHANGED:
        raise AssertionError(f"unsupported synthetic effect: {effect}")
    return tuple(
        NamedValue(name=item.name, value=changes.get(item.name, item.value), unit=item.unit)
        for item in baseline
    )


def with_simulations(
    fixture: C05Fixture,
    states: dict[InterventionFamily, tuple[SimulationStatus, StressEffect]],
) -> C05Fixture:
    candidate_by_id = {item.candidate_id: item for item in fixture.candidates.candidates}
    family_by_id = {item.candidate_id: item.family for item in fixture.candidates.candidates}
    original_by_id = {item.candidate_id: item for item in fixture.simulations.results}
    no_action_id = next(
        item.candidate_id
        for item in fixture.candidates.candidates
        if item.family is InterventionFamily.NO_ACTION
    )
    baseline = original_by_id[no_action_id].measurements
    results: list[SimulationResult] = []
    for candidate_id in sorted(candidate_by_id):
        candidate = candidate_by_id[candidate_id]
        family = family_by_id[candidate_id]
        if family not in states:
            results.append(original_by_id[candidate_id])
            continue
        status, effect = states[family]
        measurements = (
            _measurements(baseline, effect)
            if status is SimulationStatus.SUCCEEDED
            else ()
        )
        scenario_id = (
            f"scenario-{family.value.lower()}"
            if status is SimulationStatus.SUCCEEDED
            else None
        )
        scenario_hash = "b" * 64 if status is SimulationStatus.SUCCEEDED else None
        limitations = candidate.limitations
        if status is SimulationStatus.FAILED:
            limitations = tuple(
                sorted(
                    (
                        *limitations,
                        Limitation(
                            code="C04_SCENARIO_EXECUTION_FAILED",
                            message=(
                                "The deterministic scenario engine failed after its "
                                "preconditions passed."
                            ),
                        ),
                    ),
                    key=lambda item: (item.code, item.message),
                )
            )
        elif status is SimulationStatus.UNAVAILABLE:
            limitations = tuple(
                sorted(
                    (
                        *limitations,
                        Limitation(
                            code="C04_SIMULATION_BASELINE_NOT_SUPPLIED",
                            message=(
                                "No already-materialized in-memory simulation baseline was "
                                "supplied."
                            ),
                        ),
                    ),
                    key=lambda item: (item.code, item.message),
                )
            )
        identity = {
            "run_id": fixture.run.run_id,
            "candidate_id": candidate_id,
            "status": status,
            "baseline_snapshot_id": fixture.snapshot.snapshot_id,
            "baseline_snapshot_hash": fixture.snapshot.snapshot_hash,
            "scenario_id": scenario_id,
            "scenario_hash": scenario_hash,
            "affected_entities": (),
            "measurements": measurements,
        }
        results.append(
            SimulationResult(
                simulation_id=derive_artifact_id(
                    "simulation-result", "simulation-result.v1", identity
                ),
                schema_version="simulation-result.v1",
                run_id=fixture.run.run_id,
                candidate_id=candidate_id,
                status=status,
                baseline_snapshot_id=fixture.snapshot.snapshot_id,
                baseline_snapshot_hash=fixture.snapshot.snapshot_hash,
                scenario_id=scenario_id,
                scenario_hash=scenario_hash,
                affected_entities=(),
                measurements=measurements,
                limitations=limitations,
                provenance=ArtifactProvenance(
                    producer="flowlens.decision.c04_simulation",
                    producer_version="w03-c04-scenario-adapter-v1",
                    input_artifact_ids=tuple(
                        sorted(
                            (
                                fixture.run.run_id,
                                fixture.snapshot.snapshot_id,
                                candidate_id,
                            )
                        )
                    ),
                    source_refs=candidate.provenance.source_refs,
                    contract_versions=original_by_id[no_action_id].provenance.contract_versions,
                    implementation_sha=None,
                ),
            )
        )
    ordered = tuple(sorted(results, key=lambda item: (item.candidate_id, item.simulation_id)))
    bundle_identity = {
        "run_id": fixture.run.run_id,
        "snapshot_id": fixture.snapshot.snapshot_id,
        "candidate_simulation_ids": tuple(
            (item.candidate_id, item.simulation_id) for item in ordered
        ),
    }
    simulations = SimulationBundle(
        simulation_bundle_id=derive_artifact_id(
            "simulation-bundle", "simulation-bundle.v1", bundle_identity
        ),
        schema_version="simulation-bundle.v1",
        run_id=fixture.run.run_id,
        snapshot_id=fixture.snapshot.snapshot_id,
        results=ordered,
        provenance=ArtifactProvenance(
            producer="flowlens.decision.c04_simulation",
            producer_version="w03-c04-scenario-adapter-v1",
            input_artifact_ids=tuple(
                sorted(
                    (
                        fixture.run.run_id,
                        fixture.snapshot.snapshot_id,
                        fixture.candidates.candidate_set_id,
                        *(item.simulation_id for item in ordered),
                    )
                )
            ),
            source_refs=fixture.candidates.provenance.source_refs,
            contract_versions=fixture.simulations.provenance.contract_versions,
            implementation_sha=None,
        ),
    )
    return C05Fixture(
        fixture.run,
        fixture.snapshot,
        fixture.evidence,
        fixture.context,
        fixture.signals,
        fixture.diagnosis,
        fixture.candidates,
        simulations,
    )


@pytest.mark.parametrize("name", tuple(DECISION_METRIC_DIRECTIONS))
def test_each_metric_direction_and_none_semantics(name: str) -> None:
    lower_worse = DECISION_METRIC_DIRECTIONS[name] == "LOWER"
    worse = 9 if lower_worse else 11
    better = 11 if lower_worse else 9
    assert compare_metric(name, 10, worse) is MetricEffect.WORSE
    assert compare_metric(name, 10, 10) is MetricEffect.EQUAL
    assert compare_metric(name, 10, better) is MetricEffect.BETTER
    assert compare_metric(name, None, None) is MetricEffect.EQUAL
    assert compare_metric(name, None, 10) is MetricEffect.NOT_COMPARABLE
    assert compare_metric(name, 10, None) is MetricEffect.NOT_COMPARABLE


@pytest.mark.parametrize(
    ("effects", "expected"),
    [
        ((MetricEffect.WORSE, MetricEffect.EQUAL), StressEffect.WORSENED),
        ((MetricEffect.EQUAL,), StressEffect.UNCHANGED),
        ((MetricEffect.WORSE, MetricEffect.BETTER), StressEffect.MIXED),
        ((MetricEffect.BETTER, MetricEffect.EQUAL), StressEffect.IMPROVED),
        ((MetricEffect.NOT_COMPARABLE,), StressEffect.NOT_COMPARABLE),
    ],
)
def test_aggregate_stress_classes(
    effects: tuple[MetricEffect, ...], expected: StressEffect
) -> None:
    assert aggregate_stress_effect(effects) is expected


def test_strict_neutral_allows_capacity_unknown_only_and_selects_no_action() -> None:
    fixture = make_fixture(neutral_records())
    evaluation = evaluate_c05(*fixture.args())
    no_action = next(
        item for item in fixture.candidates.candidates
        if item.family is InterventionFamily.NO_ACTION
    )
    assert evaluation.neutral_no_action_eligible
    assert evaluation.disposition is RecommendationDisposition.NO_ACTION
    assert evaluation.selected_candidate_id == no_action.candidate_id
    assert evaluation.candidate_order[0] == no_action.candidate_id


def test_delivery_unknown_and_all_active_unavailable_abstain() -> None:
    delivery_unknown = evaluate_c05(*make_fixture().args())
    assert delivery_unknown.disposition is RecommendationDisposition.NO_RECOMMENDATION

    fixture = make_fixture(records_for_active(InterventionFamily.SUPPLIER_INTERVENTION))
    all_unavailable = evaluate_c05(*fixture.args())
    assert all_unavailable.disposition is RecommendationDisposition.NO_RECOMMENDATION
    assert all_unavailable.outcome_code == "C05_ACTIVE_SIMULATION_EVIDENCE_UNAVAILABLE"


@pytest.mark.parametrize(
    "family",
    (
        InterventionFamily.SUPPLIER_INTERVENTION,
        InterventionFamily.QUALITY_INTERVENTION,
        InterventionFamily.CAPACITY_INTERVENTION,
    ),
)
def test_each_single_active_family_is_investigation_only(family: InterventionFamily) -> None:
    fixture = make_fixture(records_for_active(family))
    fixture = with_simulations(
        fixture, {family: (SimulationStatus.SUCCEEDED, StressEffect.UNCHANGED)}
    )
    evaluation = evaluate_c05(*fixture.args())
    selected = next(item for item in fixture.candidates.candidates if item.family is family)
    assert evaluation.disposition is RecommendationDisposition.INVESTIGATION_ONLY
    assert evaluation.selected_candidate_id == selected.candidate_id
    assert evaluation.outcome_code == "C05_SINGLE_ACTIVE_FAMILY_INVESTIGATION"


def test_multi_active_matrix_preserves_unique_focus_ties_partial_and_nonmonotonic() -> None:
    case = next(item for item in CASES if item["case_id"] == "C03-G27")
    fixture = make_fixture(list(_records_for_case(case)))
    supplier = InterventionFamily.SUPPLIER_INTERVENTION
    quality = InterventionFamily.QUALITY_INTERVENTION

    unique = with_simulations(
        fixture,
        {
            supplier: (SimulationStatus.SUCCEEDED, StressEffect.WORSENED),
            quality: (SimulationStatus.SUCCEEDED, StressEffect.UNCHANGED),
        },
    )
    unique_eval = evaluate_c05(*unique.args())
    assert unique_eval.disposition is RecommendationDisposition.INVESTIGATION_ONLY
    assert unique_eval.selected_candidate_id == next(
        item.candidate_id for item in fixture.candidates.candidates if item.family is supplier
    )

    tied = with_simulations(
        fixture,
        {
            supplier: (SimulationStatus.SUCCEEDED, StressEffect.WORSENED),
            quality: (SimulationStatus.SUCCEEDED, StressEffect.WORSENED),
        },
    )
    tied_eval = evaluate_c05(*tied.args())
    assert tied_eval.disposition is RecommendationDisposition.DEFER_TO_HUMAN
    assert tied_eval.selected_candidate_id is None and tied_eval.top_tie_count == 2

    no_worse = with_simulations(
        fixture,
        {
            supplier: (SimulationStatus.SUCCEEDED, StressEffect.UNCHANGED),
            quality: (SimulationStatus.SUCCEEDED, StressEffect.UNCHANGED),
        },
    )
    assert evaluate_c05(*no_worse.args()).disposition is RecommendationDisposition.DEFER_TO_HUMAN

    partial = with_simulations(
        fixture,
        {
            supplier: (SimulationStatus.SUCCEEDED, StressEffect.WORSENED),
            quality: (SimulationStatus.FAILED, StressEffect.UNCHANGED),
        },
    )
    partial_eval = evaluate_c05(*partial.args())
    assert partial_eval.disposition is RecommendationDisposition.DEFER_TO_HUMAN
    assert partial_eval.partial_active_comparison

    improved = with_simulations(
        fixture,
        {
            supplier: (SimulationStatus.SUCCEEDED, StressEffect.IMPROVED),
            quality: (SimulationStatus.SUCCEEDED, StressEffect.UNCHANGED),
        },
    )
    improved_eval = evaluate_c05(*improved.args())
    assert improved_eval.disposition is RecommendationDisposition.DEFER_TO_HUMAN
    assert improved_eval.outcome_code == "C05_NONMONOTONIC_STRESS_RESULT"


def test_inactive_family_failure_does_not_block_unique_active_family() -> None:
    supplier = InterventionFamily.SUPPLIER_INTERVENTION
    fixture = make_fixture(records_for_active(supplier))
    fixture = with_simulations(
        fixture,
        {
            supplier: (SimulationStatus.SUCCEEDED, StressEffect.WORSENED),
            InterventionFamily.QUALITY_INTERVENTION: (
                SimulationStatus.FAILED,
                StressEffect.UNCHANGED,
            ),
        },
    )
    assert evaluate_c05(*fixture.args()).disposition is RecommendationDisposition.INVESTIGATION_ONLY
