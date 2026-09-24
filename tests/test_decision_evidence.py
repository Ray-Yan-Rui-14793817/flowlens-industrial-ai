"""C02 trust, freshness, uncertainty, and bounded derivation proofs."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

from flowlens.decision.enums import FreshnessStatus, TrustLevel
from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.snapshot import build_state_snapshot
from test_decision_snapshot import AS_OF, make_run, sample_projected, sample_snapshot


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
