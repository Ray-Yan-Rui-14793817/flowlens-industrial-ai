"""Immutable C02 conflict and lossless DecisionContext artifacts."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from flowlens.decision.contracts import Evidence, EvidenceBundle, StateSnapshot
from flowlens.decision.enums import TrustLevel
from flowlens.decision.primitives import (
    ArtifactProvenance,
    Limitation,
    SourceRef,
    Uncertainty,
    Validated,
    VersionRef,
    validate_artifact_id,
    validate_sorted_unique,
)
from flowlens.decision.serialization import canonical_primitive, sha256_hex
from flowlens.decision.temporal import C02BuildError
from flowlens.decision.trust import context_limitations


def _ref_key(ref: SourceRef) -> tuple[str, str, str, str, str]:
    return (
        ref.source_entity,
        ref.source_record_id,
        ref.source_field,
        str(canonical_primitive(ref.observed_at)) if ref.observed_at else "",
        str(canonical_primitive(ref.available_at)),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceConflict(Validated):
    conflict_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    conflict_code: str
    evidence_ids: tuple[str, ...]
    critical: bool
    resolution_status: str
    message: str
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        Validated.__post_init__(self)
        if self.schema_version != "evidence-conflict.v1" or self.resolution_status != "UNRESOLVED":
            raise ValueError("invalid C02 conflict schema or resolution")
        if (
            self.conflict_code
            not in (
                "WORK_ORDER_PRODUCT_MISMATCH",
                "INSPECTION_OPERATION_WORK_ORDER_MISMATCH",
                "REWORK_INSPECTION_WORK_ORDER_MISMATCH",
            )
            or not self.critical
        ):
            raise ValueError("unsupported C02 conflict")
        validate_sorted_unique(self.evidence_ids, lambda value: value, "evidence_ids")
        if not self.evidence_ids:
            raise ValueError("conflict requires supporting evidence")
        expected = "conf_" + sha256_hex(
            {
                "artifact_kind": "evidence-conflict",
                "schema_version": self.schema_version,
                "identity": {
                    "run_id": self.run_id,
                    "snapshot_id": self.snapshot_id,
                    "conflict_code": self.conflict_code,
                    "evidence_ids": self.evidence_ids,
                    "critical": self.critical,
                    "resolution_status": self.resolution_status,
                },
            }
        )
        validate_artifact_id(self.conflict_id, "conf_", expected)


def _conflict(
    snapshot: StateSnapshot, code: str, items: tuple[Evidence, ...], message: str
) -> EvidenceConflict:
    ids = tuple(sorted({item.evidence_id for item in items}))
    refs = tuple(
        sorted({ref for item in items for ref in item.provenance.source_refs}, key=_ref_key)
    )
    identity = {
        "run_id": snapshot.run_id,
        "snapshot_id": snapshot.snapshot_id,
        "conflict_code": code,
        "evidence_ids": ids,
        "critical": True,
        "resolution_status": "UNRESOLVED",
    }
    return EvidenceConflict(
        conflict_id="conf_"
        + sha256_hex(
            {
                "artifact_kind": "evidence-conflict",
                "schema_version": "evidence-conflict.v1",
                "identity": identity,
            }
        ),
        schema_version="evidence-conflict.v1",
        run_id=snapshot.run_id,
        snapshot_id=snapshot.snapshot_id,
        conflict_code=code,
        evidence_ids=ids,
        critical=True,
        resolution_status="UNRESOLVED",
        message=message,
        provenance=ArtifactProvenance(
            producer="flowlens.decision.context",
            producer_version="w03-c02-v1",
            input_artifact_ids=ids,
            source_refs=refs,
            contract_versions=(VersionRef(name="w03-c02-context", version="v1"),),
            implementation_sha=None,
        ),
    )


def detect_conflicts(
    snapshot: StateSnapshot, bundle: EvidenceBundle
) -> tuple[EvidenceConflict, ...]:
    if bundle.snapshot_id != snapshot.snapshot_id:
        raise C02BuildError("SNAPSHOT_BINDING_MISMATCH", "BLOCKED_CONTRACT")
    rows: dict[tuple[str, str], dict[str, Evidence]] = defaultdict(dict)
    for item in bundle.evidence:
        rows[(item.source_entity, item.source_record_id)][item.source_field] = item
    target_product = rows[("fact_sales_order", snapshot.order_id)].get("product_id")
    if target_product is None:
        raise C02BuildError("DIRECT_REFERENCE_MISSING", "BLOCKED_CONTRACT")
    result: list[EvidenceConflict] = []
    for (entity, row_id), fields in sorted(rows.items()):
        if entity == "fact_work_order" and fields["product_id"].value != target_product.value:
            result.append(
                _conflict(
                    snapshot,
                    "WORK_ORDER_PRODUCT_MISMATCH",
                    (target_product, fields["product_id"]),
                    f"WorkOrder {row_id} product differs from target SalesOrder product.",
                )
            )
        if entity == "fact_quality_inspection":
            operation = fields.get("operation_id")
            if operation is not None and isinstance(operation.value, str):
                operation_fields = rows.get(("fact_operation", operation.value))
                if operation_fields is not None and (
                    operation_fields["work_order_id"].value != fields["work_order_id"].value
                ):
                    result.append(
                        _conflict(
                            snapshot,
                            "INSPECTION_OPERATION_WORK_ORDER_MISMATCH",
                            (operation, fields["work_order_id"], operation_fields["work_order_id"]),
                            f"Inspection {row_id} and its Operation have different WorkOrders.",
                        )
                    )
        if entity == "fact_rework":
            inspection_id = fields["inspection_id"].value
            if isinstance(inspection_id, str):
                inspection_fields = rows.get(("fact_quality_inspection", inspection_id))
                if inspection_fields is not None and (
                    inspection_fields["work_order_id"].value != fields["work_order_id"].value
                ):
                    result.append(
                        _conflict(
                            snapshot,
                            "REWORK_INSPECTION_WORK_ORDER_MISMATCH",
                            (
                                fields["inspection_id"],
                                fields["work_order_id"],
                                inspection_fields["work_order_id"],
                            ),
                            f"Rework {row_id} and its Inspection have different WorkOrders.",
                        )
                    )
    return tuple(sorted(result, key=lambda item: item.conflict_id))


@dataclass(frozen=True, slots=True, kw_only=True)
class DecisionContext(Validated):
    context_id: str
    schema_version: str
    run_id: str
    order_id: str
    snapshot_id: str
    snapshot_hash: str
    evidence_bundle_id: str
    as_of_time: datetime
    selected_evidence_ids: tuple[str, ...]
    direct_evidence_ids: tuple[str, ...]
    derived_evidence_ids: tuple[str, ...]
    associative_evidence_ids: tuple[str, ...]
    uncertainties: tuple[Uncertainty, ...]
    conflicts: tuple[EvidenceConflict, ...]
    limitations: tuple[Limitation, ...]
    context_policy_version: str
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        Validated.__post_init__(self)
        if (
            self.schema_version != "decision-context.v1"
            or self.context_policy_version != "w03-c02-context.v1"
        ):
            raise ValueError("invalid C02 context schema or policy")
        for label in (
            "selected_evidence_ids",
            "direct_evidence_ids",
            "derived_evidence_ids",
            "associative_evidence_ids",
        ):
            validate_sorted_unique(getattr(self, label), lambda value: value, label)
        partitions = (
            set(self.direct_evidence_ids),
            set(self.derived_evidence_ids),
            set(self.associative_evidence_ids),
        )
        if (
            partitions[0] & partitions[1]
            or partitions[0] & partitions[2]
            or partitions[1] & partitions[2]
            or set(self.selected_evidence_ids) != set.union(*partitions)
        ):
            raise ValueError("DecisionContext trust partitions are inconsistent")
        validate_sorted_unique(self.conflicts, lambda item: item.conflict_id, "conflicts")
        validate_sorted_unique(
            self.limitations, lambda item: (item.code, item.message), "limitations"
        )
        validate_sorted_unique(
            self.uncertainties,
            lambda item: (item.status.value, item.code, item.message, item.evidence_ids),
            "uncertainties",
        )
        identity = {
            "run_id": self.run_id,
            "order_id": self.order_id,
            "snapshot_id": self.snapshot_id,
            "snapshot_hash": self.snapshot_hash,
            "evidence_bundle_id": self.evidence_bundle_id,
            "as_of_time": self.as_of_time,
            "selected_evidence_ids": self.selected_evidence_ids,
            "direct_evidence_ids": self.direct_evidence_ids,
            "derived_evidence_ids": self.derived_evidence_ids,
            "associative_evidence_ids": self.associative_evidence_ids,
            "uncertainties": self.uncertainties,
            "conflict_ids": tuple(item.conflict_id for item in self.conflicts),
            "limitations": self.limitations,
            "context_policy_version": self.context_policy_version,
        }
        expected = "ctx_" + sha256_hex(
            {
                "artifact_kind": "decision-context",
                "schema_version": self.schema_version,
                "identity": identity,
            }
        )
        validate_artifact_id(self.context_id, "ctx_", expected)


def build_decision_context(snapshot: StateSnapshot, bundle: EvidenceBundle) -> DecisionContext:
    if (
        bundle.run_id != snapshot.run_id
        or bundle.snapshot_id != snapshot.snapshot_id
        or bundle.snapshot_hash != snapshot.snapshot_hash
    ):
        raise C02BuildError("SNAPSHOT_BINDING_MISMATCH", "BLOCKED_CONTRACT")
    selected = tuple(
        item
        for item in bundle.evidence
        if item.trust_level
        in (TrustLevel.DIRECT_FACT, TrustLevel.DERIVED_FACT, TrustLevel.ASSOCIATIVE_EVIDENCE)
    )
    if len(selected) != len(bundle.evidence):
        raise C02BuildError("FORBIDDEN_OR_UNKNOWN_EVIDENCE", "BLOCKED_TRUST")
    ids = tuple(sorted(item.evidence_id for item in selected))
    direct = tuple(
        sorted(item.evidence_id for item in selected if item.trust_level is TrustLevel.DIRECT_FACT)
    )
    derived = tuple(
        sorted(item.evidence_id for item in selected if item.trust_level is TrustLevel.DERIVED_FACT)
    )
    associative = tuple(
        sorted(
            item.evidence_id
            for item in selected
            if item.trust_level is TrustLevel.ASSOCIATIVE_EVIDENCE
        )
    )
    conflicts = detect_conflicts(snapshot, bundle)
    evidence_ids = set(ids)
    if any(not set(conflict.evidence_ids) <= evidence_ids for conflict in conflicts):
        raise C02BuildError("CONFLICT_EVIDENCE_MISSING", "BLOCKED_CONTRACT")
    limitations = tuple(
        sorted(
            {
                *context_limitations(),
                *(limitation for item in selected for limitation in item.limitations),
            },
            key=lambda item: (item.code, item.message),
        )
    )
    identity = {
        "run_id": snapshot.run_id,
        "order_id": snapshot.order_id,
        "snapshot_id": snapshot.snapshot_id,
        "snapshot_hash": snapshot.snapshot_hash,
        "evidence_bundle_id": bundle.evidence_bundle_id,
        "as_of_time": snapshot.as_of_time,
        "selected_evidence_ids": ids,
        "direct_evidence_ids": direct,
        "derived_evidence_ids": derived,
        "associative_evidence_ids": associative,
        "uncertainties": bundle.uncertainties,
        "conflict_ids": tuple(item.conflict_id for item in conflicts),
        "limitations": limitations,
        "context_policy_version": "w03-c02-context.v1",
    }
    refs = tuple(
        sorted({ref for item in selected for ref in item.provenance.source_refs}, key=_ref_key)
    )
    provenance = ArtifactProvenance(
        producer="flowlens.decision.context",
        producer_version="w03-c02-v1",
        input_artifact_ids=tuple(
            sorted(
                (
                    snapshot.snapshot_id,
                    bundle.evidence_bundle_id,
                    *(item.conflict_id for item in conflicts),
                )
            )
        ),
        source_refs=refs,
        contract_versions=(
            VersionRef(name="w03-c02", version="v1"),
            VersionRef(name="w03-c02-context", version="v1"),
            VersionRef(name="w03-c02-derivations", version="v1"),
            VersionRef(name="w03-c02-source-matrix", version="v1"),
            VersionRef(name="w03-c02-trust-matrix", version="v1"),
        ),
        implementation_sha=None,
    )
    return DecisionContext(
        context_id="ctx_"
        + sha256_hex(
            {
                "artifact_kind": "decision-context",
                "schema_version": "decision-context.v1",
                "identity": identity,
            }
        ),
        schema_version="decision-context.v1",
        run_id=snapshot.run_id,
        order_id=snapshot.order_id,
        snapshot_id=snapshot.snapshot_id,
        snapshot_hash=snapshot.snapshot_hash,
        evidence_bundle_id=bundle.evidence_bundle_id,
        as_of_time=snapshot.as_of_time,
        selected_evidence_ids=ids,
        direct_evidence_ids=direct,
        derived_evidence_ids=derived,
        associative_evidence_ids=associative,
        uncertainties=bundle.uncertainties,
        conflicts=conflicts,
        limitations=limitations,
        context_policy_version="w03-c02-context.v1",
        provenance=provenance,
    )
