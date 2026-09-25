"""Closed-world validation for pure W03-C03 evaluators."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import Evidence, EvidenceBundle
from flowlens.decision.enums import TrustLevel
from flowlens.decision.primitives import SourceRef
from flowlens.decision.serialization import (
    canonical_primitive,
    derive_artifact_id,
    sha256_hex,
)
from flowlens.decision.trust import context_limitations

_C02_CONFLICT_CODES = frozenset(
    {
        "WORK_ORDER_PRODUCT_MISMATCH",
        "INSPECTION_OPERATION_WORK_ORDER_MISMATCH",
        "REWORK_INSPECTION_WORK_ORDER_MISMATCH",
    }
)


class C03BuildError(ValueError):
    """A deterministic fail-closed C03 input or policy error."""

    def __init__(self, code: str, state: str) -> None:
        self.code = code
        self.state = state
        super().__init__(f"{state}: {code}")


@dataclass(frozen=True, slots=True)
class EvidenceIndex:
    by_id: dict[str, Evidence]
    rows: dict[tuple[str, str], dict[str, Evidence]]

    def entity_rows(self, entity: str) -> tuple[tuple[str, dict[str, Evidence]], ...]:
        return tuple(
            (record_id, fields)
            for (row_entity, record_id), fields in sorted(self.rows.items())
            if row_entity == entity
        )


def source_ref_key(ref: SourceRef) -> tuple[str, str, str, str, str]:
    return (
        ref.source_entity,
        ref.source_record_id,
        ref.source_field,
        str(canonical_primitive(ref.observed_at)) if ref.observed_at else "",
        str(canonical_primitive(ref.available_at)),
    )


def _expected_context_id(context: DecisionContext) -> str:
    identity = {
        "run_id": context.run_id,
        "order_id": context.order_id,
        "snapshot_id": context.snapshot_id,
        "snapshot_hash": context.snapshot_hash,
        "evidence_bundle_id": context.evidence_bundle_id,
        "as_of_time": context.as_of_time,
        "selected_evidence_ids": context.selected_evidence_ids,
        "direct_evidence_ids": context.direct_evidence_ids,
        "derived_evidence_ids": context.derived_evidence_ids,
        "associative_evidence_ids": context.associative_evidence_ids,
        "uncertainties": context.uncertainties,
        "conflict_ids": tuple(item.conflict_id for item in context.conflicts),
        "limitations": context.limitations,
        "context_policy_version": context.context_policy_version,
    }
    return "ctx_" + sha256_hex(
        {
            "artifact_kind": "decision-context",
            "schema_version": context.schema_version,
            "identity": identity,
        }
    )


def _expected_conflict_codes(
    rows: dict[tuple[str, str], dict[str, Evidence]], context: DecisionContext
) -> tuple[str, ...]:
    result: list[str] = []
    order = rows.get(("fact_sales_order", context.order_id), {})
    order_product = order.get("product_id")
    for (entity, _), fields in sorted(rows.items()):
        if entity != "fact_work_order" or order_product is None:
            continue
        work_product = fields.get("product_id")
        if work_product is not None and work_product.value != order_product.value:
            result.append("WORK_ORDER_PRODUCT_MISMATCH")
    for (entity, _), fields in sorted(rows.items()):
        if entity != "fact_quality_inspection":
            continue
        operation_id = fields.get("operation_id")
        if operation_id is None or type(operation_id.value) is not str:
            continue
        operation = rows.get(("fact_operation", operation_id.value))
        if (
            operation is not None
            and operation.get("work_order_id") is not None
            and fields.get("work_order_id") is not None
            and operation["work_order_id"].value != fields["work_order_id"].value
        ):
            result.append("INSPECTION_OPERATION_WORK_ORDER_MISMATCH")
    for (entity, _), fields in sorted(rows.items()):
        if entity != "fact_rework":
            continue
        inspection_id = fields.get("inspection_id")
        if inspection_id is None or type(inspection_id.value) is not str:
            continue
        inspection = rows.get(("fact_quality_inspection", inspection_id.value))
        if (
            inspection is not None
            and inspection.get("work_order_id") is not None
            and fields.get("work_order_id") is not None
            and inspection["work_order_id"].value != fields["work_order_id"].value
        ):
            result.append("REWORK_INSPECTION_WORK_ORDER_MISMATCH")
    return tuple(sorted(result))


def _validate_conflicts(context: DecisionContext, evidence_id_set: set[str]) -> None:
    """Revalidate frozen C02 conflict values after artifact construction."""
    for conflict in context.conflicts:
        if (
            conflict.schema_version != "evidence-conflict.v1"
            or conflict.run_id != context.run_id
            or conflict.snapshot_id != context.snapshot_id
            or conflict.conflict_code not in _C02_CONFLICT_CODES
            or conflict.critical is not True
            or conflict.resolution_status != "UNRESOLVED"
            or not conflict.evidence_ids
            or tuple(sorted(conflict.evidence_ids)) != conflict.evidence_ids
            or len(set(conflict.evidence_ids)) != len(conflict.evidence_ids)
            or not set(conflict.evidence_ids) <= evidence_id_set
        ):
            raise C03BuildError("C03_NONCANONICAL_C02_CONTEXT", "BLOCKED_CONTRACT")
        identity = {
            "run_id": conflict.run_id,
            "snapshot_id": conflict.snapshot_id,
            "conflict_code": conflict.conflict_code,
            "evidence_ids": conflict.evidence_ids,
            "critical": conflict.critical,
            "resolution_status": conflict.resolution_status,
        }
        expected_id = "conf_" + sha256_hex(
            {
                "artifact_kind": "evidence-conflict",
                "schema_version": conflict.schema_version,
                "identity": identity,
            }
        )
        if conflict.conflict_id != expected_id:
            raise C03BuildError("C03_NONCANONICAL_C02_CONTEXT", "BLOCKED_CONTRACT")


def validate_c03_inputs(bundle: EvidenceBundle, context: DecisionContext) -> EvidenceIndex:
    if not isinstance(bundle, EvidenceBundle) or not isinstance(context, DecisionContext):
        raise C03BuildError("C03_RULE_INPUT_INVALID", "BLOCKED_CONTRACT")
    if (
        type(context.as_of_time) is not datetime
        or context.as_of_time.tzinfo is None
        or context.as_of_time.utcoffset() is None
    ):
        raise C03BuildError("C03_TEMPORAL_INPUT_INVALID", "BLOCKED_TEMPORAL")
    if (
        context.schema_version != "decision-context.v1"
        or context.context_policy_version != "w03-c02-context.v1"
        or context.context_id != _expected_context_id(context)
    ):
        raise C03BuildError("C03_NONCANONICAL_C02_CONTEXT", "BLOCKED_CONTRACT")
    if (
        bundle.run_id != context.run_id
        or bundle.snapshot_id != context.snapshot_id
        or bundle.snapshot_hash != context.snapshot_hash
        or bundle.evidence_bundle_id != context.evidence_bundle_id
    ):
        raise C03BuildError("C03_BINDING_MISMATCH", "BLOCKED_CONTRACT")
    evidence_ids = tuple(item.evidence_id for item in bundle.evidence)
    if tuple(sorted(evidence_ids)) != evidence_ids or len(set(evidence_ids)) != len(evidence_ids):
        raise C03BuildError("C03_BINDING_MISMATCH", "BLOCKED_CONTRACT")
    if context.selected_evidence_ids != evidence_ids:
        raise C03BuildError("C03_BINDING_MISMATCH", "BLOCKED_CONTRACT")
    if context.uncertainties != bundle.uncertainties:
        raise C03BuildError("C03_BINDING_MISMATCH", "BLOCKED_CONTRACT")
    evidence_id_set = set(evidence_ids)
    if any(not set(item.evidence_ids) <= evidence_id_set for item in bundle.uncertainties):
        raise C03BuildError("C03_BINDING_MISMATCH", "BLOCKED_CONTRACT")
    bundle_identity = {
        "run_id": bundle.run_id,
        "snapshot_id": bundle.snapshot_id,
        "snapshot_hash": bundle.snapshot_hash,
        "evidence_ids": evidence_ids,
        "uncertainties": bundle.uncertainties,
    }
    if (
        bundle.schema_version != "evidence-bundle.v1"
        or bundle.evidence_bundle_id
        != derive_artifact_id("evidence-bundle", "evidence-bundle.v1", bundle_identity)
    ):
        raise C03BuildError("C03_BINDING_MISMATCH", "BLOCKED_CONTRACT")

    expected_partitions = {
        TrustLevel.DIRECT_FACT: tuple(
            item.evidence_id
            for item in bundle.evidence
            if item.trust_level is TrustLevel.DIRECT_FACT
        ),
        TrustLevel.DERIVED_FACT: tuple(
            item.evidence_id
            for item in bundle.evidence
            if item.trust_level is TrustLevel.DERIVED_FACT
        ),
        TrustLevel.ASSOCIATIVE_EVIDENCE: tuple(
            item.evidence_id
            for item in bundle.evidence
            if item.trust_level is TrustLevel.ASSOCIATIVE_EVIDENCE
        ),
    }
    if (
        context.direct_evidence_ids != expected_partitions[TrustLevel.DIRECT_FACT]
        or context.derived_evidence_ids != expected_partitions[TrustLevel.DERIVED_FACT]
        or context.associative_evidence_ids != expected_partitions[TrustLevel.ASSOCIATIVE_EVIDENCE]
    ):
        raise C03BuildError("C03_NONCANONICAL_C02_CONTEXT", "BLOCKED_CONTRACT")

    rows: dict[tuple[str, str], dict[str, Evidence]] = defaultdict(dict)
    for item in bundle.evidence:
        if item.trust_level in (TrustLevel.UNKNOWN, TrustLevel.FORBIDDEN_INFERENCE):
            raise C03BuildError("C03_UNTRUSTED_FACT_INPUT", "BLOCKED_TRUST")
        if (
            item.run_id != context.run_id
            or item.snapshot_id != context.snapshot_id
            or item.as_of_time != context.as_of_time
        ):
            raise C03BuildError("C03_BINDING_MISMATCH", "BLOCKED_CONTRACT")
        for value in (item.available_at, item.observed_at, item.value):
            if isinstance(value, datetime) and (
                type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None
            ):
                raise C03BuildError("C03_TEMPORAL_INPUT_INVALID", "BLOCKED_TEMPORAL")
        if item.available_at > context.as_of_time or (
            item.observed_at is not None and item.observed_at > context.as_of_time
        ):
            raise C03BuildError("C03_TEMPORAL_INPUT_INVALID", "BLOCKED_TEMPORAL")
        evidence_identity = {
            "run_id": item.run_id,
            "snapshot_id": item.snapshot_id,
            "source_entity": item.source_entity,
            "source_record_id": item.source_record_id,
            "source_field": item.source_field,
            "value": item.value,
            "observed_at": item.observed_at,
            "available_at": item.available_at,
            "as_of_time": item.as_of_time,
            "relationship_type": item.relationship_type,
            "trust_level": item.trust_level,
            "freshness_status": item.freshness_status,
        }
        if item.schema_version != "evidence.v1" or item.evidence_id != derive_artifact_id(
            "evidence", "evidence.v1", evidence_identity
        ):
            raise C03BuildError("C03_BINDING_MISMATCH", "BLOCKED_CONTRACT")
        key = (item.source_entity, item.source_record_id)
        if item.source_field in rows[key]:
            raise C03BuildError("C03_DUPLICATE_EVIDENCE_KEY", "BLOCKED_CONTRACT")
        rows[key][item.source_field] = item

    expected_limitations = tuple(
        sorted(
            {
                *context_limitations(),
                *(limitation for item in bundle.evidence for limitation in item.limitations),
            },
            key=lambda item: (item.code, item.message),
        )
    )
    if context.limitations != expected_limitations:
        raise C03BuildError("C03_NONCANONICAL_C02_CONTEXT", "BLOCKED_CONTRACT")
    _validate_conflicts(context, evidence_id_set)
    if tuple(sorted(item.conflict_code for item in context.conflicts)) != _expected_conflict_codes(
        dict(rows), context
    ):
        raise C03BuildError("C03_NONCANONICAL_C02_CONTEXT", "BLOCKED_CONTRACT")

    if any(
        conflict.critical and conflict.resolution_status == "UNRESOLVED"
        for conflict in context.conflicts
    ):
        raise C03BuildError("C03_CRITICAL_CONFLICT", "BLOCKED_TRUST")
    return EvidenceIndex(
        by_id={item.evidence_id: item for item in bundle.evidence}, rows=dict(rows)
    )


def evidence_for_entities(index: EvidenceIndex, entities: tuple[str, ...]) -> tuple[Evidence, ...]:
    selected = (item for item in index.by_id.values() if item.source_entity in set(entities))
    return tuple(sorted(selected, key=lambda item: item.evidence_id))


def source_refs_for(evidence: tuple[Evidence, ...]) -> tuple[SourceRef, ...]:
    return tuple(
        sorted(
            {ref for item in evidence for ref in item.provenance.source_refs},
            key=source_ref_key,
        )
    )
