"""C02 lossless context, conflict preservation, identity, and replay."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime

from flowlens.decision.context import build_decision_context
from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.primitives import ScalarValue
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.decision.snapshot import build_state_snapshot
from flowlens.decision.temporal import project_record
from test_decision_snapshot import AS_OF, ORDER_AT, make_run, sample_projected, sample_snapshot


def test_context_is_lossless_partitioned_and_replayable() -> None:
    snapshot = sample_snapshot()
    bundle = build_evidence_bundle(snapshot)
    first = build_decision_context(snapshot, bundle)
    second = build_decision_context(snapshot, bundle)
    assert first == second
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    evidence_ids = {item.evidence_id for item in bundle.evidence}
    assert set(first.selected_evidence_ids) == evidence_ids
    assert (
        set(first.direct_evidence_ids)
        | set(first.derived_evidence_ids)
        | set(first.associative_evidence_ids)
    ) == evidence_ids
    assert not (set(first.direct_evidence_ids) & set(first.associative_evidence_ids))
    assert first.uncertainties == bundle.uncertainties
    assert {
        "W2_NON_BITEMPORAL_STATUS_EXCLUDED",
        "QUALITY_RELEASE_EVENT_ABSENT",
        "C02_SYNTHETIC_FRESHNESS_POLICY",
    } <= {item.code for item in first.limitations}
    assert first.schema_version == "decision-context.v1"


def test_context_id_changes_with_evidence_value() -> None:
    original = sample_projected()
    changed = tuple(
        replace(item, value="HIGH")
        if item.source_entity == "fact_sales_order" and item.source_field == "priority"
        else item
        for item in original
    )
    left = build_state_snapshot(make_run(), original)
    right = build_state_snapshot(make_run(), changed)
    left_context = build_decision_context(left, build_evidence_bundle(left))
    right_context = build_decision_context(right, build_evidence_bundle(right))
    assert left_context.context_id != right_context.context_id


def test_three_critical_conflicts_are_preserved() -> None:
    projected = list(sample_projected())
    projected = [
        replace(item, value="OP-2")
        if item.source_entity == "fact_quality_inspection"
        and item.source_record_id == "QI-1"
        and item.source_field == "operation_id"
        else replace(item, value="QI-2")
        if item.source_entity == "fact_rework" and item.source_field == "inspection_id"
        else item
        for item in projected
    ]
    records: tuple[tuple[str, str, dict[str, ScalarValue]], ...] = (
        (
            "fact_work_order",
            "WO-2",
            {
                "work_order_id": "WO-2",
                "sales_order_id": "SO-1",
                "product_id": "P-2",
                "planned_start_at": ORDER_AT,
                "planned_end_at": AS_OF,
                "planned_quantity": 2,
                "actual_start_at": None,
                "actual_end_at": None,
                "completed_quantity": 0,
            },
        ),
        (
            "fact_operation",
            "OP-2",
            {
                "operation_id": "OP-2",
                "work_order_id": "WO-2",
                "work_center_id": "WC-1",
                "sequence_number": 1,
                "planned_start_at": ORDER_AT,
                "planned_end_at": AS_OF,
                "actual_start_at": None,
                "actual_end_at": None,
            },
        ),
        (
            "fact_quality_inspection",
            "QI-2",
            {
                "inspection_id": "QI-2",
                "work_order_id": "WO-2",
                "operation_id": "OP-2",
                "inspection_at": datetime(2026, 1, 17, tzinfo=UTC),
                "inspection_type": "FINAL",
                "inspected_quantity": 2,
                "passed_quantity": 2,
                "failed_quantity": 0,
                "defect_category": None,
                "severity": None,
                "result": "PASS",
            },
        ),
    )
    for entity, record_id, fields in records:
        projected.extend(
            project_record(
                entity,
                record_id,
                fields,
                as_of_time=AS_OF,
                period_start=date(2026, 1, 1),
                target_order_at=ORDER_AT,
            )
        )
    snapshot = build_state_snapshot(make_run(), projected)
    bundle = build_evidence_bundle(snapshot)
    context = build_decision_context(snapshot, bundle)
    assert {item.conflict_code for item in context.conflicts} == {
        "WORK_ORDER_PRODUCT_MISMATCH",
        "INSPECTION_OPERATION_WORK_ORDER_MISMATCH",
        "REWORK_INSPECTION_WORK_ORDER_MISMATCH",
    }
    assert all(
        item.critical and item.resolution_status == "UNRESOLVED" for item in context.conflicts
    )
    assert all(
        set(item.evidence_ids) <= set(context.selected_evidence_ids) for item in context.conflicts
    )
