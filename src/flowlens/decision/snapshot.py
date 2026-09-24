"""DB-free immutable StateSnapshot assembly from authorized projected fields."""

from __future__ import annotations

from collections.abc import Iterable

from flowlens.decision.contracts import DecisionRun, StateSnapshot
from flowlens.decision.enums import UncertaintyStatus
from flowlens.decision.primitives import (
    ArtifactProvenance,
    EntityRef,
    SnapshotEntry,
    SourceRef,
    Uncertainty,
    VersionRef,
)
from flowlens.decision.serialization import (
    canonical_primitive,
    compute_snapshot_hash,
    derive_artifact_id,
)
from flowlens.decision.temporal import C02BuildError, ProjectedSourceField


def source_unknowns(
    work_order_count: int,
    material_requirement_count: int,
    required_material_ids: Iterable[str],
    inventory_material_ids: Iterable[str],
) -> tuple[Uncertainty, ...]:
    """Represent absent source observations without downstream Evidence IDs."""
    result: list[Uncertainty] = []
    if work_order_count == 0:
        result.append(
            Uncertainty(
                status=UncertaintyStatus.INSUFFICIENT_EVIDENCE,
                code="WORK_ORDER_EVIDENCE_MISSING",
                message="No target WorkOrder is available at decision time.",
                evidence_ids=(),
            )
        )
    elif material_requirement_count == 0:
        result.append(
            Uncertainty(
                status=UncertaintyStatus.INSUFFICIENT_EVIDENCE,
                code="MATERIAL_REQUIREMENT_EVIDENCE_MISSING",
                message="No target MaterialRequirement is available at decision time.",
                evidence_ids=(),
            )
        )
    present = set(inventory_material_ids)
    for material_id in sorted(set(required_material_ids) - present):
        result.append(
            Uncertainty(
                status=UncertaintyStatus.INSUFFICIENT_EVIDENCE,
                code="INVENTORY_EVIDENCE_MISSING",
                message=f"No eligible InventorySnapshot for material {material_id}.",
                evidence_ids=(),
            )
        )
    return tuple(sorted(result, key=lambda x: (x.status.value, x.code, x.message, x.evidence_ids)))


def build_state_snapshot(
    run: DecisionRun,
    projected_fields: Iterable[ProjectedSourceField],
    unknowns: tuple[Uncertainty, ...] = (),
) -> StateSnapshot:
    entries: list[SnapshotEntry] = []
    for item in projected_fields:
        if item.available_at > run.as_of_time:
            raise C02BuildError("TEMPORAL_ADMISSION_VIOLATION", "BLOCKED_TEMPORAL")
        source_ref = SourceRef(
            source_entity=item.source_entity,
            source_record_id=item.source_record_id,
            source_field=item.source_field,
            observed_at=item.observed_at,
            available_at=item.available_at,
        )
        entries.append(
            SnapshotEntry(
                entry_key=f"{item.source_entity}|{item.source_record_id}|{item.source_field}",
                entity=EntityRef(entity_type=item.source_entity, entity_id=item.source_record_id),
                field=item.source_field,
                value=item.value,
                observed_at=item.observed_at,
                available_at=item.available_at,
                source_ref=source_ref,
            )
        )
    entries.sort(key=lambda item: item.entry_key)
    if len({item.entry_key for item in entries}) != len(entries):
        raise C02BuildError("DUPLICATE_SOURCE_FIELD", "BLOCKED_CONTRACT")
    if any(item.evidence_ids for item in unknowns):
        raise C02BuildError("SNAPSHOT_UNKNOWN_EVIDENCE_CYCLE", "BLOCKED_CONTRACT")
    ordered_unknowns = tuple(
        sorted(unknowns, key=lambda x: (x.status.value, x.code, x.message, x.evidence_ids))
    )
    semantic: dict[str, object] = {
        "order_id": run.order_id,
        "as_of_time": run.as_of_time,
        "dataset_version": run.dataset_version,
        "dataset_hash": run.dataset_hash,
        "entries": tuple(entries),
        "unknowns": ordered_unknowns,
    }
    snapshot_hash = compute_snapshot_hash(semantic)
    refs = tuple(
        sorted(
            (item.source_ref for item in entries),
            key=lambda x: (
                x.source_entity,
                x.source_record_id,
                x.source_field,
                str(canonical_primitive(x.observed_at)) if x.observed_at else "",
                str(canonical_primitive(x.available_at)),
            ),
        )
    )
    provenance = ArtifactProvenance(
        producer="flowlens.decision.snapshot",
        producer_version="w03-c02-v1",
        input_artifact_ids=(run.run_id,),
        source_refs=refs,
        contract_versions=(
            VersionRef(name="w03-c02", version="v1"),
            VersionRef(name="w03-c02-source-matrix", version="v1"),
        ),
        implementation_sha=None,
    )
    return StateSnapshot(
        snapshot_id=derive_artifact_id(
            "state-snapshot",
            "state-snapshot.v1",
            {"run_id": run.run_id, "snapshot_hash": snapshot_hash},
        ),
        schema_version="state-snapshot.v1",
        run_id=run.run_id,
        order_id=run.order_id,
        as_of_time=run.as_of_time,
        dataset_version=run.dataset_version,
        dataset_hash=run.dataset_hash,
        snapshot_hash=snapshot_hash,
        entries=tuple(entries),
        unknowns=ordered_unknowns,
        provenance=provenance,
    )
