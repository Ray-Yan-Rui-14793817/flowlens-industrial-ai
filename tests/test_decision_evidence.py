"""C02 trust, freshness, uncertainty, and bounded derivation proofs."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

from flowlens.decision.enums import FreshnessStatus, TrustLevel
from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.primitives import ScalarValue
from flowlens.decision.snapshot import build_state_snapshot, source_unknowns
from flowlens.decision.temporal import project_record
from test_decision_snapshot import AS_OF, ORDER_AT, make_run, sample_projected, sample_snapshot


def test_source_evidence_is_exactly_snapshot_backed() -> None:
    snapshot = sample_snapshot()
    bundle = build_evidence_bundle(snapshot)
    source = [item for item in bundle.evidence if item.source_entity != "c02_derivation"]
    assert len(source) == len(snapshot.entries)
    by_key = {
        (item.source_entity, item.source_record_id, item.source_field): item for item in source
    }
    for entry in snapshot.entries:
        item = by_key[
            (
                entry.source_ref.source_entity,
                entry.source_ref.source_record_id,
                entry.source_ref.source_field,
            )
        ]
        assert (item.value, item.observed_at, item.available_at) == (
            entry.value,
            entry.observed_at,
            entry.available_at,
        )
        assert item.provenance.source_refs == (entry.source_ref,)
    assert all(item.available_at <= AS_OF for item in bundle.evidence)
    assert all(item.trust_level is not TrustLevel.FORBIDDEN_INFERENCE for item in bundle.evidence)


def test_association_derivation_and_quality_unknowns() -> None:
    bundle = build_evidence_bundle(sample_snapshot())
    po = [item for item in bundle.evidence if item.source_entity == "fact_purchase_order"]
    assert po and all(item.trust_level is TrustLevel.ASSOCIATIVE_EVIDENCE for item in po)
    assert all(item.relationship_type == "MATERIAL_TIME_ASSOCIATION" for item in po)
    derived = {
        item.source_field: item
        for item in bundle.evidence
        if item.source_entity == "c02_derivation"
    }
    assert derived["delivered_quantity_as_of"].value == 4
    assert derived["remaining_quantity_as_of"].value == 6
    assert derived["delivery_state_as_of"].value == "PARTIALLY_DELIVERED_AS_OF"
    assert derived["work_order_state_as_of"].value == "IN_PROGRESS_AS_OF"
    assert derived["purchase_order_receipt_state_as_of"].value == "NOT_RECEIVED_AS_OF"
    assert (
        derived["purchase_order_receipt_state_as_of"].trust_level is TrustLevel.ASSOCIATIVE_EVIDENCE
    )
    assert derived["unresolved_failed_quantity_as_of"].value == 2
    codes = {item.code for item in bundle.uncertainties}
    assert {
        "PO_ALLOCATION_ASSOCIATIVE_ONLY",
        "MATERIAL_AVAILABILITY_CURRENT_STATE_UNKNOWN",
        "QUALITY_FINALITY_UNKNOWN",
        "QUALITY_DISPOSITION_UNKNOWN",
    } <= codes
    assert "DOES_NOT_ESTABLISH_ORDER_SPECIFIC_ALLOCATION" in {
        lim.code for item in po for lim in item.limitations
    }


def test_inventory_freshness_exact_boundaries() -> None:
    observed = datetime(2026, 1, 16, tzinfo=UTC)
    for age, expected in (
        (timedelta(hours=24), FreshnessStatus.FRESH),
        (timedelta(hours=24, microseconds=1), FreshnessStatus.STALE),
        (timedelta(days=7), FreshnessStatus.STALE),
        (timedelta(days=7, microseconds=1), FreshnessStatus.EXPIRED),
    ):
        snapshot = sample_snapshot(observed + age)
        bundle = build_evidence_bundle(snapshot)
        items = [
            item for item in bundle.evidence if item.source_entity == "fact_inventory_snapshot"
        ]
        assert items and {item.freshness_status for item in items} == {expected}


def test_full_recorded_rework_still_has_unknown_quality_finality() -> None:
    projected = tuple(
        replace(item, value=3)
        if item.source_entity == "fact_rework" and item.source_field == "rework_quantity"
        else item
        for item in sample_projected()
    )
    snapshot = build_state_snapshot(make_run(), projected)
    bundle = build_evidence_bundle(snapshot)
    codes = {item.code for item in bundle.uncertainties}
    assert "QUALITY_FINALITY_UNKNOWN" in codes
    assert "QUALITY_DISPOSITION_UNKNOWN" not in codes


def test_full_delivery_uses_only_admitted_delivery_quantity() -> None:
    projected = tuple(
        replace(item, value=10)
        if item.source_entity == "fact_delivery" and item.source_field == "delivered_quantity"
        else item
        for item in sample_projected()
    )
    bundle = build_evidence_bundle(build_state_snapshot(make_run(), projected))
    derived = {
        item.source_field: item.value
        for item in bundle.evidence
        if item.source_entity == "c02_derivation"
    }
    assert derived["delivered_quantity_as_of"] == 10
    assert derived["remaining_quantity_as_of"] == 0
    assert derived["delivery_state_as_of"] == "DELIVERED_AS_OF"


def test_work_order_and_operation_states_follow_admitted_events_only() -> None:
    fields: dict[str, ScalarValue] = {
        "operation_id": "OP-1",
        "work_order_id": "WO-1",
        "work_center_id": "WC-1",
        "sequence_number": 1,
        "planned_start_at": ORDER_AT,
        "planned_end_at": datetime(2026, 1, 23, tzinfo=UTC),
        "actual_start_at": datetime(2026, 1, 14, tzinfo=UTC),
        "actual_end_at": datetime(2026, 1, 22, tzinfo=UTC),
        "status": "COMPLETED",
    }
    for at, expected in (
        (datetime(2026, 1, 13, tzinfo=UTC), "NOT_STARTED_AS_OF"),
        (AS_OF, "IN_PROGRESS_AS_OF"),
        (datetime(2026, 1, 23, tzinfo=UTC), "COMPLETED_AS_OF"),
    ):
        operation = project_record(
            "fact_operation",
            "OP-1",
            fields,
            as_of_time=at,
            period_start=date(2026, 1, 1),
            target_order_at=ORDER_AT,
        )
        snapshot = build_state_snapshot(make_run(at), (*sample_projected(at), *operation))
        derived = {
            item.source_field: item.value
            for item in build_evidence_bundle(snapshot).evidence
            if item.source_entity == "c02_derivation"
        }
        assert derived["work_order_state_as_of"] == expected
        assert derived["operation_state_as_of"] == expected


def test_missing_procurement_and_inventory_remain_unknown() -> None:
    projected = tuple(
        item
        for item in sample_projected()
        if item.source_entity not in {"fact_purchase_order", "fact_inventory_snapshot"}
    )
    unknowns = source_unknowns(1, 1, ("MAT-1",), ())
    bundle = build_evidence_bundle(build_state_snapshot(make_run(), projected, unknowns))
    codes = {item.code for item in bundle.uncertainties}
    assert {"PROCUREMENT_EVIDENCE_NOT_AVAILABLE", "INVENTORY_EVIDENCE_MISSING"} <= codes
    assert not any(item.source_entity == "fact_purchase_order" for item in bundle.evidence)
