"""Pure C02 snapshot fixtures and immutable identity checks."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from flowlens.decision.contracts import DecisionRun, StateSnapshot
from flowlens.decision.primitives import ArtifactProvenance, ScalarValue, VersionRef
from flowlens.decision.serialization import canonical_json_bytes, derive_artifact_id
from flowlens.decision.snapshot import build_state_snapshot, source_unknowns
from flowlens.decision.temporal import ProjectedSourceField, project_record

ORDER_AT = datetime(2026, 1, 10, tzinfo=UTC)
AS_OF = datetime(2026, 1, 20, tzinfo=UTC)
PERIOD_START = date(2026, 1, 1)


def make_run(
    as_of: datetime = AS_OF,
    dataset_version: str = "dsv-1",
    dataset_hash: str = "a" * 64,
) -> DecisionRun:
    identity = {
        "order_id": "SO-1",
        "as_of_time": as_of,
        "dataset_version": dataset_version,
        "dataset_hash": dataset_hash,
        "contract_bundle_version": "w03-c01-v1",
        "tool_registry_version": "w03-c02-tools.v1",
    }
    return DecisionRun(
        run_id=derive_artifact_id("decision-run", "decision-run.v1", identity),
        schema_version="decision-run.v1",
        order_id="SO-1",
        as_of_time=as_of,
        dataset_version=dataset_version,
        dataset_hash=dataset_hash,
        contract_bundle_version="w03-c01-v1",
        tool_registry_version="w03-c02-tools.v1",
        provenance=ArtifactProvenance(
            producer="test",
            producer_version="v1",
            input_artifact_ids=(),
            source_refs=(),
            contract_versions=(VersionRef(name="w03-c01", version="v1"),),
            implementation_sha=None,
        ),
    )


def sample_records() -> tuple[tuple[str, str, dict[str, ScalarValue]], ...]:
    records: tuple[tuple[str, str, dict[str, ScalarValue]], ...] = (
        (
            "fact_sales_order",
            "SO-1",
            {
                "sales_order_id": "SO-1",
                "customer_id": "C-1",
                "product_id": "P-1",
                "order_at": ORDER_AT,
                "promised_delivery_at": datetime(2026, 2, 1, tzinfo=UTC),
                "order_quantity": 10,
                "priority": "NORMAL",
                "status": "DELIVERED",
            },
        ),
        (
            "fact_work_order",
            "WO-1",
            {
                "work_order_id": "WO-1",
                "sales_order_id": "SO-1",
                "product_id": "P-1",
                "planned_start_at": datetime(2026, 1, 12, tzinfo=UTC),
                "planned_end_at": datetime(2026, 1, 23, tzinfo=UTC),
                "planned_quantity": 10,
                "actual_start_at": datetime(2026, 1, 14, tzinfo=UTC),
                "actual_end_at": datetime(2026, 1, 22, tzinfo=UTC),
                "completed_quantity": 9,
                "status": "COMPLETED",
            },
        ),
        (
            "fact_material_requirement",
            "MR-1",
            {
                "material_requirement_id": "MR-1",
                "work_order_id": "WO-1",
                "material_id": "MAT-1",
                "required_quantity": Decimal("10"),
                "need_by_at": datetime(2026, 1, 15, tzinfo=UTC),
            },
        ),
        (
            "fact_purchase_order",
            "PO-1",
            {
                "purchase_order_id": "PO-1",
                "supplier_id": "SUP-1",
                "material_id": "MAT-1",
                "ordered_at": datetime(2026, 1, 11, tzinfo=UTC),
                "promised_receipt_at": datetime(2026, 1, 18, tzinfo=UTC),
                "ordered_quantity": Decimal("20"),
                "actual_receipt_at": datetime(2026, 1, 22, tzinfo=UTC),
                "received_quantity": Decimal("20"),
                "status": "RECEIVED",
            },
        ),
        (
            "fact_inventory_snapshot",
            "INV-1",
            {
                "inventory_snapshot_id": "INV-1",
                "material_id": "MAT-1",
                "snapshot_at": datetime(2026, 1, 16, tzinfo=UTC),
                "on_hand_quantity": Decimal("30"),
                "reserved_quantity": Decimal("5"),
            },
        ),
        (
            "fact_quality_inspection",
            "QI-1",
            {
                "inspection_id": "QI-1",
                "work_order_id": "WO-1",
                "operation_id": None,
                "inspection_at": datetime(2026, 1, 17, tzinfo=UTC),
                "inspection_type": "FINAL",
                "inspected_quantity": 10,
                "passed_quantity": 7,
                "failed_quantity": 3,
                "defect_category": "SURFACE",
                "severity": "MEDIUM",
                "result": "FAIL",
            },
        ),
        (
            "fact_rework",
            "RW-1",
            {
                "rework_id": "RW-1",
                "inspection_id": "QI-1",
                "work_order_id": "WO-1",
                "work_center_id": "WC-1",
                "rework_start_at": datetime(2026, 1, 18, tzinfo=UTC),
                "rework_end_at": datetime(2026, 1, 22, tzinfo=UTC),
                "rework_quantity": 1,
                "rework_reason": "SYNTHETIC_SURFACE_REFINISH",
            },
        ),
        (
            "fact_delivery",
            "D-1",
            {
                "delivery_id": "D-1",
                "sales_order_id": "SO-1",
                "delivery_at": datetime(2026, 1, 19, tzinfo=UTC),
                "delivered_quantity": 4,
            },
        ),
    )
    return records


def sample_projected(as_of: datetime = AS_OF) -> tuple[ProjectedSourceField, ...]:
    projected: list[ProjectedSourceField] = []
    for entity, record_id, fields in sample_records():
        projected.extend(
            project_record(
                entity,
                record_id,
                fields,
                as_of_time=as_of,
                period_start=PERIOD_START,
                target_order_at=ORDER_AT,
            )
        )
    return tuple(projected)


def sample_snapshot(as_of: datetime = AS_OF) -> StateSnapshot:
    unknowns = source_unknowns(1, 1, ("MAT-1",), ("MAT-1",))
    return build_state_snapshot(make_run(as_of), sample_projected(as_of), unknowns)


def test_snapshot_replay_and_source_exclusion() -> None:
    first = sample_snapshot()
    second = sample_snapshot()
    assert first == second
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert len(first.snapshot_hash) == 64
    assert not any(entry.field == "status" for entry in first.entries)
    assert not any(
        entry.field in ("actual_end_at", "completed_quantity", "received_quantity")
        for entry in first.entries
    )


def test_snapshot_unknowns_have_no_downstream_evidence_ids() -> None:
    unknowns = source_unknowns(0, 0, ("MAT-1",), ())
    assert {item.code for item in unknowns} == {
        "WORK_ORDER_EVIDENCE_MISSING",
        "INVENTORY_EVIDENCE_MISSING",
    }
    snapshot = build_state_snapshot(make_run(), sample_projected(), unknowns)
    assert all(not item.evidence_ids for item in snapshot.unknowns)
