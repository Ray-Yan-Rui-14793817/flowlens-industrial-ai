"""Pure deterministic W03-C03 signal construction."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import cast

from flowlens.decision.c03_policy import (
    C03_POLICY_REASON,
    C03_PRODUCER_VERSION,
    SIGNAL_POLICIES,
    limitations_for,
)
from flowlens.decision.c03_validation import (
    C03BuildError,
    EvidenceIndex,
    evidence_for_entities,
    source_refs_for,
    validate_c03_inputs,
)
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import Evidence, EvidenceBundle, Signal, SignalBundle
from flowlens.decision.enums import SignalState, SignalType
from flowlens.decision.primitives import ArtifactProvenance, Limitation, VersionRef
from flowlens.decision.serialization import derive_artifact_id


def _field(
    fields: dict[str, Evidence], name: str, expected: type[object]
) -> tuple[Evidence | None, bool]:
    item = fields.get(name)
    if item is None or item.value is None:
        return None, True
    if type(item.value) is not expected:
        raise C03BuildError("C03_RULE_INPUT_INVALID", "BLOCKED_CONTRACT")
    return item, False


def _int_quantity(item: Evidence | None) -> tuple[int | None, bool]:
    if item is None or item.value is None:
        return None, True
    value = item.value
    if type(value) is not int:
        raise C03BuildError("C03_RULE_INPUT_INVALID", "BLOCKED_CONTRACT")
    if value < 0:
        raise C03BuildError("C03_RULE_INPUT_INVALID", "BLOCKED_CONTRACT")
    return value, False


def _decimal_quantity(
    item: Evidence | None, *, positive: bool = False
) -> tuple[Decimal | None, bool]:
    if item is None or item.value is None:
        return None, True
    value = item.value
    if type(value) is not Decimal or not value.is_finite():
        raise C03BuildError("C03_RULE_INPUT_INVALID", "BLOCKED_CONTRACT")
    if value < 0 or (positive and value <= 0):
        raise C03BuildError("C03_RULE_INPUT_INVALID", "BLOCKED_CONTRACT")
    return value, False


def _row_evidence(fields: dict[str, Evidence]) -> tuple[Evidence, ...]:
    return tuple(sorted(fields.values(), key=lambda item: item.evidence_id))


def _material_scope(
    index: EvidenceIndex,
) -> tuple[
    tuple[tuple[str, dict[str, Evidence]], ...],
    tuple[tuple[str, dict[str, Evidence]], ...],
    bool,
]:
    requirements = index.entity_rows("fact_material_requirement")
    materials: set[str] = set()
    incomplete = False
    for _, fields in requirements:
        material, missing_material = _field(fields, "material_id", str)
        incomplete = incomplete or missing_material
        if material is not None:
            materials.add(str(material.value))
    purchase_orders = tuple(
        (record_id, fields)
        for record_id, fields in index.entity_rows("fact_purchase_order")
        if fields.get("material_id") is not None
        and type(fields["material_id"].value) is str
        and fields["material_id"].value in materials
    )
    return requirements, purchase_orders, incomplete


def _po_values(
    fields: dict[str, Evidence],
) -> tuple[str | None, datetime | None, datetime | None, Decimal | None, bool]:
    _, missing_id = _field(fields, "purchase_order_id", str)
    material, missing_material = _field(fields, "material_id", str)
    promise, missing_promise = _field(fields, "promised_receipt_at", datetime)
    ordered, missing_ordered = _decimal_quantity(fields.get("ordered_quantity"), positive=True)
    actual_item = fields.get("actual_receipt_at")
    actual: datetime | None = None
    missing_actual_pair = False
    received = Decimal(0)
    if actual_item is not None:
        if actual_item.value is None or type(actual_item.value) is not datetime:
            raise C03BuildError("C03_RULE_INPUT_INVALID", "BLOCKED_CONTRACT")
        actual = actual_item.value
        received_value, missing_received = _decimal_quantity(fields.get("received_quantity"))
        missing_actual_pair = missing_received
        if received_value is not None:
            received = received_value
    elif fields.get("received_quantity") is not None:
        raise C03BuildError("C03_RULE_INPUT_INVALID", "BLOCKED_CONTRACT")
    if ordered is not None and received > ordered:
        raise C03BuildError("C03_RULE_INPUT_INVALID", "BLOCKED_CONTRACT")
    outstanding = None if ordered is None or missing_actual_pair else ordered - received
    incomplete = (
        missing_id or missing_material or missing_promise or missing_ordered or missing_actual_pair
    )
    return (
        str(material.value) if material is not None else None,
        promise.value if promise is not None and type(promise.value) is datetime else None,
        actual,
        outstanding,
        incomplete,
    )


def _supplier(
    index: EvidenceIndex, context: DecisionContext
) -> tuple[SignalState, set[str], bool, tuple[Evidence, ...]]:
    requirements, purchase_orders, incomplete = _material_scope(index)
    support = tuple(
        sorted(
            {
                item
                for _, fields in (*requirements, *purchase_orders)
                for item in _row_evidence(fields)
            },
            key=lambda item: item.evidence_id,
        )
    )
    reasons: set[str] = set()
    for _, fields in purchase_orders:
        _, promise, actual, outstanding, row_incomplete = _po_values(fields)
        incomplete = incomplete or row_incomplete
        if promise is None:
            continue
        if actual is not None and actual > promise:
            reasons.add("C03_PO_RECEIPT_LATE")
        if outstanding is not None and outstanding > 0 and context.as_of_time > promise:
            reasons.add("C03_PO_OUTSTANDING_OVERDUE")
    if reasons:
        state = SignalState.ACTIVE
    elif not purchase_orders:
        state = SignalState.UNKNOWN
        reasons.add("C03_PO_EVIDENCE_MISSING")
    elif incomplete:
        state = SignalState.UNKNOWN
        reasons.add("C03_REQUIRED_FIELDS_MISSING")
    else:
        state = SignalState.INACTIVE
        reasons.add("C03_NO_OBSERVED_PO_LATENESS")
    return state, reasons, incomplete, support


def _material(
    index: EvidenceIndex, context: DecisionContext
) -> tuple[SignalState, set[str], bool, tuple[Evidence, ...]]:
    requirements, purchase_orders, incomplete = _material_scope(index)
    support = tuple(
        sorted(
            {
                item
                for _, fields in (*requirements, *purchase_orders)
                for item in _row_evidence(fields)
            },
            key=lambda item: item.evidence_id,
        )
    )
    reasons: set[str] = set()
    po_values = [(fields, _po_values(fields)) for _, fields in purchase_orders]
    for _, mr in requirements:
        _, missing_id = _field(mr, "material_requirement_id", str)
        material, missing_material = _field(mr, "material_id", str)
        need, missing_need = _field(mr, "need_by_at", datetime)
        incomplete = incomplete or missing_id or missing_material or missing_need
        if material is None or need is None:
            continue
        need_at = cast(datetime, need.value)
        associated = [values for _, values in po_values if values[0] == material.value]
        if not associated:
            incomplete = True
            reasons.add("C03_PO_FOR_REQUIREMENT_MISSING")
        for _, promise, actual, outstanding, row_incomplete in associated:
            incomplete = incomplete or row_incomplete
            if actual is not None and actual > need_at:
                reasons.add("C03_RECEIPT_AFTER_NEED_BY")
            if outstanding is not None and outstanding > 0:
                if promise is not None and promise > need_at:
                    reasons.add("C03_OUTSTANDING_PROMISE_AFTER_NEED_BY")
                if context.as_of_time > need_at:
                    reasons.add("C03_NEED_BY_PASSED_WITH_OUTSTANDING_PO")
    positive = reasons & {
        "C03_RECEIPT_AFTER_NEED_BY",
        "C03_OUTSTANDING_PROMISE_AFTER_NEED_BY",
        "C03_NEED_BY_PASSED_WITH_OUTSTANDING_PO",
    }
    if positive:
        state = SignalState.ACTIVE
    elif not requirements:
        state = SignalState.UNKNOWN
        reasons.add("C03_REQUIREMENT_EVIDENCE_MISSING")
    elif incomplete:
        state = SignalState.UNKNOWN
        reasons.add("C03_REQUIRED_FIELDS_MISSING")
    else:
        state = SignalState.INACTIVE
        reasons.add("C03_NO_ASSOCIATED_TIMING_WARNING")
    return state, reasons, incomplete, support


def _quality_failure(
    index: EvidenceIndex,
) -> tuple[SignalState, set[str], bool, tuple[Evidence, ...]]:
    rows = index.entity_rows("fact_quality_inspection")
    support = evidence_for_entities(index, ("fact_quality_inspection",))
    active = False
    incomplete = False
    for _, fields in rows:
        value, missing = _int_quantity(fields.get("failed_quantity"))
        incomplete = incomplete or missing
        active = active or (value is not None and value > 0)
    if active:
        return SignalState.ACTIVE, {"C03_RECORDED_FAILED_QUANTITY"}, incomplete, support
    if not rows:
        return SignalState.UNKNOWN, {"C03_INSPECTION_EVIDENCE_MISSING"}, False, support
    if incomplete:
        return SignalState.UNKNOWN, {"C03_REQUIRED_FIELDS_MISSING"}, True, support
    return SignalState.INACTIVE, {"C03_NO_FAILURE_IN_OBSERVED_INSPECTIONS"}, False, support


def _rework(index: EvidenceIndex) -> tuple[SignalState, set[str], bool, tuple[Evidence, ...]]:
    inspections = index.entity_rows("fact_quality_inspection")
    rows = index.entity_rows("fact_rework")
    support = evidence_for_entities(index, ("fact_quality_inspection", "fact_rework"))
    active = False
    incomplete = False
    for _, fields in rows:
        value, missing = _int_quantity(fields.get("rework_quantity"))
        incomplete = incomplete or missing
        active = active or (value is not None and value > 0)
    if active:
        return SignalState.ACTIVE, {"C03_RECORDED_REWORK"}, incomplete, support
    if not rows and not inspections:
        return SignalState.UNKNOWN, {"C03_REWORK_OBSERVATION_SCOPE_MISSING"}, False, support
    if incomplete:
        return SignalState.UNKNOWN, {"C03_REQUIRED_FIELDS_MISSING"}, True, support
    return SignalState.INACTIVE, {"C03_NO_REWORK_IN_OBSERVED_RECORDS"}, False, support


def _disposition(index: EvidenceIndex) -> tuple[SignalState, set[str], bool, tuple[Evidence, ...]]:
    inspections = index.entity_rows("fact_quality_inspection")
    support_items = list(evidence_for_entities(index, ("fact_quality_inspection", "fact_rework")))
    active = False
    incomplete = False
    for inspection_id, _ in inspections:
        fields = index.rows.get(
            ("c02_derivation", f"c02.unresolved_failed_quantity_as_of.v1|{inspection_id}"), {}
        )
        item = fields.get("unresolved_failed_quantity_as_of")
        if item is not None:
            support_items.append(item)
        value, missing = _int_quantity(item)
        incomplete = incomplete or missing
        active = active or (value is not None and value > 0)
    support = tuple(sorted(set(support_items), key=lambda item: item.evidence_id))
    if active:
        return SignalState.ACTIVE, {"C03_FAILED_QUANTITY_DISPOSITION_GAP"}, incomplete, support
    if not inspections:
        return SignalState.UNKNOWN, {"C03_INSPECTION_EVIDENCE_MISSING"}, False, support
    if incomplete:
        return SignalState.UNKNOWN, {"C03_REQUIRED_FIELDS_MISSING"}, True, support
    return SignalState.INACTIVE, {"C03_NO_OBSERVED_DISPOSITION_GAP"}, False, support


def _queue(
    index: EvidenceIndex, context: DecisionContext
) -> tuple[SignalState, set[str], bool, tuple[Evidence, ...]]:
    rows = index.entity_rows("fact_operation")
    support = evidence_for_entities(index, ("fact_operation",))
    reasons: set[str] = set()
    incomplete = False
    for _, fields in rows:
        planned, missing = _field(fields, "planned_start_at", datetime)
        incomplete = incomplete or missing
        if planned is None:
            continue
        planned_at = cast(datetime, planned.value)
        actual = fields.get("actual_start_at")
        if actual is not None:
            if actual.value is None or type(actual.value) is not datetime:
                raise C03BuildError("C03_RULE_INPUT_INVALID", "BLOCKED_CONTRACT")
            if actual.value > planned_at:
                reasons.add("C03_OPERATION_START_SLIPPAGE")
        elif context.as_of_time > planned_at:
            reasons.add("C03_OPERATION_START_OVERDUE")
    if reasons:
        state = SignalState.ACTIVE
    elif not rows:
        state = SignalState.UNKNOWN
        reasons.add("C03_OPERATION_EVIDENCE_MISSING")
    elif incomplete:
        state = SignalState.UNKNOWN
        reasons.add("C03_REQUIRED_FIELDS_MISSING")
    else:
        state = SignalState.INACTIVE
        reasons.add("C03_NO_OBSERVED_START_SLIPPAGE")
    return state, reasons, incomplete, support


def _capacity(index: EvidenceIndex) -> tuple[SignalState, set[str], bool, tuple[Evidence, ...]]:
    return (
        SignalState.UNKNOWN,
        {"C03_CAPACITY_SCOPE_INSUFFICIENT"},
        False,
        evidence_for_entities(index, ("dim_work_center", "fact_operation")),
    )


def _delivery(
    index: EvidenceIndex, context: DecisionContext
) -> tuple[SignalState, set[str], bool, tuple[Evidence, ...]]:
    support_items = list(
        evidence_for_entities(index, ("fact_delivery", "fact_sales_order", "fact_work_order"))
    )
    order = index.rows.get(("fact_sales_order", context.order_id), {})
    promise, missing_promise = _field(order, "promised_delivery_at", datetime)
    remaining_fields = index.rows.get(
        ("c02_derivation", f"c02.remaining_quantity_as_of.v1|{context.order_id}"), {}
    )
    remaining_item = remaining_fields.get("remaining_quantity_as_of")
    for derivation_id, field_name in (
        ("c02.delivered_quantity_as_of.v1", "delivered_quantity_as_of"),
        ("c02.remaining_quantity_as_of.v1", "remaining_quantity_as_of"),
        ("c02.delivery_state_as_of.v1", "delivery_state_as_of"),
    ):
        derived = index.rows.get(("c02_derivation", f"{derivation_id}|{context.order_id}"), {}).get(
            field_name
        )
        if derived is not None:
            support_items.append(derived)
    remaining, missing_remaining = _int_quantity(remaining_item)
    incomplete = missing_promise or missing_remaining
    reasons: set[str] = set()

    work_orders = index.entity_rows("fact_work_order")
    work_order_values: list[tuple[datetime | None, str | None]] = []
    for work_order_id, fields in work_orders:
        planned, missing_plan = _field(fields, "planned_end_at", datetime)
        state_fields = index.rows.get(
            ("c02_derivation", f"c02.work_order_state_as_of.v1|{work_order_id}"), {}
        )
        state, missing_state = _field(state_fields, "work_order_state_as_of", str)
        if state is not None:
            support_items.append(state)
        incomplete = incomplete or missing_plan or missing_state
        work_order_values.append(
            (
                planned.value if planned is not None and type(planned.value) is datetime else None,
                str(state.value) if state is not None else None,
            )
        )
    support = tuple(sorted(set(support_items), key=lambda item: item.evidence_id))

    if remaining == 0:
        return SignalState.INACTIVE, {"C03_DELIVERY_FULFILLED_AS_OF"}, False, support
    if remaining is not None and remaining > 0 and promise is not None:
        promised_at = cast(datetime, promise.value)
        if context.as_of_time > promised_at:
            reasons.add("C03_UNFULFILLED_COMMITMENT_OVERDUE")
        if any(
            planned is not None
            and state in ("NOT_STARTED_AS_OF", "IN_PROGRESS_AS_OF")
            and planned > promised_at
            for planned, state in work_order_values
        ):
            reasons.add("C03_INCOMPLETE_PLAN_AFTER_COMMITMENT")
    if reasons:
        return SignalState.ACTIVE, reasons, incomplete, support
    reasons.add("C03_DELIVERY_FORECAST_UNSUPPORTED")
    if incomplete:
        reasons.add("C03_REQUIRED_FIELDS_MISSING")
    return SignalState.UNKNOWN, reasons, incomplete, support


def _merge_limitations(
    signal_type: SignalType,
    support: tuple[Evidence, ...],
    context: DecisionContext,
    partial: bool,
) -> tuple[Limitation, ...]:
    return tuple(
        sorted(
            {
                *limitations_for(signal_type, partial),
                *context.limitations,
                *(limitation for item in support for limitation in item.limitations),
            },
            key=lambda item: (item.code, item.message),
        )
    )


def _make_signal(
    signal_type: SignalType,
    state: SignalState,
    reasons: set[str],
    incomplete: bool,
    support: tuple[Evidence, ...],
    context: DecisionContext,
) -> Signal:
    partial = state is SignalState.ACTIVE and incomplete
    if partial:
        reasons.update(("C03_INPUT_INCOMPLETE", "C03_SCOPE_PARTIALLY_OBSERVED"))
    reasons.add(C03_POLICY_REASON)
    evidence_ids = tuple(item.evidence_id for item in support)
    reason_codes = tuple(sorted(reasons))
    identity = {
        "run_id": context.run_id,
        "snapshot_id": context.snapshot_id,
        "signal_type": signal_type,
        "state": state,
        "evidence_ids": evidence_ids,
        "reason_codes": reason_codes,
    }
    return Signal(
        signal_id=derive_artifact_id("signal", "signal.v1", identity),
        schema_version="signal.v1",
        run_id=context.run_id,
        snapshot_id=context.snapshot_id,
        signal_type=signal_type,
        state=state,
        evidence_ids=evidence_ids,
        reason_codes=reason_codes,
        limitations=_merge_limitations(signal_type, support, context, partial),
        provenance=ArtifactProvenance(
            producer="flowlens.decision.signals",
            producer_version=C03_PRODUCER_VERSION,
            input_artifact_ids=tuple(sorted((context.evidence_bundle_id, context.context_id))),
            source_refs=source_refs_for(support),
            contract_versions=(
                VersionRef(name="w03-c01", version="v1"),
                VersionRef(name="w03-c02", version="v1"),
                VersionRef(name="w03-c02-context", version="v1"),
                VersionRef(name="w03-c03", version="v1"),
                VersionRef(name="w03-c03-signals", version="v1"),
            ),
            implementation_sha=None,
        ),
    )


def build_signal_bundle(bundle: EvidenceBundle, context: DecisionContext) -> SignalBundle:
    """Build exactly eight deterministic signals from frozen C02 artifacts."""
    index = validate_c03_inputs(bundle, context)
    evaluations = {
        SignalType.SUPPLIER_LATE_RECEIPT: _supplier(index, context),
        SignalType.MATERIAL_TIMING_RISK: _material(index, context),
        SignalType.QUALITY_FAILURE: _quality_failure(index),
        SignalType.REWORK_PRESENT: _rework(index),
        SignalType.QUALITY_DISPOSITION_UNKNOWN: _disposition(index),
        SignalType.QUEUE_DELAY: _queue(index, context),
        SignalType.CAPACITY_PRESSURE: _capacity(index),
        SignalType.DELIVERY_RISK: _delivery(index, context),
    }
    signals = tuple(
        _make_signal(signal_type, *evaluations[signal_type], context)
        for signal_type in sorted(SIGNAL_POLICIES, key=lambda item: item.value)
    )
    identity = {
        "run_id": context.run_id,
        "snapshot_id": context.snapshot_id,
        "signal_ids": tuple(item.signal_id for item in signals),
    }
    all_evidence = tuple(
        sorted(
            {index.by_id[evidence_id] for signal in signals for evidence_id in signal.evidence_ids},
            key=lambda item: item.evidence_id,
        )
    )
    return SignalBundle(
        signal_bundle_id=derive_artifact_id("signal-bundle", "signal-bundle.v1", identity),
        schema_version="signal-bundle.v1",
        run_id=context.run_id,
        snapshot_id=context.snapshot_id,
        signals=signals,
        provenance=ArtifactProvenance(
            producer="flowlens.decision.signals",
            producer_version=C03_PRODUCER_VERSION,
            input_artifact_ids=tuple(
                sorted(
                    (
                        context.evidence_bundle_id,
                        context.context_id,
                        *(item.signal_id for item in signals),
                    )
                )
            ),
            source_refs=source_refs_for(all_evidence),
            contract_versions=(
                VersionRef(name="w03-c01", version="v1"),
                VersionRef(name="w03-c02", version="v1"),
                VersionRef(name="w03-c02-context", version="v1"),
                VersionRef(name="w03-c03", version="v1"),
                VersionRef(name="w03-c03-signals", version="v1"),
            ),
            implementation_sha=None,
        ),
    )
