"""Pure C02 source Evidence, trust-preserving derivations, and unknowns."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from flowlens.decision.contracts import Evidence, EvidenceBundle, StateSnapshot
from flowlens.decision.derivations import derive_observations
from flowlens.decision.enums import FreshnessStatus, TrustLevel, UncertaintyStatus
from flowlens.decision.primitives import ArtifactProvenance, SourceRef, Uncertainty, VersionRef
from flowlens.decision.serialization import canonical_primitive, derive_artifact_id
from flowlens.decision.temporal import C02BuildError
from flowlens.decision.trust import classify_source


def _ref_key(ref: SourceRef) -> tuple[str, str, str, str, str]:
    return (
        ref.source_entity,
        ref.source_record_id,
        ref.source_field,
        str(canonical_primitive(ref.observed_at)) if ref.observed_at else "",
        str(canonical_primitive(ref.available_at)),
    )


def _source_evidence(snapshot: StateSnapshot) -> tuple[Evidence, ...]:
    result: list[Evidence] = []
    for entry in snapshot.entries:
        relationship, trust, freshness, limitations = classify_source(entry, snapshot.as_of_time)
        identity = {
            "run_id": snapshot.run_id,
            "snapshot_id": snapshot.snapshot_id,
            "source_entity": entry.source_ref.source_entity,
            "source_record_id": entry.source_ref.source_record_id,
            "source_field": entry.source_ref.source_field,
            "value": entry.value,
            "observed_at": entry.observed_at,
            "available_at": entry.available_at,
            "as_of_time": snapshot.as_of_time,
            "relationship_type": relationship,
            "trust_level": trust,
            "freshness_status": freshness,
        }
        result.append(
            Evidence(
                evidence_id=derive_artifact_id("evidence", "evidence.v1", identity),
                schema_version="evidence.v1",
                run_id=snapshot.run_id,
                snapshot_id=snapshot.snapshot_id,
                source_entity=entry.source_ref.source_entity,
                source_record_id=entry.source_ref.source_record_id,
                source_field=entry.source_ref.source_field,
                value=entry.value,
                observed_at=entry.observed_at,
                available_at=entry.available_at,
                as_of_time=snapshot.as_of_time,
                relationship_type=relationship,
                trust_level=trust,
                freshness_status=freshness,
                limitations=limitations,
                provenance=ArtifactProvenance(
                    producer="flowlens.decision.evidence",
                    producer_version="w03-c02-v1",
                    input_artifact_ids=(snapshot.snapshot_id,),
                    source_refs=(entry.source_ref,),
                    contract_versions=(
                        VersionRef(name="w03-c02-source-matrix", version="v1"),
                        VersionRef(name="w03-c02-trust-matrix", version="v1"),
                    ),
                    implementation_sha=None,
                ),
            )
        )
    return tuple(sorted(result, key=lambda item: item.evidence_id))


def _uncertainty(
    code: str,
    status: UncertaintyStatus,
    message: str,
    evidence: tuple[Evidence, ...] = (),
) -> Uncertainty:
    return Uncertainty(
        status=status,
        code=code,
        message=message,
        evidence_ids=tuple(sorted({item.evidence_id for item in evidence})),
    )


def _evidence_uncertainties(
    snapshot: StateSnapshot, evidence: tuple[Evidence, ...]
) -> tuple[Uncertainty, ...]:
    by_row: dict[tuple[str, str], dict[str, Evidence]] = defaultdict(dict)
    for item in evidence:
        by_row[(item.source_entity, item.source_record_id)][item.source_field] = item
    required_materials = sorted(
        {
            item.value
            for item in evidence
            if item.source_entity == "fact_material_requirement"
            and item.source_field == "material_id"
            and isinstance(item.value, str)
        }
    )
    result = list(snapshot.unknowns)
    for material_id in required_materials:
        po_rows = [
            fields
            for (entity, _), fields in by_row.items()
            if entity == "fact_purchase_order"
            and fields.get("material_id") is not None
            and fields["material_id"].value == material_id
        ]
        if not po_rows:
            result.append(
                _uncertainty(
                    "PROCUREMENT_EVIDENCE_NOT_AVAILABLE",
                    UncertaintyStatus.INSUFFICIENT_EVIDENCE,
                    f"No eligible PurchaseOrder for required material {material_id}.",
                )
            )
        else:
            refs = tuple(
                item
                for fields in po_rows
                for field, item in fields.items()
                if field in ("purchase_order_id", "material_id")
            )
            result.append(
                _uncertainty(
                    "PO_ALLOCATION_ASSOCIATIVE_ONLY",
                    UncertaintyStatus.ASSOCIATIVE_ONLY,
                    f"PurchaseOrders for material {material_id} are associative "
                    "to the target order.",
                    refs,
                )
            )
        inventory_rows = [
            fields
            for (entity, _), fields in by_row.items()
            if entity == "fact_inventory_snapshot"
            and fields.get("material_id") is not None
            and fields["material_id"].value == material_id
        ]
        if inventory_rows and not any(
            fields["snapshot_at"].freshness_status is FreshnessStatus.FRESH
            for fields in inventory_rows
        ):
            times = [fields["snapshot_at"].value for fields in inventory_rows]
            if not all(isinstance(value, datetime) for value in times):
                raise C02BuildError("TEMPORAL_ADMISSION_VIOLATION", "BLOCKED_TEMPORAL")
            latest = max(value for value in times if isinstance(value, datetime))
            latest_evidence = tuple(
                item
                for fields in inventory_rows
                if fields["snapshot_at"].value == latest
                for item in fields.values()
            )
            result.append(
                _uncertainty(
                    "MATERIAL_AVAILABILITY_CURRENT_STATE_UNKNOWN",
                    UncertaintyStatus.INSUFFICIENT_EVIDENCE,
                    f"No fresh inventory observation for required material {material_id}.",
                    latest_evidence,
                )
            )

    inspection_rows = {
        row_id: fields
        for (entity, row_id), fields in by_row.items()
        if entity == "fact_quality_inspection"
    }
    rework_rows = {
        row_id: fields for (entity, row_id), fields in by_row.items() if entity == "fact_rework"
    }
    work_order_exists = any(entity == "fact_work_order" for entity, _ in by_row)
    if work_order_exists and not inspection_rows:
        result.append(
            _uncertainty(
                "QUALITY_EVIDENCE_NOT_AVAILABLE",
                UncertaintyStatus.INSUFFICIENT_EVIDENCE,
                "No eligible QualityInspection exists for target WorkOrders.",
            )
        )
    if inspection_rows:
        refs = tuple(
            item
            for fields in (*inspection_rows.values(), *rework_rows.values())
            for item in fields.values()
        )
        result.append(
            _uncertainty(
                "QUALITY_FINALITY_UNKNOWN",
                UncertaintyStatus.UNKNOWN,
                "Formal quality finality is unknown because W2 has no release event.",
                refs,
            )
        )
    for inspection_id, fields in sorted(inspection_rows.items()):
        derived = by_row.get(
            ("c02_derivation", f"c02.unresolved_failed_quantity_as_of.v1|{inspection_id}"), {}
        )
        unresolved = derived.get("unresolved_failed_quantity_as_of")
        if unresolved is None or not isinstance(unresolved.value, int):
            raise C02BuildError("DERIVATION_INPUT_MISSING", "BLOCKED_CONTRACT")
        if unresolved.value > 0:
            linked = tuple(
                rw["rework_quantity"]
                for rw in rework_rows.values()
                if rw.get("inspection_id") is not None
                and rw["inspection_id"].value == inspection_id
            )
            failed = fields.get("failed_quantity")
            if failed is None:
                raise C02BuildError("DERIVATION_INPUT_MISSING", "BLOCKED_CONTRACT")
            result.append(
                _uncertainty(
                    "QUALITY_DISPOSITION_UNKNOWN",
                    UncertaintyStatus.UNRESOLVED_DISPOSITION,
                    f"Unresolved failed quantity for inspection {inspection_id} "
                    "has unknown disposition.",
                    (failed, *linked),
                )
            )
    unique = {
        (item.status.value, item.code, item.message, item.evidence_ids): item for item in result
    }
    return tuple(unique[key] for key in sorted(unique))


def build_evidence_bundle(snapshot: StateSnapshot) -> EvidenceBundle:
    source = _source_evidence(snapshot)
    derived = derive_observations(snapshot, source)
    evidence = tuple(sorted((*source, *derived), key=lambda item: item.evidence_id))
    if len({item.evidence_id for item in evidence}) != len(evidence):
        raise C02BuildError("DUPLICATE_EVIDENCE", "BLOCKED_CONTRACT")
    if any(item.trust_level is TrustLevel.FORBIDDEN_INFERENCE for item in evidence):
        raise C02BuildError("FORBIDDEN_INFERENCE_EVIDENCE", "BLOCKED_TRUST")
    uncertainties = _evidence_uncertainties(snapshot, evidence)
    identity = {
        "run_id": snapshot.run_id,
        "snapshot_id": snapshot.snapshot_id,
        "snapshot_hash": snapshot.snapshot_hash,
        "evidence_ids": tuple(item.evidence_id for item in evidence),
        "uncertainties": uncertainties,
    }
    refs = tuple(
        sorted({ref for item in evidence for ref in item.provenance.source_refs}, key=_ref_key)
    )
    return EvidenceBundle(
        evidence_bundle_id=derive_artifact_id("evidence-bundle", "evidence-bundle.v1", identity),
        schema_version="evidence-bundle.v1",
        run_id=snapshot.run_id,
        snapshot_id=snapshot.snapshot_id,
        snapshot_hash=snapshot.snapshot_hash,
        evidence=evidence,
        uncertainties=uncertainties,
        provenance=ArtifactProvenance(
            producer="flowlens.decision.evidence",
            producer_version="w03-c02-v1",
            input_artifact_ids=(snapshot.snapshot_id,),
            source_refs=refs,
            contract_versions=(
                VersionRef(name="w03-c02-derivations", version="v1"),
                VersionRef(name="w03-c02-source-matrix", version="v1"),
                VersionRef(name="w03-c02-trust-matrix", version="v1"),
            ),
            implementation_sha=None,
        ),
    )
