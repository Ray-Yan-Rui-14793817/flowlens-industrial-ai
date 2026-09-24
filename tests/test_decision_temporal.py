"""C02 field-level availability, exact boundaries, and no future-tail leakage."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.primitives import ScalarValue
from flowlens.decision.snapshot import build_state_snapshot
from flowlens.decision.temporal import C02BuildError, project_record, validate_as_of
from test_decision_snapshot import ORDER_AT, make_run, sample_projected, sample_records


def test_as_of_period_boundaries() -> None:
    validate_as_of(datetime(2026, 1, 1, tzinfo=UTC), date(2026, 1, 1), date(2026, 3, 31))
    validate_as_of(
        datetime(2026, 3, 31, 15, 59, 59, 999999, tzinfo=UTC), date(2026, 1, 1), date(2026, 3, 31)
    )
    with pytest.raises(C02BuildError, match="AS_OF_OUTSIDE_DATASET_HORIZON"):
        validate_as_of(datetime(2025, 12, 31, tzinfo=UTC), date(2026, 1, 1), date(2026, 3, 31))
    with pytest.raises(C02BuildError, match="AS_OF_OUTSIDE_DATASET_HORIZON"):
        validate_as_of(datetime(2026, 3, 31, 16, tzinfo=UTC), date(2026, 1, 1), date(2026, 3, 31))


@pytest.mark.parametrize(
    ("entity", "event_field"),
    (
        ("fact_quality_inspection", "inspection_at"),
        ("fact_rework", "rework_start_at"),
        ("fact_inventory_snapshot", "snapshot_at"),
        ("fact_delivery", "delivery_at"),
    ),
)
def test_future_event_rows_excluded(entity: str, event_field: str) -> None:
    record_id, original = next(
        (record_id, fields) for kind, record_id, fields in sample_records() if kind == entity
    )
    fields = dict(original)
    fields[event_field] = datetime(2026, 1, 20, 0, 0, 0, 1, tzinfo=UTC)
    assert not project_record(
        entity,
        record_id,
        fields,
        as_of_time=datetime(2026, 1, 20, tzinfo=UTC),
        period_start=date(2026, 1, 1),
        target_order_at=ORDER_AT,
    )


def test_operation_future_actuals_are_invisible() -> None:
    future = datetime(2026, 1, 21, tzinfo=UTC)
    fields: dict[str, ScalarValue] = {
        "operation_id": "OP-1",
        "work_order_id": "WO-1",
        "work_center_id": "WC-1",
        "sequence_number": 1,
        "planned_start_at": ORDER_AT,
        "planned_end_at": future,
        "actual_start_at": future,
        "actual_end_at": future,
        "status": "COMPLETED",
    }
    projected = project_record(
        "fact_operation",
        "OP-1",
        fields,
        as_of_time=datetime(2026, 1, 20, tzinfo=UTC),
        period_start=date(2026, 1, 1),
        target_order_at=ORDER_AT,
    )
    assert {item.source_field for item in projected} == {
        "operation_id",
        "work_order_id",
        "work_center_id",
        "sequence_number",
        "planned_start_at",
        "planned_end_at",
    }


def test_field_event_cutoff_is_inclusive_to_microsecond() -> None:
    event = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    fields: dict[str, ScalarValue] = {
        "work_order_id": "WO-1",
        "sales_order_id": "SO-1",
        "product_id": "P-1",
        "planned_start_at": ORDER_AT,
        "planned_end_at": event + timedelta(days=2),
        "planned_quantity": 10,
        "actual_start_at": event,
        "actual_end_at": event + timedelta(days=1),
        "completed_quantity": 10,
        "status": "COMPLETED",
    }
    before = project_record(
        "fact_work_order",
        "WO-1",
        fields,
        as_of_time=event - timedelta(microseconds=1),
        period_start=date(2026, 1, 1),
        target_order_at=ORDER_AT,
    )
    at = project_record(
        "fact_work_order",
        "WO-1",
        fields,
        as_of_time=event,
        period_start=date(2026, 1, 1),
        target_order_at=ORDER_AT,
    )
    assert "actual_start_at" not in {item.source_field for item in before}
    assert "actual_start_at" in {item.source_field for item in at}
    assert "actual_end_at" not in {item.source_field for item in at}
    assert "completed_quantity" not in {item.source_field for item in at}
    assert "status" not in {item.source_field for item in at}


def test_future_rows_and_receipt_values_are_invisible() -> None:
    cutoff = datetime(2026, 1, 20, tzinfo=UTC)
    po: dict[str, ScalarValue] = {
        "purchase_order_id": "PO-1",
        "supplier_id": "SUP-1",
        "material_id": "MAT-1",
        "ordered_at": ORDER_AT,
        "promised_receipt_at": cutoff,
        "ordered_quantity": 10,
        "actual_receipt_at": cutoff + timedelta(microseconds=1),
        "received_quantity": 10,
        "status": "RECEIVED",
    }
    projected = project_record(
        "fact_purchase_order",
        "PO-1",
        po,
        as_of_time=cutoff,
        period_start=date(2026, 1, 1),
        target_order_at=ORDER_AT,
    )
    fields = {item.source_field for item in projected}
    assert "actual_receipt_at" not in fields
    assert "received_quantity" not in fields
    assert "status" not in fields
    delivery: dict[str, ScalarValue] = {
        "delivery_id": "D-1",
        "sales_order_id": "SO-1",
        "delivery_at": cutoff + timedelta(microseconds=1),
        "delivered_quantity": 10,
    }
    assert not project_record(
        "fact_delivery",
        "D-1",
        delivery,
        as_of_time=cutoff,
        period_start=date(2026, 1, 1),
        target_order_at=ORDER_AT,
    )


def test_future_tail_normalized_visible_semantics() -> None:
    cutoff = datetime(2026, 1, 20, tzinfo=UTC)
    original = sample_projected(cutoff)
    mutated = tuple(item for item in original)
    future: dict[str, ScalarValue] = {
        "delivery_id": "D-FUTURE",
        "sales_order_id": "SO-1",
        "delivery_at": cutoff + timedelta(days=1),
        "delivered_quantity": 3,
    }
    mutated += project_record(
        "fact_delivery",
        "D-FUTURE",
        future,
        as_of_time=cutoff,
        period_start=date(2026, 1, 1),
        target_order_at=ORDER_AT,
    )
    left = build_state_snapshot(make_run(cutoff), original)
    right = build_state_snapshot(make_run(cutoff), mutated)
    assert left.entries == right.entries
    assert left.snapshot_hash == right.snapshot_hash


def test_cross_dataset_future_tail_preserves_normalized_semantics() -> None:
    cutoff = datetime(2026, 1, 20, tzinfo=UTC)

    def project_variant(days_later: int) -> tuple[tuple[object, ...], tuple[object, ...]]:
        future = cutoff + timedelta(days=days_later)
        records = [
            (entity, record_id, dict(fields)) for entity, record_id, fields in sample_records()
        ]
        for entity, _, fields in records:
            if entity == "fact_work_order":
                fields["actual_end_at"] = future
                fields["completed_quantity"] = days_later
            elif entity == "fact_purchase_order":
                fields["actual_receipt_at"] = future
                fields["received_quantity"] = Decimal(days_later)
            elif entity == "fact_rework":
                fields["rework_end_at"] = future
        records.extend(
            (
                (
                    "fact_operation",
                    "OP-FUTURE",
                    {
                        "operation_id": "OP-FUTURE",
                        "work_order_id": "WO-1",
                        "work_center_id": "WC-1",
                        "sequence_number": 1,
                        "planned_start_at": ORDER_AT,
                        "planned_end_at": cutoff + timedelta(days=2),
                        "actual_start_at": future,
                        "actual_end_at": future,
                    },
                ),
                (
                    "fact_delivery",
                    "D-FUTURE",
                    {
                        "delivery_id": "D-FUTURE",
                        "sales_order_id": "SO-1",
                        "delivery_at": future,
                        "delivered_quantity": days_later,
                    },
                ),
                (
                    "fact_quality_inspection",
                    "QI-FUTURE",
                    {
                        "inspection_id": "QI-FUTURE",
                        "work_order_id": "WO-1",
                        "operation_id": "OP-FUTURE",
                        "inspection_at": future,
                        "inspection_type": "FINAL",
                        "inspected_quantity": days_later,
                        "passed_quantity": 0,
                        "failed_quantity": days_later,
                        "defect_category": "FUTURE",
                        "severity": "HIGH",
                        "result": "FAIL",
                    },
                ),
                (
                    "fact_rework",
                    "RW-FUTURE",
                    {
                        "rework_id": "RW-FUTURE",
                        "inspection_id": "QI-FUTURE",
                        "work_order_id": "WO-1",
                        "work_center_id": "WC-1",
                        "rework_start_at": future,
                        "rework_end_at": future,
                        "rework_quantity": days_later,
                        "rework_reason": "FUTURE",
                    },
                ),
                (
                    "fact_inventory_snapshot",
                    "INV-FUTURE",
                    {
                        "inventory_snapshot_id": "INV-FUTURE",
                        "material_id": "MAT-1",
                        "snapshot_at": future,
                        "on_hand_quantity": Decimal(days_later),
                        "reserved_quantity": Decimal(0),
                    },
                ),
            )
        )
        projected = tuple(
            item
            for entity, record_id, fields in records
            for item in project_record(
                entity,
                record_id,
                fields,
                as_of_time=cutoff,
                period_start=date(2026, 1, 1),
                target_order_at=ORDER_AT,
            )
        )
        run = make_run(cutoff, f"dsv-{days_later}", str(days_later) * 64)
        snapshot = build_state_snapshot(run, projected)
        bundle = build_evidence_bundle(snapshot)
        source_view = tuple(
            (
                entry.source_ref.source_entity,
                entry.source_ref.source_record_id,
                entry.field,
                entry.value,
                entry.observed_at,
                entry.available_at,
            )
            for entry in snapshot.entries
        )
        evidence_view = tuple(
            sorted(
                (
                    (
                        item.source_entity,
                        item.source_record_id,
                        item.source_field,
                        item.value,
                        item.observed_at,
                        item.available_at,
                        item.relationship_type,
                        item.trust_level,
                        item.freshness_status,
                        item.limitations,
                    )
                    for item in bundle.evidence
                ),
                key=repr,
            )
        )
        return source_view, evidence_view

    assert project_variant(2) == project_variant(3)
