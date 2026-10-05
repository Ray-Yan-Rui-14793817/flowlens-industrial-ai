"""The seven authorized C02 observation-state derivations, without database access."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from flowlens.decision.contracts import Evidence, StateSnapshot
from flowlens.decision.enums import FreshnessStatus, TrustLevel
from flowlens.decision.primitives import ArtifactProvenance, SourceRef, VersionRef
from flowlens.decision.serialization import canonical_primitive, derive_artifact_id
from flowlens.decision.temporal import C02BuildError

DERIVATION_IDS = (
    "c02.delivered_quantity_as_of.v1",
    "c02.remaining_quantity_as_of.v1",
    "c02.delivery_state_as_of.v1",
    "c02.work_order_state_as_of.v1",
    "c02.operation_state_as_of.v1",
    "c02.purchase_order_receipt_state_as_of.v1",
    "c02.unresolved_failed_quantity_as_of.v1",
)


def _ref_key(ref: SourceRef) -> tuple[str, str, str, str, str]:
    return (
        ref.source_entity,
        ref.source_record_id,
        ref.source_field,
        str(canonical_primitive(ref.observed_at)) if ref.observed_at else "",
        str(canonical_primitive(ref.available_at)),
    )


def _derive(
    snapshot: StateSnapshot,
    derivation_id: str,
    target_id: str,
    field: str,
    value: int | str,
    inputs: Iterable[Evidence],
) -> Evidence:
    selected = tuple(sorted(inputs, key=lambda item: item.evidence_id))
    if not selected:
        raise C02BuildError("DERIVATION_INPUT_MISSING", "BLOCKED_CONTRACT")
    associative = any(item.trust_level is TrustLevel.ASSOCIATIVE_EVIDENCE for item in selected)
    if any(
        item.trust_level in (TrustLevel.UNKNOWN, TrustLevel.FORBIDDEN_INFERENCE)
        for item in selected
    ):
        raise C02BuildError("DERIVATION_INPUT_UNTRUSTED", "BLOCKED_TRUST")
    trust = TrustLevel.ASSOCIATIVE_EVIDENCE if associative else TrustLevel.DERIVED_FACT
    relationship = "DERIVED_FROM_ASSOCIATIVE" if associative else "DERIVED_FROM_DIRECT"
    limitations = tuple(
        sorted(
            {item for source in selected for item in source.limitations},
            key=lambda item: (item.code, item.message),
        )
    )
    refs = tuple(
        sorted({ref for item in selected for ref in item.provenance.source_refs}, key=_ref_key)
    )
    identity = {
        "run_id": snapshot.run_id,
        "snapshot_id": snapshot.snapshot_id,
        "source_entity": "c02_derivation",
        "source_record_id": f"{derivation_id}|{target_id}",
        "source_field": field,
        "value": value,
        "observed_at": None,
        "available_at": snapshot.as_of_time,
        "as_of_time": snapshot.as_of_time,
        "relationship_type": relationship,
        "trust_level": trust,
        "freshness_status": FreshnessStatus.NOT_APPLICABLE,
    }
    return Evidence(
        evidence_id=derive_artifact_id("evidence", "evidence.v1", identity),
        schema_version="evidence.v1",
        run_id=snapshot.run_id,
        snapshot_id=snapshot.snapshot_id,
        source_entity="c02_derivation",
        source_record_id=f"{derivation_id}|{target_id}",
        source_field=field,
        value=value,
        observed_at=None,
        available_at=snapshot.as_of_time,
        as_of_time=snapshot.as_of_time,
        relationship_type=relationship,
        trust_level=trust,
        freshness_status=FreshnessStatus.NOT_APPLICABLE,
        limitations=limitations,
        provenance=ArtifactProvenance(
            producer="flowlens.decision.derivations",
            producer_version="w03-c02-v1",
            input_artifact_ids=tuple(item.evidence_id for item in selected),
            source_refs=refs,
            contract_versions=(VersionRef(name="w03-c02-derivations", version="v1"),),
            implementation_sha=None,
        ),
    )


def derive_observations(
    snapshot: StateSnapshot, source_evidence: tuple[Evidence, ...]
) -> tuple[Evidence, ...]:
    """Return only the frozen C02 derivations; never infer risk or causality."""
    by_row: dict[tuple[str, str], dict[str, Evidence]] = defaultdict(dict)
    for item in source_evidence:
        by_row[(item.source_entity, item.source_record_id)][item.source_field] = item
    order = by_row.get(("fact_sales_order", snapshot.order_id), {})
    quantity_evidence = order.get("order_quantity")
    id_evidence = order.get("sales_order_id")
    if (
        quantity_evidence is None
        or id_evidence is None
        or not isinstance(quantity_evidence.value, int)
    ):
        raise C02BuildError("DERIVATION_INPUT_MISSING", "BLOCKED_CONTRACT")
    order_quantity = quantity_evidence.value
    deliveries = [fields for (entity, _), fields in by_row.items() if entity == "fact_delivery"]
    delivery_values: list[Evidence] = []
    for fields in deliveries:
        value = fields.get("delivered_quantity")
        if value is None or not isinstance(value.value, int):
            raise C02BuildError("DERIVATION_INPUT_MISSING", "BLOCKED_CONTRACT")
        delivery_values.append(value)
    delivered = sum(item.value for item in delivery_values if isinstance(item.value, int))
    if delivered > order_quantity:
        raise C02BuildError("DELIVERY_QUANTITY_CONTRACT_VIOLATION", "BLOCKED_CONTRACT")
    first = _derive(
        snapshot,
        DERIVATION_IDS[0],
        snapshot.order_id,
        "delivered_quantity_as_of",
        delivered,
        (id_evidence, quantity_evidence, *delivery_values),
    )
    remaining = _derive(
        snapshot,
        DERIVATION_IDS[1],
        snapshot.order_id,
        "remaining_quantity_as_of",
        order_quantity - delivered,
        (quantity_evidence, first),
    )
    delivery_state = (
        "NOT_DELIVERED_AS_OF"
        if delivered == 0
        else "DELIVERED_AS_OF"
        if delivered == order_quantity
        else "PARTIALLY_DELIVERED_AS_OF"
    )
    third = _derive(
        snapshot,
        DERIVATION_IDS[2],
        snapshot.order_id,
        "delivery_state_as_of",
        delivery_state,
        (quantity_evidence, first),
    )
    results = [first, remaining, third]

    for entity, rule, field in (
        ("fact_work_order", DERIVATION_IDS[3], "work_order_state_as_of"),
        ("fact_operation", DERIVATION_IDS[4], "operation_state_as_of"),
    ):
        id_field = "work_order_id" if entity == "fact_work_order" else "operation_id"
        for (row_entity, row_id), fields in sorted(by_row.items()):
            if row_entity != entity:
                continue
            selected = [fields[id_field]]
            start = fields.get("actual_start_at")
            end = fields.get("actual_end_at")
            if start is not None:
                selected.append(start)
            if end is not None:
                selected.append(end)
            state_value = (
                "COMPLETED_AS_OF" if end else "IN_PROGRESS_AS_OF" if start else "NOT_STARTED_AS_OF"
            )
            results.append(_derive(snapshot, rule, row_id, field, state_value, selected))

    for (entity, row_id), fields in sorted(by_row.items()):
        if entity != "fact_purchase_order":
            continue
        ordered = fields.get("ordered_quantity")
        identifier = fields.get("purchase_order_id")
        if ordered is None or identifier is None:
            raise C02BuildError("DERIVATION_INPUT_MISSING", "BLOCKED_CONTRACT")
        receipt = fields.get("actual_receipt_at")
        received = fields.get("received_quantity")
        selected = [identifier, ordered]
        if receipt is None:
            receipt_state = "NOT_RECEIVED_AS_OF"
        else:
            if received is None or received.value is None or ordered.value is None:
                raise C02BuildError("DERIVATION_INPUT_MISSING", "BLOCKED_CONTRACT")
            selected.extend((receipt, received))
            if received.value > ordered.value:  # type: ignore[operator]
                raise C02BuildError("RECEIPT_QUANTITY_CONTRACT_VIOLATION", "BLOCKED_CONTRACT")
            receipt_state = (
                "RECEIVED_AS_OF" if received.value == ordered.value else "PARTIALLY_RECEIVED_AS_OF"
            )
        results.append(
            _derive(
                snapshot,
                DERIVATION_IDS[5],
                row_id,
                "purchase_order_receipt_state_as_of",
                receipt_state,
                selected,
            )
        )

    reworks_by_inspection: dict[str, list[dict[str, Evidence]]] = defaultdict(list)
    for (entity, _), fields in by_row.items():
        if entity == "fact_rework":
            inspection = fields.get("inspection_id")
            if inspection is not None and isinstance(inspection.value, str):
                reworks_by_inspection[inspection.value].append(fields)
    for (entity, row_id), fields in sorted(by_row.items()):
        if entity != "fact_quality_inspection":
            continue
        failed = fields.get("failed_quantity")
        identifier = fields.get("inspection_id")
        if failed is None or identifier is None or not isinstance(failed.value, int):
            raise C02BuildError("DERIVATION_INPUT_MISSING", "BLOCKED_CONTRACT")
        linked = [rw["rework_quantity"] for rw in reworks_by_inspection[row_id]]
        reworked = sum(item.value for item in linked if isinstance(item.value, int))
        results.append(
            _derive(
                snapshot,
                DERIVATION_IDS[6],
                row_id,
                "unresolved_failed_quantity_as_of",
                max(failed.value - reworked, 0),
                (identifier, failed, *linked),
            )
        )
    return tuple(sorted(results, key=lambda item: item.evidence_id))
