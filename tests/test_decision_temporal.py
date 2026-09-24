"""C02 field-level availability, exact boundaries, and no future-tail leakage."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from flowlens.decision.context import build_decision_context
from flowlens.decision.contracts import Evidence
from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.primitives import ScalarValue, Uncertainty
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.decision.snapshot import build_state_snapshot, source_unknowns
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


@pytest.mark.parametrize(
    "case",
    ("complete", "missing_inventory", "missing_quality", "missing_procurement", "conflict"),
)
def test_cross_dataset_future_tail_preserves_normalized_semantics(case: str) -> None:
    cutoff = datetime(2026, 1, 20, tzinfo=UTC)

    def project_variant(days_later: int) -> tuple[tuple[object, ...], set[str]]:
        future = cutoff + timedelta(days=days_later)
        records = [
            (entity, record_id, dict(fields))
            for entity, record_id, fields in sample_records()
            if not (
                (case == "missing_inventory" and entity == "fact_inventory_snapshot")
                or (
                    case == "missing_quality"
                    and entity in ("fact_quality_inspection", "fact_rework")
                )
                or (case == "missing_procurement" and entity == "fact_purchase_order")
            )
        ]
        for entity, _, fields in records:
            if entity == "fact_work_order":
                fields["actual_end_at"] = future
                fields["completed_quantity"] = days_later
                if case == "conflict":
                    fields["product_id"] = "P-2"
            elif entity == "fact_purchase_order":
                fields["actual_receipt_at"] = future
                fields["received_quantity"] = Decimal(days_later)
            elif entity == "fact_rework":
                fields["rework_end_at"] = future
        records.extend(
            (
                (
                    "fact_purchase_order",
                    "PO-FUTURE",
                    {
                        "purchase_order_id": "PO-FUTURE",
                        "supplier_id": "SUP-FUTURE",
                        "material_id": "MAT-1",
                        "ordered_at": future,
                        "promised_receipt_at": future + timedelta(days=1),
                        "ordered_quantity": Decimal(days_later),
                        "actual_receipt_at": future + timedelta(days=1),
                        "received_quantity": Decimal(days_later),
                        "status": "RECEIVED",
                    },
                ),
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
        run = make_run(
            cutoff,
            f"dsv-{case}-{days_later}",
            hashlib.sha256(f"{case}:{days_later}".encode()).hexdigest(),
        )
        inventory_materials = tuple(
            item.value
            for item in projected
            if item.source_entity == "fact_inventory_snapshot"
            and item.source_field == "material_id"
            and isinstance(item.value, str)
        )
        unknowns = source_unknowns(1, 1, ("MAT-1",), inventory_materials)
        snapshot = build_state_snapshot(run, projected, unknowns)
        bundle = build_evidence_bundle(snapshot)
        context = build_decision_context(snapshot, bundle)
        future_ids = {"PO-FUTURE", "D-FUTURE", "QI-FUTURE", "RW-FUTURE", "INV-FUTURE"}
        assert not any(
            entry.source_ref.source_record_id in future_ids for entry in snapshot.entries
        )
        assert not any(item.source_record_id in future_ids for item in bundle.evidence)
        assert context.uncertainties == bundle.uncertainties
        assert canonical_json_bytes(snapshot) == canonical_json_bytes(
            build_state_snapshot(run, projected, unknowns)
        )
        assert canonical_json_bytes(bundle) == canonical_json_bytes(build_evidence_bundle(snapshot))
        assert canonical_json_bytes(context) == canonical_json_bytes(
            build_decision_context(snapshot, bundle)
        )

        def evidence_key(item: Evidence) -> tuple[object, ...]:
            return (
                item.source_entity,
                item.source_record_id,
                item.source_field,
                item.value,
                item.observed_at,
                item.available_at,
                item.relationship_type,
                item.trust_level,
                item.freshness_status,
                tuple((limit.code, limit.message) for limit in item.limitations),
            )

        keys_by_id = {item.evidence_id: evidence_key(item) for item in bundle.evidence}

        def evidence_refs(ids: tuple[str, ...]) -> tuple[tuple[object, ...], ...]:
            return tuple(sorted((keys_by_id[item_id] for item_id in ids), key=repr))

        def uncertainty_key(item: Uncertainty) -> tuple[object, ...]:
            return item.status, item.code, item.message, evidence_refs(item.evidence_ids)

        def uncertainties(items: Iterable[Uncertainty]) -> tuple[tuple[object, ...], ...]:
            return tuple(sorted((uncertainty_key(item) for item in items), key=repr))

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
        evidence_view = tuple(sorted(keys_by_id.values(), key=repr))
        context_view = (
            context.schema_version,
            context.context_policy_version,
            context.order_id,
            context.as_of_time,
            evidence_refs(context.selected_evidence_ids),
            evidence_refs(context.direct_evidence_ids),
            evidence_refs(context.derived_evidence_ids),
            evidence_refs(context.associative_evidence_ids),
            uncertainties(context.uncertainties),
            tuple((item.code, item.message) for item in context.limitations),
            tuple(
                sorted(
                    (
                        (
                            item.conflict_code,
                            item.critical,
                            item.resolution_status,
                            item.message,
                            evidence_refs(item.evidence_ids),
                        )
                        for item in context.conflicts
                    ),
                    key=repr,
                )
            ),
        )
        normalized = (
            snapshot.schema_version,
            snapshot.order_id,
            snapshot.as_of_time,
            source_view,
            uncertainties(snapshot.unknowns),
            bundle.schema_version,
            evidence_view,
            uncertainties(bundle.uncertainties),
            context_view,
        )
        codes = {item.code for item in bundle.uncertainties}
        codes.update(item.conflict_code for item in context.conflicts)
        return normalized, codes

    first, first_codes = project_variant(2)
    second, second_codes = project_variant(3)
    assert first == second
    assert first_codes == second_codes
    if case == "missing_inventory":
        assert "INVENTORY_EVIDENCE_MISSING" in first_codes
    elif case == "missing_quality":
        assert "QUALITY_EVIDENCE_NOT_AVAILABLE" in first_codes
        assert "QUALITY_FINALITY_UNKNOWN" not in first_codes
    elif case == "missing_procurement":
        assert "PROCUREMENT_EVIDENCE_NOT_AVAILABLE" in first_codes
    elif case == "conflict":
        assert "WORK_ORDER_PRODUCT_MISMATCH" in first_codes
