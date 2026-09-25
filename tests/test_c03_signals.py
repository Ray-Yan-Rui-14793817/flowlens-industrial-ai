"""W03-C03 golden signal-vector coverage over the closed C02 fixture."""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from flowlens.decision.c03_validation import C03BuildError
from flowlens.decision.context import DecisionContext, build_decision_context
from flowlens.decision.contracts import EvidenceBundle, SignalBundle, StateSnapshot
from flowlens.decision.enums import SignalState, SignalType
from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.primitives import ScalarValue
from flowlens.decision.signals import build_signal_bundle
from flowlens.decision.snapshot import build_state_snapshot, source_unknowns
from flowlens.decision.temporal import ProjectedSourceField, project_record
from test_decision_snapshot import AS_OF, ORDER_AT, PERIOD_START, make_run, sample_records

Record = tuple[str, str, dict[str, ScalarValue]]
VECTOR_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "w03"
    / "checkpoints"
    / "c03"
    / "specs"
    / "acceptance_vectors.json"
)


def _decode(value: object) -> ScalarValue:
    if isinstance(value, dict):
        if set(value) == {"datetime"}:
            rendered = value["datetime"]
            assert isinstance(rendered, str)
            return datetime.fromisoformat(rendered.replace("Z", "+00:00"))
        if set(value) == {"decimal"}:
            rendered = value["decimal"]
            assert isinstance(rendered, str)
            return Decimal(rendered)
        raise AssertionError(f"unsupported vector value: {value!r}")
    assert value is None or type(value) in (bool, int, str)
    return cast(ScalarValue, value)


def _records_for_case(case: dict[str, object]) -> tuple[Record, ...]:
    drop_entities = case["drop_entities"]
    assert isinstance(drop_entities, list)
    drops = {str(item) for item in drop_entities}
    records: list[Record] = [
        (entity, record_id, dict(fields))
        for entity, record_id, fields in sample_records()
        if entity not in drops
    ]
    patches = case["patch_records"]
    assert isinstance(patches, list)
    for patch in patches:
        assert isinstance(patch, dict)
        entity = patch["source_entity"]
        record_id = patch["record_id"]
        values = patch["set"]
        assert isinstance(entity, str) and isinstance(record_id, str) and isinstance(values, dict)
        target = next(
            fields
            for row_entity, row_id, fields in records
            if row_entity == entity and row_id == record_id
        )
        target.update({str(name): _decode(value) for name, value in values.items()})
    appended = case["append_records"]
    assert isinstance(appended, list)
    for item in appended:
        assert isinstance(item, dict)
        entity = item["source_entity"]
        record_id = item["record_id"]
        fields = item["fields"]
        assert isinstance(entity, str) and isinstance(record_id, str) and isinstance(fields, dict)
        records.append(
            (
                entity,
                record_id,
                {str(name): _decode(value) for name, value in fields.items()},
            )
        )
    return tuple(records)


def build_c03_fixture(
    records: Iterable[Record] | None = None,
    *,
    as_of: datetime = AS_OF,
) -> tuple[StateSnapshot, EvidenceBundle, DecisionContext]:
    selected = tuple(sample_records() if records is None else records)
    projected: list[ProjectedSourceField] = []
    for entity, record_id, fields in selected:
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
    rows = {(item.source_entity, item.source_record_id) for item in projected}
    required_materials = tuple(
        str(item.value)
        for item in projected
        if item.source_entity == "fact_material_requirement" and item.source_field == "material_id"
    )
    inventory_materials = tuple(
        str(item.value)
        for item in projected
        if item.source_entity == "fact_inventory_snapshot" and item.source_field == "material_id"
    )
    unknowns = source_unknowns(
        sum(entity == "fact_work_order" for entity, _ in rows),
        sum(entity == "fact_material_requirement" for entity, _ in rows),
        required_materials,
        inventory_materials,
    )
    snapshot = build_state_snapshot(make_run(as_of), projected, unknowns)
    bundle = build_evidence_bundle(snapshot)
    return snapshot, bundle, build_decision_context(snapshot, bundle)


def signal_map(signals: SignalBundle) -> dict[SignalType, SignalState]:
    return {item.signal_type: item.state for item in signals.signals}


with VECTOR_PATH.open(encoding="utf-8") as vector_file:
    CASES: list[dict[str, object]] = json.load(vector_file)["cases"]


@pytest.mark.parametrize("case", CASES, ids=lambda case: str(case["case_id"]))
def test_published_golden_signal_vectors(case: dict[str, object]) -> None:
    _, bundle, context = build_c03_fixture(_records_for_case(case))
    if case["case_id"] == "C03-G32":
        with pytest.raises(C03BuildError, match="C03_CRITICAL_CONFLICT") as caught:
            build_signal_bundle(bundle, context)
        assert caught.value.code == "C03_CRITICAL_CONFLICT"
        assert caught.value.state == "BLOCKED_TRUST"
        return

    first = build_signal_bundle(bundle, context)
    second = build_signal_bundle(bundle, context)
    assert first == second
    assert len(first.signals) == len(SignalType) == 8
    assert tuple(item.signal_type.value for item in first.signals) == tuple(
        sorted(item.value for item in SignalType)
    )
    expected = case["expected_signals"]
    assert isinstance(expected, dict)
    actual = signal_map(first)
    for name, state in expected.items():
        assert actual[SignalType(str(name))] is SignalState(str(state))
    for signal in first.signals:
        assert "C03_POLICY_V1" in signal.reason_codes
        assert "C03_RULE_BASED_NOT_CAUSAL" in {limitation.code for limitation in signal.limitations}


def test_equality_boundaries_and_multi_po_partial_positive() -> None:
    records = list(sample_records())
    records.append(
        (
            "fact_purchase_order",
            "PO-2",
            {
                "purchase_order_id": "PO-2",
                "supplier_id": "SUP-2",
                "material_id": "MAT-1",
                "ordered_at": datetime(2026, 1, 12, tzinfo=UTC),
                "promised_receipt_at": datetime(2026, 1, 19, tzinfo=UTC),
                "ordered_quantity": Decimal("4"),
                "actual_receipt_at": None,
                "received_quantity": None,
                "status": "OPEN",
            },
        )
    )
    _, bundle, context = build_c03_fixture(records)
    supplier = next(
        item
        for item in build_signal_bundle(bundle, context).signals
        if item.signal_type is SignalType.SUPPLIER_LATE_RECEIPT
    )
    assert supplier.state is SignalState.ACTIVE
    assert "C03_PO_OUTSTANDING_OVERDUE" in supplier.reason_codes

    # Missing a required field in another associated PO does not erase the positive witness.
    evidence = tuple(
        item
        for item in bundle.evidence
        if not (
            item.source_entity == "fact_purchase_order"
            and item.source_record_id == "PO-2"
            and item.source_field == "promised_receipt_at"
        )
    )
    from test_c03_harness import rebind_bundle_and_context

    rebound_bundle, rebound_context = rebind_bundle_and_context(bundle, context, evidence)
    partial = next(
        item
        for item in build_signal_bundle(rebound_bundle, rebound_context).signals
        if item.signal_type is SignalType.SUPPLIER_LATE_RECEIPT
    )
    assert partial.state is SignalState.ACTIVE
    assert {"C03_INPUT_INCOMPLETE", "C03_SCOPE_PARTIALLY_OBSERVED"} <= set(partial.reason_codes)
