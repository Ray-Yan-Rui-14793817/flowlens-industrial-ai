"""Pure W04-C05 bounded findings; frozen C04 envelopes confer no query authority."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal, InvalidOperation
from types import MappingProxyType
from typing import Any, Final, NoReturn, cast

from flowlens.decision.c06_validation import validate_c05_packet
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.enums import FreshnessStatus, SignalState, SignalType, TrustLevel
from flowlens.decision.primitives import validate_structural_dataclass
from flowlens.decision.serialization import canonical_json_bytes, canonical_primitive, sha256_hex
from flowlens.investigation.c02_binding import validate_investigation_case_binding
from flowlens.investigation.c03_planning import validate_investigation_planning
from flowlens.investigation.c04_queries import validate_evidence_query_specs
from flowlens.investigation.c04_registry import C04_NAVIGATION_CONTRACT_VERSION
from flowlens.investigation.contracts import (
    ConflictRecord,
    EvidenceObservation,
    EvidenceQuerySpec,
    EvidenceSlice,
    FindingRecord,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
    UncertaintyItem,
    UncertaintyRegister,
)
from flowlens.investigation.enums import ConflictType, FindingStatus, UncertaintyType

C05_INVALID_DECISION_PACKET: Final = "C05_INVALID_DECISION_PACKET"
C05_CASE_BINDING_MISMATCH: Final = "C05_CASE_BINDING_MISMATCH"
C05_PLANNING_BINDING_MISMATCH: Final = "C05_PLANNING_BINDING_MISMATCH"
C05_QUERY_SET_MISMATCH: Final = "C05_QUERY_SET_MISMATCH"
C05_EVIDENCE_SET_MISMATCH: Final = "C05_EVIDENCE_SET_MISMATCH"
C05_EVIDENCE_PROVENANCE_MISMATCH: Final = "C05_EVIDENCE_PROVENANCE_MISMATCH"
C05_EVIDENCE_VALUE_INVALID: Final = "C05_EVIDENCE_VALUE_INVALID"
C05_FINDING_SET_MISMATCH: Final = "C05_FINDING_SET_MISMATCH"
C05_CONFLICT_SET_MISMATCH: Final = "C05_CONFLICT_SET_MISMATCH"
C05_UNCERTAINTY_REGISTER_MISMATCH: Final = "C05_UNCERTAINTY_REGISTER_MISMATCH"
C05_OUTPUT_REFERENCE_MISMATCH: Final = "C05_OUTPUT_REFERENCE_MISMATCH"

_FINDINGS: Final = MappingProxyType(
    {
        SignalType.SUPPLIER_LATE_RECEIPT: "W04_C05_ASSOCIATED_RECEIPT_LATENESS",
        SignalType.MATERIAL_TIMING_RISK: "W04_C05_ASSOCIATED_MATERIAL_TIMING_WARNING",
        SignalType.QUALITY_FAILURE: "W04_C05_RECORDED_QUALITY_FAILURE",
        SignalType.REWORK_PRESENT: "W04_C05_RECORDED_REWORK",
        SignalType.QUALITY_DISPOSITION_UNKNOWN: "W04_C05_QUALITY_DISPOSITION_UNRESOLVED",
        SignalType.QUEUE_DELAY: "W04_C05_START_SLIPPAGE_PROXY",
        SignalType.CAPACITY_PRESSURE: "W04_C05_CAPACITY_PRESSURE_UNRESOLVED",
        SignalType.DELIVERY_RISK: "W04_C05_DELIVERY_COMMITMENT_WARNING",
    }
)
_DATETIMES: Final = frozenset(
    (family, field)
    for family, fields in (
        ("fact_sales_order", ("order_at", "promised_delivery_at")),
        (
            "fact_work_order",
            ("planned_start_at", "planned_end_at", "actual_start_at", "actual_end_at"),
        ),
        (
            "fact_operation",
            ("planned_start_at", "planned_end_at", "actual_start_at", "actual_end_at"),
        ),
        ("fact_material_requirement", ("need_by_at",)),
        ("fact_purchase_order", ("ordered_at", "promised_receipt_at", "actual_receipt_at")),
        ("fact_quality_inspection", ("inspection_at",)),
        ("fact_rework", ("rework_start_at", "rework_end_at")),
        ("fact_delivery", ("delivery_at",)),
    )
    for field in fields
)
_DECIMALS: Final = frozenset(
    {
        ("fact_material_requirement", "required_quantity"),
        ("fact_purchase_order", "ordered_quantity"),
        ("fact_purchase_order", "received_quantity"),
    }
)
_INTS: Final = frozenset(
    (family, field)
    for family, fields in (
        ("fact_sales_order", ("order_quantity",)),
        ("fact_work_order", ("planned_quantity", "completed_quantity")),
        ("fact_operation", ("sequence_number",)),
        ("fact_quality_inspection", ("inspected_quantity", "passed_quantity", "failed_quantity")),
        ("fact_rework", ("rework_quantity",)),
        ("fact_delivery", ("delivered_quantity",)),
    )
    for field in fields
)
_STRINGS: Final = frozenset(
    {
        ("fact_material_requirement", "material_id"),
        ("fact_purchase_order", "material_id"),
        ("fact_quality_inspection", "result"),
    }
)
_ACTUAL_EVENTS: Final = frozenset(
    {
        ("fact_work_order", "actual_start_at"),
        ("fact_work_order", "actual_end_at"),
        ("fact_operation", "actual_start_at"),
        ("fact_operation", "actual_end_at"),
        ("fact_purchase_order", "actual_receipt_at"),
        ("fact_quality_inspection", "inspection_at"),
        ("fact_rework", "rework_start_at"),
        ("fact_rework", "rework_end_at"),
        ("fact_delivery", "delivery_at"),
    }
)
_ELIGIBLE_FRESHNESS: Final = frozenset({FreshnessStatus.FRESH, FreshnessStatus.NOT_APPLICABLE})
_ELIGIBLE_TRUST: Final = frozenset({TrustLevel.DIRECT_FACT, TrustLevel.ASSOCIATIVE_EVIDENCE})
_ALWAYS_UNKNOWN: Final = frozenset(
    {
        SignalType.CAPACITY_PRESSURE,
        SignalType.QUALITY_DISPOSITION_UNKNOWN,
    }
)
_CONFLICT_CODES: Final = frozenset(
    {
        "C05_CONFLICT_DUPLICATE_FIELD_VALUE",
        "C05_CONFLICT_WORK_ORDER_ACTUAL_WINDOW",
        "C05_CONFLICT_OPERATION_ACTUAL_WINDOW",
        "C05_CONFLICT_REWORK_WINDOW",
        "C05_CONFLICT_PO_RECEIPT_BEFORE_ORDER",
        "C05_CONFLICT_DELIVERY_BEFORE_ORDER",
        "C05_CONFLICT_QUALITY_RESULT_QUANTITY",
        "C05_CONFLICT_PO_QUANTITY_EXCEEDS_ORDERED",
        "C05_CONFLICT_WO_COMPLETION_EXCEEDS_PLANNED",
        "C05_CONFLICT_DELIVERY_EXCEEDS_ORDER",
        "C05_CONFLICT_SUPPORT_VS_CONTRADICTION",
    }
)
type _Value = datetime | Decimal | int | str | None
type _Key = tuple[str, str, str]
type _Result = tuple[set[str], set[str], bool]


class C05FindingError(ValueError):
    """Closed, detail-free public failure surface."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise C05FindingError(code) from None


def _identity(value: object, code: str) -> None:
    """Check the supplied envelope before reconstruction can refresh its identity."""
    try:
        validate_structural_dataclass(value)
        detached = replace(cast(Any, value))
        if canonical_json_bytes(value) != canonical_json_bytes(detached):
            _fail(code)
    except (AttributeError, TypeError, ValueError):
        _fail(code)


def _decode(obs: EvidenceObservation) -> _Value:
    key = (obs.source_family_code, obs.source_field)
    value = obs.source_value
    if value is None:
        return None
    try:
        if key in _DATETIMES:
            if type(value) is datetime:
                decoded = value
            elif type(value) is str:
                decoded = datetime.fromisoformat(value)
                if canonical_primitive(decoded) != value:
                    _fail(C05_EVIDENCE_VALUE_INVALID)
            else:
                _fail(C05_EVIDENCE_VALUE_INVALID)
            if decoded.tzinfo is None or decoded.utcoffset() is None:
                _fail(C05_EVIDENCE_VALUE_INVALID)
            return decoded
        if key in _DECIMALS:
            if type(value) is Decimal:
                quantity = value
            elif type(value) is str:
                quantity = Decimal(value)
                if canonical_primitive(quantity) != value:
                    _fail(C05_EVIDENCE_VALUE_INVALID)
            else:
                _fail(C05_EVIDENCE_VALUE_INVALID)
            if not quantity.is_finite() or quantity < 0:
                _fail(C05_EVIDENCE_VALUE_INVALID)
            return quantity
        if key in _INTS:
            if type(value) is not int or value < 0:
                _fail(C05_EVIDENCE_VALUE_INVALID)
            return value
        if key in _STRINGS:
            if type(value) is not str or not value:
                _fail(C05_EVIDENCE_VALUE_INVALID)
            if key == ("fact_quality_inspection", "result") and value not in ("PASS", "FAIL"):
                _fail(C05_EVIDENCE_VALUE_INVALID)
            return value
    except (ValueError, TypeError, InvalidOperation, OverflowError):
        _fail(C05_EVIDENCE_VALUE_INVALID)
    # Unused C04 context fields retain their generic wire representation.
    return None


def _admit(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
    slices: tuple[EvidenceSlice, ...],
) -> None:
    try:
        if type(packet) is not DecisionPacket:
            _fail(C05_INVALID_DECISION_PACKET)
        validate_c05_packet(packet)
    except (AttributeError, TypeError, ValueError):
        _fail(C05_INVALID_DECISION_PACKET)
    try:
        if type(case) is not InvestigationCase:
            _fail(C05_CASE_BINDING_MISMATCH)
        validate_investigation_case_binding(packet, case)
    except (AttributeError, TypeError, ValueError):
        _fail(C05_CASE_BINDING_MISMATCH)
    try:
        if (
            type(questions) is not tuple
            or type(plan) is not InvestigationPlan
            or any(type(q) is not InvestigationQuestion for q in questions)
        ):
            _fail(C05_PLANNING_BINDING_MISMATCH)
        validate_investigation_planning(packet, case, questions, plan)
    except (AttributeError, TypeError, ValueError):
        _fail(C05_PLANNING_BINDING_MISMATCH)
    try:
        if type(queries) is not tuple or any(type(q) is not EvidenceQuerySpec for q in queries):
            _fail(C05_QUERY_SET_MISMATCH)
        validate_evidence_query_specs(packet, case, questions, plan, queries)
    except (AttributeError, TypeError, ValueError):
        _fail(C05_QUERY_SET_MISMATCH)
    if type(slices) is not tuple or len(slices) != len(queries):
        _fail(C05_EVIDENCE_SET_MISMATCH)
    for query, item in zip(queries, slices, strict=True):
        if (
            type(item) is not EvidenceSlice
            or type(item.observations) is not tuple
            or any(type(obs) is not EvidenceObservation for obs in item.observations)
        ):
            _fail(C05_EVIDENCE_SET_MISMATCH)
        for obs in item.observations:
            try:
                validate_structural_dataclass(obs)
            except (AttributeError, TypeError, ValueError):
                # Invalid evaluated scalars have their own stable error; identity never refreshes.
                _decode(obs)
                _fail(C05_EVIDENCE_SET_MISMATCH)
            _identity(obs, C05_EVIDENCE_SET_MISMATCH)
        _identity(item, C05_EVIDENCE_SET_MISMATCH)
        if (
            item.case_id,
            item.plan_id,
            item.step_id,
            item.question_id,
            item.query_id,
            item.as_of_time,
        ) != (
            case.artifact_id,
            plan.artifact_id,
            query.step_id,
            query.question_id,
            query.artifact_id,
            query.as_of_time,
        ) or item.as_of_time != case.as_of_time:
            _fail(C05_EVIDENCE_SET_MISMATCH)
        for obs in item.observations:
            if (
                obs.source_family_code != query.source_family_code
                or obs.source_field not in query.requested_fields
                or (obs.trust_class,) != query.allowed_trust_classes
                or obs.relationship_code != query.expected_relationship_code
                or obs.available_at > query.as_of_time
                or (obs.event_time is not None and obs.event_time > query.as_of_time)
                or obs.trust_class is TrustLevel.FORBIDDEN_INFERENCE
                or obs.freshness_code not in tuple(status.value for status in FreshnessStatus)
            ):
                _fail(C05_EVIDENCE_SET_MISMATCH)
            provenance = "c04prov_" + sha256_hex(
                {
                    "navigation_contract_version": C04_NAVIGATION_CONTRACT_VERSION,
                    "dataset_version": packet.run.dataset_version,
                    "dataset_hash": packet.run.dataset_hash,
                    "source_family_code": obs.source_family_code,
                    "source_record_id": obs.source_record_id,
                    "source_field": obs.source_field,
                    "source_value": obs.source_value,
                    "event_time": obs.event_time,
                    "available_at": obs.available_at,
                    "freshness_code": obs.freshness_code,
                    "trust_class": obs.trust_class,
                    "relationship_code": obs.relationship_code,
                }
            )
            if obs.provenance_ref != provenance:
                _fail(C05_EVIDENCE_PROVENANCE_MISMATCH)
            decoded = _decode(obs)
            if (
                (obs.source_family_code, obs.source_field) in _ACTUAL_EVENTS
                and type(decoded) is datetime
                and decoded > case.as_of_time
            ):
                _fail(C05_EVIDENCE_SET_MISMATCH)


@dataclass(frozen=True, slots=True)
class _Cell:
    value: _Value
    refs: tuple[str, ...]


def _refs(*cells: _Cell | None) -> set[str]:
    return {ref for cell in cells if cell is not None for ref in cell.refs}


class _Scope:
    """Ephemeral question-local indices; no state persists between calls."""

    def __init__(
        self,
        case: InvestigationCase,
        question: InvestigationQuestion,
        queries: tuple[EvidenceQuerySpec, ...],
        slices: tuple[EvidenceSlice, ...],
    ) -> None:
        self.case = case
        self.question = question
        self.slices = slices
        self.observations = {obs.artifact_id: obs for item in slices for obs in item.observations}
        self.observed_keys = frozenset(
            (obs.source_family_code, obs.source_record_id, obs.source_field)
            for obs in self.observations.values()
        )
        self.family_refs: dict[str, set[str]] = {}
        for query, item in zip(queries, slices, strict=True):
            self.family_refs.setdefault(query.source_family_code, set()).update(
                (query.artifact_id, item.artifact_id)
            )
        self.items: dict[UncertaintyType, set[str]] = {}
        self.conflicts: dict[str, ConflictRecord] = {}
        self.cells: dict[_Key, tuple[_Cell, ...]] = {}
        grouped: dict[_Key, dict[bytes, list[EvidenceObservation]]] = {}
        self.uncertainty(
            UncertaintyType.FORBIDDEN_INFERENCE,
            {question.artifact_id, *question.forbidden_inference_codes},
        )
        for item in slices:
            if not item.observations:
                self.uncertainty(
                    UncertaintyType.MISSING_EVIDENCE, {item.artifact_id, item.query_id}
                )
        for obs in self.observations.values():
            if obs.source_value is None or obs.freshness_code == FreshnessStatus.UNKNOWN:
                self.uncertainty(UncertaintyType.UNKNOWN_EVIDENCE, {obs.artifact_id})
            if obs.freshness_code in (FreshnessStatus.STALE, FreshnessStatus.EXPIRED):
                self.uncertainty(UncertaintyType.STALE_EVIDENCE, {obs.artifact_id})
            if obs.trust_class not in _ELIGIBLE_TRUST or obs.freshness_code not in (
                status.value for status in _ELIGIBLE_FRESHNESS
            ):
                continue
            key = (obs.source_family_code, obs.source_record_id, obs.source_field)
            versions = grouped.setdefault(key, {})
            versions.setdefault(canonical_json_bytes(obs.source_value), []).append(obs)
        for key, options in grouped.items():
            self.cells[key] = tuple(
                _Cell(_decode(values[0]), tuple(sorted(obs.artifact_id for obs in values)))
                for _, values in sorted(options.items())
            )
            if len(options) > 1:
                self.conflict(
                    "DUPLICATE_FIELD_VALUE", ConflictType.VALUE_CONFLICT, _refs(*self.cells[key])
                )

    def uncertainty(self, kind: UncertaintyType, refs: set[str]) -> None:
        self.items.setdefault(kind, set()).update({self.question.artifact_id, *refs})

    def missing(self, family: str) -> None:
        self.uncertainty(
            UncertaintyType.MISSING_EVIDENCE,
            self.family_refs.get(family, set()),
        )

    def rows(self, family: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    obs.source_record_id
                    for obs in self.observations.values()
                    if obs.source_family_code == family
                }
            )
        )

    def peek(self, family: str, record: str, field: str) -> _Cell | None:
        cells = self.cells.get((family, record, field), ())
        return cells[0] if len(cells) == 1 else None

    def read(self, family: str, record: str, field: str, *, nullable: bool = False) -> _Cell | None:
        cell = self.peek(family, record, field)
        if cell is None:
            if (family, record, field) not in self.observed_keys:
                self.missing(family)
            return None
        if cell.value is None and not nullable:
            self.uncertainty(UncertaintyType.UNKNOWN_EVIDENCE, set(cell.refs))
            return None
        if any(
            self.observations[ref].trust_class is TrustLevel.ASSOCIATIVE_EVIDENCE
            for ref in cell.refs
        ):
            self.uncertainty(UncertaintyType.ASSOCIATIVE_ONLY, set(cell.refs))
        return cell

    def conflict(self, code: str, kind: ConflictType, refs: set[str]) -> None:
        if len(refs) < 2:
            return
        item = ConflictRecord(
            case_id=self.case.artifact_id,
            question_id=self.question.artifact_id,
            conflict_code="C05_CONFLICT_" + code,
            conflict_type=kind,
            evidence_ids=tuple(sorted(refs)),
        )
        self.conflicts[item.artifact_id] = item
        associative = {
            ref
            for ref in refs
            if self.observations[ref].trust_class is TrustLevel.ASSOCIATIVE_EVIDENCE
        }
        if associative:
            self.uncertainty(UncertaintyType.ASSOCIATIVE_ONLY, associative)


def _fixed_conflicts(scope: _Scope) -> None:
    for family, start, end, code in (
        ("fact_work_order", "actual_start_at", "actual_end_at", "WORK_ORDER_ACTUAL_WINDOW"),
        ("fact_operation", "actual_start_at", "actual_end_at", "OPERATION_ACTUAL_WINDOW"),
        ("fact_rework", "rework_start_at", "rework_end_at", "REWORK_WINDOW"),
        ("fact_purchase_order", "ordered_at", "actual_receipt_at", "PO_RECEIPT_BEFORE_ORDER"),
    ):
        for row in scope.rows(family):
            a, b = scope.peek(family, row, start), scope.peek(family, row, end)
            if (
                a
                and b
                and type(a.value) is datetime
                and type(b.value) is datetime
                and b.value < a.value
            ):
                scope.conflict(code, ConflictType.TIMESTAMP_CONFLICT, _refs(a, b))
    orders = scope.rows("fact_sales_order")
    for order in orders:
        ordered = scope.peek("fact_sales_order", order, "order_at")
        for row in scope.rows("fact_delivery"):
            delivered = scope.peek("fact_delivery", row, "delivery_at")
            if (
                ordered
                and delivered
                and type(ordered.value) is datetime
                and type(delivered.value) is datetime
                and delivered.value < ordered.value
            ):
                scope.conflict(
                    "DELIVERY_BEFORE_ORDER",
                    ConflictType.TIMESTAMP_CONFLICT,
                    _refs(ordered, delivered),
                )
    for family, lower, upper, code in (
        (
            "fact_purchase_order",
            "ordered_quantity",
            "received_quantity",
            "PO_QUANTITY_EXCEEDS_ORDERED",
        ),
        (
            "fact_work_order",
            "planned_quantity",
            "completed_quantity",
            "WO_COMPLETION_EXCEEDS_PLANNED",
        ),
    ):
        for row in scope.rows(family):
            a, b = scope.peek(family, row, lower), scope.peek(family, row, upper)
            if (
                a
                and b
                and isinstance(a.value, (int, Decimal))
                and isinstance(b.value, (int, Decimal))
                and b.value > a.value
            ):
                scope.conflict(code, ConflictType.VALUE_CONFLICT, _refs(a, b))
    for row in scope.rows("fact_quality_inspection"):
        inspected, passed, failed, result = (
            scope.peek("fact_quality_inspection", row, field)
            for field in ("inspected_quantity", "passed_quantity", "failed_quantity", "result")
        )
        if (
            inspected
            and passed
            and failed
            and type(inspected.value) is int
            and type(passed.value) is int
            and type(failed.value) is int
            and passed.value + failed.value != inspected.value
        ):
            scope.conflict(
                "QUALITY_RESULT_QUANTITY",
                ConflictType.VALUE_CONFLICT,
                _refs(inspected, passed, failed),
            )
        if (
            result
            and failed
            and type(failed.value) is int
            and (
                (result.value == "PASS" and failed.value > 0)
                or (result.value == "FAIL" and failed.value == 0)
            )
        ):
            scope.conflict(
                "QUALITY_RESULT_QUANTITY", ConflictType.VALUE_CONFLICT, _refs(result, failed)
            )
    deliveries = tuple(
        scope.peek("fact_delivery", row, "delivered_quantity")
        for row in scope.rows("fact_delivery")
    )
    if deliveries and all(cell is not None and type(cell.value) is int for cell in deliveries):
        total = sum(cast(int, cast(_Cell, cell).value) for cell in deliveries)
        for order in orders:
            quantity = scope.peek("fact_sales_order", order, "order_quantity")
            if quantity and type(quantity.value) is int and total > quantity.value:
                scope.conflict(
                    "DELIVERY_EXCEEDS_ORDER",
                    ConflictType.VALUE_CONFLICT,
                    _refs(quantity, *deliveries),
                )


def _quantity(scope: _Scope, family: str, field: str) -> _Result:
    rows = scope.rows(family)
    if not rows:
        scope.missing(family)
        return set(), set(), True
    support: set[str] = set()
    contra: set[str] = set()
    complete_zero = True
    gap = False
    for row in rows:
        options = scope.cells.get((family, row, field), ())
        positive = tuple(c for c in options if type(c.value) is int and c.value > 0)
        zeros = tuple(c for c in options if type(c.value) is int and c.value == 0)
        support.update(_refs(*positive))
        contra.update(_refs(*zeros))
        complete_zero = complete_zero and bool(zeros)
        if not options or any(c.value is None for c in options):
            scope.read(family, row, field)
            gap = True
        gap = gap or len(options) > 1
    return support, contra if complete_zero else set(), gap


def _queue(scope: _Scope) -> _Result:
    family = "fact_operation"
    rows = scope.rows(family)
    if not rows:
        scope.missing(family)
        return set(), set(), True
    support: set[str] = set()
    contra: set[str] = set()
    gap = False
    for row in rows:
        planned = scope.read(family, row, "planned_start_at")
        actual = scope.read(family, row, "actual_start_at", nullable=True)
        if planned is None or actual is None:
            gap = True
            continue
        plan_time = cast(datetime, planned.value)
        if (actual.value is None and scope.case.as_of_time > plan_time) or (
            type(actual.value) is datetime and actual.value > plan_time
        ):
            support.update(_refs(planned, actual))
        else:
            contra.update(_refs(planned, actual))
    return support, contra if not support and not gap else set(), gap


def _association(scope: _Scope, *, material: bool) -> _Result:
    req_family, po_family = "fact_material_requirement", "fact_purchase_order"
    requirements, purchases = scope.rows(req_family), scope.rows(po_family)
    if not requirements or not purchases:
        scope.missing(req_family if not requirements else po_family)
        return set(), set(), True
    support: set[str] = set()
    contra: set[str] = set()
    gap = False
    pairs = 0
    for requirement in requirements:
        req_id = scope.read(req_family, requirement, "material_id")
        need = scope.read(req_family, requirement, "need_by_at") if material else None
        if req_id is None or (material and need is None):
            gap = True
            continue
        matched = False
        for purchase in purchases:
            po_id = scope.read(po_family, purchase, "material_id")
            if po_id is None:
                gap = True
                continue
            if po_id.value != req_id.value:
                continue
            matched = True
            pairs += 1
            promised = scope.read(po_family, purchase, "promised_receipt_at")
            actual = scope.read(po_family, purchase, "actual_receipt_at", nullable=True)
            ordered = scope.read(po_family, purchase, "ordered_quantity")
            received = scope.read(po_family, purchase, "received_quantity")
            deadline = need if material else promised
            warning: set[str] = set()
            if actual and type(actual.value) is datetime and deadline:
                if actual.value > cast(datetime, deadline.value):
                    warning.update(_refs(req_id, po_id, actual, deadline))
            if ordered and received and deadline:
                outstanding = cast(Decimal, ordered.value) > cast(Decimal, received.value)
                if outstanding and scope.case.as_of_time > cast(datetime, deadline.value):
                    warning.update(_refs(req_id, po_id, ordered, received, deadline))
                if (
                    material
                    and outstanding
                    and promised
                    and cast(datetime, promised.value) > cast(datetime, deadline.value)
                ):
                    warning.update(_refs(req_id, po_id, ordered, received, promised, deadline))
            support.update(warning)
            complete = all(c is not None for c in (promised, actual, ordered, received))
            gap = gap or not complete
            if complete and not warning:
                contra.update(_refs(req_id, po_id, need, promised, actual, ordered, received))
        if not matched:
            scope.missing(po_family)
            # Only MATERIAL requires a PO for every requirement.
            gap = gap or material
    if not pairs:
        gap = True
    return support, contra if pairs and not support and not gap else set(), gap


def _delivery(scope: _Scope) -> _Result:
    orders, deliveries = scope.rows("fact_sales_order"), scope.rows("fact_delivery")
    if not orders or not deliveries:
        scope.missing("fact_sales_order" if not orders else "fact_delivery")
        return set(), set(), True
    cells = tuple(scope.read("fact_delivery", row, "delivered_quantity") for row in deliveries)
    if any(cell is None for cell in cells):
        return set(), set(), True
    total = sum(cast(int, cast(_Cell, cell).value) for cell in cells)
    support: set[str] = set()
    contra: set[str] = set()
    gap = False
    for order in orders:
        quantity = scope.read("fact_sales_order", order, "order_quantity")
        if quantity is None:
            gap = True
            continue
        if total >= cast(int, quantity.value):
            contra.update(_refs(quantity, *cells))
            continue
        promise = scope.read("fact_sales_order", order, "promised_delivery_at")
        if promise is None:
            gap = True
            continue
        if scope.case.as_of_time > cast(datetime, promise.value):
            support.update(_refs(quantity, promise, *cells))
        work_orders = scope.rows("fact_work_order")
        for work_order in work_orders:
            planned = scope.read("fact_work_order", work_order, "planned_end_at")
            actual = scope.read("fact_work_order", work_order, "actual_end_at", nullable=True)
            if (
                planned
                and actual
                and actual.value is None
                and cast(datetime, planned.value) > cast(datetime, promise.value)
            ):
                support.update(_refs(quantity, promise, planned, actual, *cells))
            gap = gap or planned is None or actual is None
    return support, contra if not support and not gap else set(), gap


def _project(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    queries: tuple[EvidenceQuerySpec, ...],
    slices: tuple[EvidenceSlice, ...],
) -> tuple[tuple[FindingRecord, ...], tuple[ConflictRecord, ...], UncertaintyRegister]:
    findings: list[FindingRecord] = []
    conflicts: list[ConflictRecord] = []
    items: list[UncertaintyItem] = []
    for question in questions:
        signals = tuple(
            signal for signal in packet.signals.signals if signal.signal_id in question.trigger_refs
        )
        if (
            len(signals) != 1
            or type(signals[0].signal_type) is not SignalType
            or signals[0].state is SignalState.INACTIVE
        ):
            _fail(C05_PLANNING_BINDING_MISMATCH)
        signal = signals[0]
        scoped_slices = tuple(s for s in slices if s.question_id == question.artifact_id)
        scoped_queries = tuple(q for q in queries if q.question_id == question.artifact_id)
        scope = _Scope(case, question, scoped_queries, scoped_slices)
        _fixed_conflicts(scope)
        support: set[str] = set()
        contra: set[str] = set()
        gap = False
        unknown = signal.state is SignalState.UNKNOWN or signal.signal_type in _ALWAYS_UNKNOWN
        if not unknown:
            if signal.signal_type in (
                SignalType.SUPPLIER_LATE_RECEIPT,
                SignalType.MATERIAL_TIMING_RISK,
            ):
                support, contra, gap = _association(
                    scope, material=signal.signal_type is SignalType.MATERIAL_TIMING_RISK
                )
            elif signal.signal_type is SignalType.QUALITY_FAILURE:
                support, contra, gap = _quantity(
                    scope, "fact_quality_inspection", "failed_quantity"
                )
            elif signal.signal_type is SignalType.REWORK_PRESENT:
                support, contra, gap = _quantity(scope, "fact_rework", "rework_quantity")
            elif signal.signal_type is SignalType.QUEUE_DELAY:
                support, contra, gap = _queue(scope)
            elif signal.signal_type is SignalType.DELIVERY_RISK:
                support, contra, gap = _delivery(scope)
        if support and contra:
            witnesses = support | contra
            kind = (
                ConflictType.DIRECT_VS_DIRECT
                if all(
                    scope.observations[ref].trust_class is TrustLevel.DIRECT_FACT
                    for ref in witnesses
                )
                else ConflictType.VALUE_CONFLICT
            )
            scope.conflict("SUPPORT_VS_CONTRADICTION", kind, witnesses)
        if scope.conflicts:
            scope.uncertainty(
                UncertaintyType.CONFLICTING_EVIDENCE,
                {
                    ref
                    for conflict in scope.conflicts.values()
                    for ref in (conflict.artifact_id, *conflict.evidence_ids)
                },
            )
        if unknown:
            status = FindingStatus.UNKNOWN
        elif scope.conflicts:
            status = FindingStatus.UNRESOLVED
        elif support:
            status = FindingStatus.SUPPORTED
        elif contra and not gap:
            status = FindingStatus.CONTRADICTED
        else:
            status = FindingStatus.UNRESOLVED
        if status in (FindingStatus.UNKNOWN, FindingStatus.UNRESOLVED):
            scope.uncertainty(UncertaintyType.UNRESOLVED_QUESTION, {question.artifact_id})
        question_items = tuple(
            UncertaintyItem(
                case_id=case.artifact_id,
                question_id=question.artifact_id,
                uncertainty_code="C05_UNCERTAINTY_" + kind.value,
                uncertainty_type=kind,
                related_refs=tuple(sorted(refs)),
            )
            for kind, refs in sorted(scope.items.items())
        )
        findings.append(
            FindingRecord(
                case_id=case.artifact_id,
                question_id=question.artifact_id,
                finding_code=_FINDINGS[signal.signal_type],
                status=status,
                supporting_evidence_ids=tuple(sorted(support)),
                contradicting_evidence_ids=tuple(sorted(contra)),
                related_conflict_ids=tuple(sorted(scope.conflicts)),
                uncertainty_item_ids=tuple(sorted(item.artifact_id for item in question_items)),
            )
        )
        conflicts.extend(scope.conflicts.values())
        items.extend(question_items)
    return (
        tuple(findings),
        tuple(sorted(conflicts, key=lambda c: c.artifact_id)),
        UncertaintyRegister(
            case_id=case.artifact_id, items=tuple(sorted(items, key=lambda item: item.artifact_id))
        ),
    )


def derive_findings_conflicts_uncertainty(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
    slices: tuple[EvidenceSlice, ...],
) -> tuple[tuple[FindingRecord, ...], tuple[ConflictRecord, ...], UncertaintyRegister]:
    """Validate exact upstream artifacts, then project one bounded finding per question."""
    try:
        _admit(packet, case, questions, plan, queries, slices)
    except C05FindingError:
        raise
    except (AttributeError, TypeError, ValueError):
        _fail(C05_EVIDENCE_SET_MISMATCH)
    return _project(packet, case, questions, queries, slices)


def validate_findings_conflicts_uncertainty(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
    slices: tuple[EvidenceSlice, ...],
    findings: tuple[FindingRecord, ...],
    conflicts: tuple[ConflictRecord, ...],
    uncertainty_register: UncertaintyRegister,
) -> None:
    """Rebuild and compare whole envelopes, including original derived identity claims."""
    expected = derive_findings_conflicts_uncertainty(packet, case, questions, plan, queries, slices)
    if (
        type(findings) is not tuple
        or any(type(f) is not FindingRecord for f in findings)
        or len(findings) != len(expected[0])
    ):
        _fail(C05_FINDING_SET_MISMATCH)
    if (
        type(conflicts) is not tuple
        or any(type(c) is not ConflictRecord for c in conflicts)
        or len(conflicts) != len(expected[1])
    ):
        _fail(C05_CONFLICT_SET_MISMATCH)
    if type(uncertainty_register) is not UncertaintyRegister:
        _fail(C05_UNCERTAINTY_REGISTER_MISMATCH)
    try:
        validate_structural_dataclass(uncertainty_register)
    except (AttributeError, TypeError, ValueError):
        _fail(C05_UNCERTAINTY_REGISTER_MISMATCH)
    if (
        type(uncertainty_register.items) is not tuple
        or any(type(i) is not UncertaintyItem for i in uncertainty_register.items)
        or len(uncertainty_register.items) != len(expected[2].items)
    ):
        _fail(C05_UNCERTAINTY_REGISTER_MISMATCH)
    for finding in findings:
        _identity(finding, C05_FINDING_SET_MISMATCH)
    for conflict in conflicts:
        _identity(conflict, C05_CONFLICT_SET_MISMATCH)
        if conflict.conflict_code not in _CONFLICT_CODES:
            _fail(C05_CONFLICT_SET_MISMATCH)
    for item in uncertainty_register.items:
        _identity(item, C05_UNCERTAINTY_REGISTER_MISMATCH)
    _identity(uncertainty_register, C05_UNCERTAINTY_REGISTER_MISMATCH)
    detached_register = replace(
        uncertainty_register, items=tuple(replace(item) for item in uncertainty_register.items)
    )
    if canonical_json_bytes(uncertainty_register) != canonical_json_bytes(detached_register):
        _fail(C05_UNCERTAINTY_REGISTER_MISMATCH)
    question_ids = {q.artifact_id for q in questions}
    obs_refs = {
        q.artifact_id: {
            o.artifact_id for s in slices if s.question_id == q.artifact_id for o in s.observations
        }
        for q in questions
    }
    conflict_refs = {
        q.artifact_id: {c.artifact_id for c in conflicts if c.question_id == q.artifact_id}
        for q in questions
    }
    uncertainty_refs = {
        q.artifact_id: {
            i.artifact_id for i in uncertainty_register.items if i.question_id == q.artifact_id
        }
        for q in questions
    }
    scoped_values: tuple[FindingRecord | ConflictRecord | UncertaintyItem, ...] = (
        *findings,
        *conflicts,
        *uncertainty_register.items,
    )
    for value in scoped_values:
        if value.case_id != case.artifact_id or value.question_id not in question_ids:
            _fail(C05_OUTPUT_REFERENCE_MISMATCH)
    if uncertainty_register.case_id != case.artifact_id:
        _fail(C05_OUTPUT_REFERENCE_MISMATCH)
    for finding in findings:
        qid = finding.question_id
        if (
            not set((*finding.supporting_evidence_ids, *finding.contradicting_evidence_ids))
            <= obs_refs[qid]
            or not set(finding.related_conflict_ids) <= conflict_refs[qid]
            or not set(finding.uncertainty_item_ids) <= uncertainty_refs[qid]
        ):
            _fail(C05_OUTPUT_REFERENCE_MISMATCH)
    for conflict in conflicts:
        if not set(conflict.evidence_ids) <= obs_refs[conflict.question_id]:
            _fail(C05_OUTPUT_REFERENCE_MISMATCH)
    for question in questions:
        known = {
            question.artifact_id,
            *question.forbidden_inference_codes,
            *obs_refs[question.artifact_id],
            *conflict_refs[question.artifact_id],
        }
        known.update(
            ref
            for s in slices
            if s.question_id == question.artifact_id
            for ref in (s.artifact_id, s.query_id)
        )
        for item in uncertainty_register.items:
            if item.question_id == question.artifact_id and not set(item.related_refs) <= known:
                _fail(C05_OUTPUT_REFERENCE_MISMATCH)
    for supplied, wanted, code in (
        (findings, expected[0], C05_FINDING_SET_MISMATCH),
        (conflicts, expected[1], C05_CONFLICT_SET_MISMATCH),
        (uncertainty_register, expected[2], C05_UNCERTAINTY_REGISTER_MISMATCH),
    ):
        if canonical_json_bytes(supplied) != canonical_json_bytes(wanted):
            _fail(code)
