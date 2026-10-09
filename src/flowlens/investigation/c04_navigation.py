"""Sole C04 PostgreSQL reader: closed traversal, temporal admission and no writes."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime
from types import MappingProxyType
from typing import Any, Final, cast

from sqlalchemy import case as sql_case
from sqlalchemy import select, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.selectable import FromClause, Select

from flowlens.data.models import (
    DatasetVersion,
    Delivery,
    MaterialRequirement,
    Operation,
    PurchaseOrder,
    QualityInspection,
    Rework,
    SalesOrder,
    WorkCenter,
    WorkOrder,
)
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.enums import FreshnessStatus, TrustLevel
from flowlens.decision.primitives import (
    EntityRef,
    ScalarValue,
    SnapshotEntry,
    SourceRef,
    validate_aware_datetime,
    validate_structural_dataclass,
)
from flowlens.decision.serialization import canonical_json_bytes, sha256_hex
from flowlens.decision.temporal import (
    BUSINESS_TIMEZONE,
    SOURCE_FIELDS,
    C02BuildError,
    ProjectedSourceField,
    project_record,
    validate_as_of,
)
from flowlens.decision.trust import classify_source
from flowlens.investigation.c04_queries import (
    C04_EVIDENCE_BINDING_MISMATCH,
    C04_QUERY_NOT_AUTHORIZED,
    C04_READ_ONLY_VIOLATION,
    C04_RESULT_LIMIT_EXCEEDED,
    C04_SOURCE_CONTEXT_MISMATCH,
    C04_SOURCE_UNAVAILABLE,
    C04_TEMPORAL_VIOLATION,
    C04EvidenceError,
    validate_evidence_query_specs,
)
from flowlens.investigation.c04_registry import (
    C04_MAX_OBSERVATIONS_PER_SLICE,
    C04_MAX_RECORDS_PER_QUERY,
    C04_NAVIGATION_CONTRACT_VERSION,
    C04_SOURCE_REGISTRY,
)
from flowlens.investigation.contracts import (
    EvidenceObservation,
    EvidenceQuerySpec,
    EvidenceSlice,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
)

_SO: Final[FromClause] = SalesOrder.__table__
_WO: Final[FromClause] = WorkOrder.__table__
_OP: Final[FromClause] = Operation.__table__
_MR: Final[FromClause] = MaterialRequirement.__table__
_PO: Final[FromClause] = PurchaseOrder.__table__
_QI: Final[FromClause] = QualityInspection.__table__
_RW: Final[FromClause] = Rework.__table__
_DV: Final[FromClause] = Delivery.__table__
_WC: Final[FromClause] = WorkCenter.__table__
_ORDER_WORK: Final = _SO.join(_WO, _WO.c.sales_order_id == _SO.c.sales_order_id)
_ORDER_OPERATION: Final = _ORDER_WORK.join(_OP, _OP.c.work_order_id == _WO.c.work_order_id)
_ORDER_MATERIAL: Final = _ORDER_WORK.join(_MR, _MR.c.work_order_id == _WO.c.work_order_id)
_TABLES: Final = MappingProxyType(
    {
        "dim_work_center": _WC,
        "fact_delivery": _DV,
        "fact_material_requirement": _MR,
        "fact_operation": _OP,
        "fact_purchase_order": _PO,
        "fact_quality_inspection": _QI,
        "fact_rework": _RW,
        "fact_sales_order": _SO,
        "fact_work_order": _WO,
    }
)
_TRAVERSALS: Final = MappingProxyType(
    {
        "dim_work_center": _ORDER_OPERATION.join(_WC, _WC.c.work_center_id == _OP.c.work_center_id),
        "fact_delivery": _SO.join(_DV, _DV.c.sales_order_id == _SO.c.sales_order_id),
        "fact_material_requirement": _ORDER_MATERIAL,
        "fact_operation": _ORDER_OPERATION,
        "fact_purchase_order": _ORDER_MATERIAL.join(_PO, _PO.c.material_id == _MR.c.material_id),
        "fact_quality_inspection": _ORDER_WORK.join(
            _QI, _QI.c.work_order_id == _WO.c.work_order_id
        ),
        "fact_rework": _ORDER_WORK.join(_RW, _RW.c.work_order_id == _WO.c.work_order_id),
        "fact_sales_order": _SO,
        "fact_work_order": _ORDER_WORK,
    }
)
_OWNERS: Final = MappingProxyType(
    {
        "dim_work_center": (_SO, _WO, _OP, _WC),
        "fact_delivery": (_SO, _DV),
        "fact_material_requirement": (_SO, _WO, _MR),
        "fact_operation": (_SO, _WO, _OP),
        "fact_purchase_order": (_SO, _WO, _MR, _PO),
        "fact_quality_inspection": (_SO, _WO, _QI),
        "fact_rework": (_SO, _WO, _RW),
        "fact_sales_order": (_SO,),
        "fact_work_order": (_SO, _WO),
    }
)
_EVENT_ROWS: Final = MappingProxyType(
    {
        "fact_sales_order": "order_at",
        "fact_purchase_order": "ordered_at",
        "fact_quality_inspection": "inspection_at",
        "fact_rework": "rework_start_at",
        "fact_delivery": "delivery_at",
    }
)
if not (tuple(_TABLES) == tuple(_TRAVERSALS) == tuple(_OWNERS) == tuple(C04_SOURCE_REGISTRY)):
    raise ValueError("C04 adapters must match the closed source registry")


@dataclass(frozen=True, slots=True)
class _SourceContext:
    period_start: date
    target_order_at: datetime


def _source_context(connection: Connection, packet: DecisionPacket) -> _SourceContext:
    try:
        revisions = (
            connection.execute(text("SELECT version_num FROM alembic_version")).scalars().all()
        )
    except SQLAlchemyError:
        raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH) from None
    if revisions != ["0002_industrial_data_foundation"]:
        raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH)
    dataset = DatasetVersion.__table__
    versions = (
        connection.execute(
            select(
                dataset.c.dataset_version_id,
                dataset.c.content_hash,
                dataset.c.period_start,
                dataset.c.period_end,
            )
            .order_by(dataset.c.dataset_version_id)
            .limit(2)
        )
        .mappings()
        .all()
    )
    if len(versions) != 1:
        raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH)
    version = versions[0]
    if (
        version["dataset_version_id"] != packet.run.dataset_version
        or version["content_hash"] != packet.run.dataset_hash
        or type(version["period_start"]) is not date
        or type(version["period_end"]) is not date
    ):
        raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH)
    try:
        validate_as_of(packet.run.as_of_time, version["period_start"], version["period_end"])
    except (TypeError, ValueError):
        raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH) from None
    orders = (
        connection.execute(
            select(
                _SO.c.dataset_version_id,
                _SO.c.sales_order_id,
                _SO.c.order_at,
            )
            .where(
                _SO.c.dataset_version_id == packet.run.dataset_version,
                _SO.c.sales_order_id == packet.run.order_id,
            )
            .order_by(_SO.c.sales_order_id)
            .limit(2)
        )
        .mappings()
        .all()
    )
    if len(orders) != 1 or (
        orders[0]["dataset_version_id"] != packet.run.dataset_version
        or orders[0]["sales_order_id"] != packet.run.order_id
        or type(orders[0]["order_at"]) is not datetime
    ):
        raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH)
    order_at = orders[0]["order_at"]
    try:
        validate_aware_datetime(order_at, "order_at")
        if order_at > packet.run.as_of_time:
            raise ValueError("unavailable target")
    except (TypeError, ValueError):
        raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH) from None
    return _SourceContext(version["period_start"], order_at)


def _column(family: str, field: str, as_of: datetime) -> ColumnElement[Any]:
    table = _TABLES[family]
    gate: str | None = None
    if family in ("fact_work_order", "fact_operation"):
        if field in ("actual_start_at", "actual_end_at"):
            gate = field
        elif family == "fact_work_order" and field == "completed_quantity":
            gate = "actual_end_at"
    elif family == "fact_purchase_order" and field in ("actual_receipt_at", "received_quantity"):
        gate = "actual_receipt_at"
    elif family == "fact_rework" and field == "rework_end_at":
        gate = field
    return (
        sql_case((table.c[gate] <= as_of, table.c[field]), else_=None).label(field)
        if gate is not None
        else table.c[field]
    )


def _statement(family: str, packet: DecisionPacket) -> Select[Any]:
    if family not in C04_SOURCE_REGISTRY:
        raise C04EvidenceError(C04_QUERY_NOT_AUTHORIZED)
    table = _TABLES[family]
    at = packet.run.as_of_time
    columns = [
        table.c.dataset_version_id,
        *(_column(family, field, at) for field in SOURCE_FIELDS[family]),
    ]
    conditions = [
        owner.c.dataset_version_id == packet.run.dataset_version for owner in _OWNERS[family]
    ]
    conditions.extend((_SO.c.sales_order_id == packet.run.order_id, _SO.c.order_at <= at))
    if family in _EVENT_ROWS:
        conditions.append(table.c[_EVENT_ROWS[family]] <= at)
    elif family == "dim_work_center":
        conditions.append(table.c.active_from <= at.astimezone(BUSINESS_TIMEZONE).date())
    return (
        select(*columns)
        .select_from(_TRAVERSALS[family])
        .where(*conditions)
        .distinct()
        .order_by(
            table.c[C04_SOURCE_REGISTRY[family].primary_key],
        )
        .limit(C04_MAX_RECORDS_PER_QUERY + 1)
    )


def _records(
    connection: Connection,
    packet: DecisionPacket,
    family: str,
) -> tuple[tuple[str, dict[str, ScalarValue]], ...]:
    rows = connection.execute(_statement(family, packet)).mappings().all()
    key = C04_SOURCE_REGISTRY[family].primary_key
    unique: dict[str, dict[str, ScalarValue]] = {}
    for row in rows:
        record_id = row[key]
        if row["dataset_version_id"] != packet.run.dataset_version or (
            type(record_id) is not str or not record_id or record_id != record_id.strip()
        ):
            raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH)
        values = {field: cast(ScalarValue, row[field]) for field in SOURCE_FIELDS[family]}
        if record_id in unique and canonical_json_bytes(unique[record_id]) != canonical_json_bytes(
            values,
        ):
            raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH)
        unique[record_id] = values
        if len(unique) > C04_MAX_RECORDS_PER_QUERY:
            raise C04EvidenceError(C04_RESULT_LIMIT_EXCEEDED)
    return tuple((record_id, unique[record_id]) for record_id in sorted(unique))


def _observation(
    packet: DecisionPacket,
    query: EvidenceQuerySpec,
    projected: ProjectedSourceField,
) -> EvidenceObservation:
    if (
        projected.source_entity != query.source_family_code
        or projected.source_field not in query.requested_fields
    ):
        raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH)
    try:
        validate_aware_datetime(projected.available_at, "available_at")
        if projected.observed_at is not None:
            validate_aware_datetime(projected.observed_at, "observed_at")
        if projected.available_at > query.as_of_time or (
            projected.observed_at is not None and projected.observed_at > query.as_of_time
        ):
            raise ValueError("unavailable observation")
    except (AttributeError, TypeError, ValueError):
        raise C04EvidenceError(C04_TEMPORAL_VIOLATION) from None
    ref = SourceRef(
        source_entity=projected.source_entity,
        source_record_id=projected.source_record_id,
        source_field=projected.source_field,
        observed_at=projected.observed_at,
        available_at=projected.available_at,
    )
    entry = SnapshotEntry(
        entry_key=f"{projected.source_entity}|{projected.source_record_id}|{projected.source_field}",
        entity=EntityRef(entity_type=projected.source_entity, entity_id=projected.source_record_id),
        field=projected.source_field,
        value=projected.value,
        observed_at=projected.observed_at,
        available_at=projected.available_at,
        source_ref=ref,
    )
    relationship, trust, freshness, _limitations = classify_source(entry, query.as_of_time)
    if (
        type(trust) is not TrustLevel
        or type(freshness) is not FreshnessStatus
        or trust is TrustLevel.FORBIDDEN_INFERENCE
        or (trust,) != query.allowed_trust_classes
        or relationship != query.expected_relationship_code
    ):
        raise C04EvidenceError(C04_QUERY_NOT_AUTHORIZED)
    provenance = "c04prov_" + sha256_hex(
        {
            "navigation_contract_version": C04_NAVIGATION_CONTRACT_VERSION,
            "dataset_version": packet.run.dataset_version,
            "dataset_hash": packet.run.dataset_hash,
            "source_family_code": projected.source_entity,
            "source_record_id": projected.source_record_id,
            "source_field": projected.source_field,
            "source_value": projected.value,
            "event_time": projected.observed_at,
            "available_at": projected.available_at,
            "freshness_code": freshness.value,
            "trust_class": trust,
            "relationship_code": relationship,
        }
    )
    return EvidenceObservation(
        source_family_code=projected.source_entity,
        source_record_id=projected.source_record_id,
        source_field=projected.source_field,
        source_value=projected.value,
        event_time=projected.observed_at,
        available_at=projected.available_at,
        freshness_code=freshness.value,
        provenance_ref=provenance,
        trust_class=trust,
        relationship_code=relationship,
    )


def _slice(
    connection: Connection,
    packet: DecisionPacket,
    context: _SourceContext,
    query: EvidenceQuerySpec,
) -> EvidenceSlice:
    observations: dict[str, EvidenceObservation] = {}
    for record_id, values in _records(connection, packet, query.source_family_code):
        projected = project_record(
            query.source_family_code,
            record_id,
            values,
            as_of_time=query.as_of_time,
            period_start=context.period_start,
            target_order_at=context.target_order_at,
        )
        for field in projected:
            if (
                type(field) is not ProjectedSourceField
                or field.source_entity != query.source_family_code
                or field.source_record_id != record_id
                or field.source_field not in SOURCE_FIELDS[query.source_family_code]
            ):
                raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH)
            if field.source_field in query.requested_fields:
                observation = _observation(packet, query, field)
                observations[observation.artifact_id] = observation
                if len(observations) > C04_MAX_OBSERVATIONS_PER_SLICE:
                    raise C04EvidenceError(C04_RESULT_LIMIT_EXCEEDED)
    return EvidenceSlice(
        case_id=query.case_id,
        plan_id=query.plan_id,
        step_id=query.step_id,
        question_id=query.question_id,
        query_id=query.artifact_id,
        as_of_time=query.as_of_time,
        observations=tuple(observations[key] for key in sorted(observations)),
    )


def _execute(
    engine: Engine,
    packet: DecisionPacket,
    queries: tuple[EvidenceQuerySpec, ...],
) -> tuple[EvidenceSlice, ...]:
    if not isinstance(engine, Engine) or engine.dialect.name != "postgresql":
        raise C04EvidenceError(C04_SOURCE_UNAVAILABLE)
    try:
        with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
            with connection.begin():
                try:
                    connection.execute(text("SET TRANSACTION READ ONLY"))
                    isolation = connection.execute(text("SHOW transaction_isolation")).scalar_one()
                    read_only = connection.execute(text("SHOW transaction_read_only")).scalar_one()
                except SQLAlchemyError:
                    raise C04EvidenceError(C04_READ_ONLY_VIOLATION) from None
                if isolation != "repeatable read" or read_only != "on":
                    raise C04EvidenceError(C04_READ_ONLY_VIOLATION)
                context = _source_context(connection, packet)
                return tuple(_slice(connection, packet, context, query) for query in queries)
    except C04EvidenceError:
        raise
    except C02BuildError as error:
        code = (
            C04_TEMPORAL_VIOLATION
            if error.state == "BLOCKED_TEMPORAL"
            else C04_SOURCE_CONTEXT_MISMATCH
        )
        raise C04EvidenceError(code) from None
    except SQLAlchemyError:
        raise C04EvidenceError(C04_SOURCE_UNAVAILABLE) from None
    except (AttributeError, KeyError, TypeError, ValueError):
        raise C04EvidenceError(C04_SOURCE_CONTEXT_MISMATCH) from None


def execute_evidence_navigation(
    engine: Engine,
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
) -> tuple[EvidenceSlice, ...]:
    """Validate inherited authority, then read all exact queries in one immutable DB view."""
    validate_evidence_query_specs(packet, case, questions, plan, queries)
    return _execute(engine, packet, queries)


def validate_evidence_navigation(
    engine: Engine,
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
    slices: tuple[EvidenceSlice, ...],
) -> None:
    """Re-execute in a new read-only transaction and compare original full C01 envelopes."""
    validate_evidence_query_specs(packet, case, questions, plan, queries)
    if type(slices) is not tuple or any(type(item) is not EvidenceSlice for item in slices):
        raise C04EvidenceError(C04_EVIDENCE_BINDING_MISMATCH)
    expected = _execute(engine, packet, queries)
    try:
        for item in slices:
            if type(item.observations) is not tuple or any(
                type(observation) is not EvidenceObservation for observation in item.observations
            ):
                raise C04EvidenceError(C04_EVIDENCE_BINDING_MISMATCH)
            detached = replace(item, observations=tuple(replace(obs) for obs in item.observations))
            validate_structural_dataclass(item)
            if canonical_json_bytes(item) != canonical_json_bytes(detached):
                raise C04EvidenceError(C04_EVIDENCE_BINDING_MISMATCH)
        # C01 deliberately restores Decimal/date/datetime scalar values as their
        # W03 canonical text. Full envelopes preserve that frozen roundtrip rule.
        if canonical_json_bytes(slices) != canonical_json_bytes(expected):
            raise C04EvidenceError(C04_EVIDENCE_BINDING_MISMATCH)
    except (AttributeError, TypeError, ValueError):
        raise C04EvidenceError(C04_EVIDENCE_BINDING_MISMATCH) from None
