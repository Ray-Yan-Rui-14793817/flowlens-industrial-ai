"""Pure immutable W04-C01 contracts, with no investigation execution capability."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, fields
from datetime import datetime
from enum import StrEnum
from types import UnionType
from typing import Any, ClassVar, Self, cast, get_args, get_origin, get_type_hints

from flowlens.decision.enums import TrustLevel
from flowlens.decision.primitives import (
    ScalarValue,
    Validated,
    validate_artifact_id,
    validate_sha256,
    validate_sorted_unique,
)
from flowlens.decision.serialization import canonical_json_text, sha256_hex
from flowlens.investigation.enums import (
    ConflictType,
    FindingStatus,
    HumanInvestigationOutcome,
    SummaryRendererMode,
    UncertaintyType,
)

# Extend the W03 prefix + full SHA-256 identity convention without editing its
# closed kind registry, following the existing W03 DecisionContext precedent.
_PREFIXES = {
    "investigation-case": "icase_",
    "investigation-question": "iquest_",
    "investigation-step": "istep_",
    "investigation-plan": "iplan_",
    "entity-key": "ekey_",
    "evidence-query-spec": "eqry_",
    "evidence-observation": "eobs_",
    "evidence-slice": "eslice_",
    "finding-record": "ifind_",
    "conflict-record": "iconf_",
    "uncertainty-item": "uitem_",
    "uncertainty-register": "ureg_",
    "summary-section-record": "isect_",
    "investigation-summary-record": "isum_",
    "human-investigation-event": "hievt_",
}
_DERIVED = frozenset({"artifact_id", "content_hash"})
_CODE = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*\Z", re.ASCII)
_MAX_CODE_LENGTH = 128
_CODE_FIELDS = frozenset(
    {
        "subject_type", "question_code", "source_family_code", "source_field",
        "freshness_code", "relationship_code", "expected_relationship_code",
        "key_name", "finding_code", "conflict_code", "uncertainty_code",
        "section_code", "planner_contract_version", "summary_contract_version",
        "note_class",
    }
)
_CODE_TUPLES = frozenset(
    {
        "risk_families", "required_evidence_families", "allowed_traversal_families",
        "forbidden_inference_codes", "expected_evidence_families", "requested_fields",
    }
)
_SET_TUPLES = _CODE_TUPLES | frozenset(
    {
        "source_signal_ids", "trigger_refs", "allowed_trust_classes",
        "depends_on_step_ids", "supporting_evidence_ids", "contradicting_evidence_ids",
        "related_conflict_ids", "uncertainty_item_ids", "evidence_ids", "related_refs",
        "grounding_refs", "finding_ids", "conflict_ids", "human_event_ids",
        "reviewed_finding_ids", "reviewed_conflict_ids", "acknowledged_uncertainty_item_ids",
    }
)


def _code(value: str, label: str) -> None:
    if len(value) > _MAX_CODE_LENGTH or _CODE.fullmatch(value) is None:
        raise ValueError(f"{label} must be an identifier-style code of at most 128 characters")


def _semantic(value: object) -> object:
    if isinstance(value, _Artifact):
        return value.canonical_payload()
    if isinstance(value, tuple):
        return tuple(_semantic(item) for item in value)
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class _Artifact(Validated):
    schema_version: str
    content_hash: str = field(init=False)
    artifact_id: str = field(init=False)
    _kind: ClassVar[str]

    def canonical_payload(self) -> dict[str, object]:
        """W03 identity envelope, recursively excluding derived identity fields."""
        return {
            "artifact_kind": self._kind,
            "schema_version": self.schema_version,
            "identity": {
                item.name: _semantic(getattr(self, item.name))
                for item in fields(self)
                if item.name not in _DERIVED and item.name != "schema_version"
            },
        }

    def __post_init__(self) -> None:
        # Validate caller data before canonicalization can inspect it. Reject
        # collection/model subclasses that can add mutable public state.
        object.__setattr__(self, "content_hash", "0" * 64)
        object.__setattr__(self, "artifact_id", "uninitialized")
        hints = get_type_hints(type(self))
        for item in fields(self):
            expected_type = hints[item.name]
            value = getattr(self, item.name)
            if get_origin(expected_type) is tuple:
                if type(value) is not tuple:
                    raise TypeError(f"{item.name} must be an exact immutable tuple")
                member_type = get_args(expected_type)[0]
                if isinstance(member_type, type) and issubclass(member_type, _Artifact):
                    if any(type(member) is not member_type for member in value):
                        raise TypeError(f"{item.name} must contain exact immutable value objects")
        Validated.__post_init__(self)
        if self._kind not in _PREFIXES or self.schema_version != f"{self._kind}.v1":
            raise ValueError("unsupported artifact kind or schema_version")
        for item in fields(self):
            value = getattr(self, item.name)
            if item.name in _CODE_FIELDS:
                _code(value, item.name)
            if item.name in _CODE_TUPLES:
                for code in value:
                    _code(code, item.name)
            if item.name in _SET_TUPLES:
                validate_sorted_unique(value, lambda entry: entry, item.name)
        digest = sha256_hex(self.canonical_payload())
        expected = _PREFIXES[self._kind] + digest
        object.__setattr__(self, "content_hash", digest)
        object.__setattr__(self, "artifact_id", expected)
        validate_sha256(self.content_hash, "content_hash")
        validate_artifact_id(self.artifact_id, _PREFIXES[self._kind], expected)

    def to_json(self) -> str:
        """Serialize the full immutable envelope with the exact W03 encoder."""
        return canonical_json_text(self)

    @classmethod
    def from_json(cls, raw: str | bytes) -> Self:
        """Parse only this contract's exact fields and validate claimed identities."""
        parsed: object = json.loads(
            raw, object_pairs_hook=_unique_object,
            parse_float=_reject_number, parse_constant=_reject_number,
        )
        return cast(Self, _decode_model(cls, parsed))


def _usable_trust(values: tuple[TrustLevel, ...]) -> None:
    if TrustLevel.FORBIDDEN_INFERENCE in values:
        raise ValueError("FORBIDDEN trust cannot authorize usable evidence")


@dataclass(frozen=True, slots=True, kw_only=True)
class InvestigationCase(_Artifact):
    _kind: ClassVar[str] = "investigation-case"
    schema_version: str = "investigation-case.v1"
    source_decision_packet_id: str
    source_decision_packet_hash: str
    decision_run_id: str
    subject_type: str
    subject_id: str
    as_of_time: datetime
    opened_at: datetime
    opened_by: str
    risk_families: tuple[str, ...]
    source_signal_ids: tuple[str, ...]
    source_diagnosis_id: str
    source_recommendation_id: str

    def __post_init__(self) -> None:
        _Artifact.__post_init__(self)
        validate_sha256(self.source_decision_packet_hash, "source_decision_packet_hash")
        if self.opened_at < self.as_of_time:
            raise ValueError("opened_at must be >= as_of_time")


@dataclass(frozen=True, slots=True, kw_only=True)
class InvestigationQuestion(_Artifact):
    _kind: ClassVar[str] = "investigation-question"
    schema_version: str = "investigation-question.v1"
    case_id: str
    question_code: str
    trigger_refs: tuple[str, ...]
    required_evidence_families: tuple[str, ...]
    allowed_traversal_families: tuple[str, ...]
    allowed_trust_classes: tuple[TrustLevel, ...]
    as_of_time: datetime
    forbidden_inference_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        _Artifact.__post_init__(self)
        _usable_trust(self.allowed_trust_classes)


@dataclass(frozen=True, slots=True, kw_only=True)
class InvestigationStep(_Artifact):
    _kind: ClassVar[str] = "investigation-step"
    schema_version: str = "investigation-step.v1"
    case_id: str
    question_id: str
    ordinal: int
    depends_on_step_ids: tuple[str, ...]
    expected_evidence_families: tuple[str, ...]

    def __post_init__(self) -> None:
        _Artifact.__post_init__(self)
        if self.ordinal < 1:
            raise ValueError("ordinal must be >= 1")
        for reference in (self.case_id, self.question_id, *self.depends_on_step_ids):
            _code(reference, "step reference")
        if self.artifact_id in self.depends_on_step_ids:
            raise ValueError("self-dependency is prohibited")


@dataclass(frozen=True, slots=True, kw_only=True)
class InvestigationPlan(_Artifact):
    _kind: ClassVar[str] = "investigation-plan"
    schema_version: str = "investigation-plan.v1"
    case_id: str
    as_of_time: datetime
    planner_contract_version: str
    steps: tuple[InvestigationStep, ...]

    def __post_init__(self) -> None:
        _Artifact.__post_init__(self)
        earlier: set[str] = set()
        for ordinal, step in enumerate(self.steps, start=1):
            if step.case_id != self.case_id or step.ordinal != ordinal:
                raise ValueError("plan requires same case and contiguous ordinals from 1")
            if step.artifact_id in earlier:
                raise ValueError("step identities must be unique")
            if not set(step.depends_on_step_ids) <= earlier:
                raise ValueError("dependencies must reference earlier plan steps only")
            earlier.add(step.artifact_id)


@dataclass(frozen=True, slots=True, kw_only=True)
class EntityKey(_Artifact):
    _kind: ClassVar[str] = "entity-key"
    schema_version: str = "entity-key.v1"
    key_name: str
    key_value: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceQuerySpec(_Artifact):
    _kind: ClassVar[str] = "evidence-query-spec"
    schema_version: str = "evidence-query-spec.v1"
    case_id: str
    plan_id: str
    step_id: str
    question_id: str
    source_family_code: str
    entity_keys: tuple[EntityKey, ...]
    as_of_time: datetime
    requested_fields: tuple[str, ...]
    allowed_trust_classes: tuple[TrustLevel, ...]
    expected_relationship_code: str

    def __post_init__(self) -> None:
        _Artifact.__post_init__(self)
        if not self.entity_keys or not self.requested_fields or not self.allowed_trust_classes:
            raise ValueError("query requires entity keys, requested fields and allowed trust")
        validate_sorted_unique(self.entity_keys, lambda key: key.key_name, "entity_keys")
        _usable_trust(self.allowed_trust_classes)


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceObservation(_Artifact):
    _kind: ClassVar[str] = "evidence-observation"
    schema_version: str = "evidence-observation.v1"
    source_family_code: str
    source_record_id: str
    source_field: str
    source_value: ScalarValue
    available_at: datetime
    event_time: datetime | None = None
    freshness_code: str
    provenance_ref: str
    trust_class: TrustLevel
    relationship_code: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceSlice(_Artifact):
    _kind: ClassVar[str] = "evidence-slice"
    schema_version: str = "evidence-slice.v1"
    case_id: str
    plan_id: str
    step_id: str
    question_id: str
    query_id: str
    as_of_time: datetime
    observations: tuple[EvidenceObservation, ...]

    def __post_init__(self) -> None:
        _Artifact.__post_init__(self)
        validate_sorted_unique(
            self.observations, lambda observation: observation.artifact_id, "observations"
        )
        for observation in self.observations:
            if observation.available_at > self.as_of_time:
                raise ValueError("future observation: available_at must be <= as_of_time")
            if observation.trust_class is TrustLevel.FORBIDDEN_INFERENCE:
                raise ValueError("FORBIDDEN observation cannot enter usable evidence")


@dataclass(frozen=True, slots=True, kw_only=True)
class FindingRecord(_Artifact):
    _kind: ClassVar[str] = "finding-record"
    schema_version: str = "finding-record.v1"
    case_id: str
    question_id: str
    finding_code: str
    status: FindingStatus
    supporting_evidence_ids: tuple[str, ...]
    contradicting_evidence_ids: tuple[str, ...]
    related_conflict_ids: tuple[str, ...]
    uncertainty_item_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _Artifact.__post_init__(self)
        if set(self.supporting_evidence_ids) & set(self.contradicting_evidence_ids):
            raise ValueError("supporting and contradicting evidence must be disjoint")
        if self.status is FindingStatus.SUPPORTED and not self.supporting_evidence_ids:
            raise ValueError("SUPPORTED requires supporting evidence")
        if self.status is FindingStatus.CONTRADICTED and not self.contradicting_evidence_ids:
            raise ValueError("CONTRADICTED requires contradicting evidence")
        if self.status is FindingStatus.UNKNOWN and not self.uncertainty_item_ids:
            raise ValueError("UNKNOWN requires explicit uncertainty")
        if self.status is FindingStatus.UNRESOLVED and not any(
            (self.supporting_evidence_ids, self.contradicting_evidence_ids,
             self.related_conflict_ids, self.uncertainty_item_ids)
        ):
            raise ValueError("UNRESOLVED requires explicit evidence/conflict/uncertainty basis")


@dataclass(frozen=True, slots=True, kw_only=True)
class ConflictRecord(_Artifact):
    _kind: ClassVar[str] = "conflict-record"
    schema_version: str = "conflict-record.v1"
    case_id: str
    question_id: str
    conflict_code: str
    conflict_type: ConflictType
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _Artifact.__post_init__(self)
        if len(self.evidence_ids) < 2:
            raise ValueError("conflict requires at least two unique evidence refs")


@dataclass(frozen=True, slots=True, kw_only=True)
class UncertaintyItem(_Artifact):
    _kind: ClassVar[str] = "uncertainty-item"
    schema_version: str = "uncertainty-item.v1"
    case_id: str
    question_id: str
    uncertainty_code: str
    uncertainty_type: UncertaintyType
    related_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class UncertaintyRegister(_Artifact):
    _kind: ClassVar[str] = "uncertainty-register"
    schema_version: str = "uncertainty-register.v1"
    case_id: str
    items: tuple[UncertaintyItem, ...]

    def __post_init__(self) -> None:
        _Artifact.__post_init__(self)
        validate_sorted_unique(self.items, lambda item: item.artifact_id, "items")
        if any(item.case_id != self.case_id for item in self.items):
            raise ValueError("uncertainty items must belong to the register case")


@dataclass(frozen=True, slots=True, kw_only=True)
class SummarySectionRecord(_Artifact):
    """Presentation text and refs only; no evidence or finding authority."""

    _kind: ClassVar[str] = "summary-section-record"
    schema_version: str = "summary-section-record.v1"
    section_code: str
    renderer_mode: SummaryRendererMode
    text: str
    grounding_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class InvestigationSummaryRecord(_Artifact):
    _kind: ClassVar[str] = "investigation-summary-record"
    schema_version: str = "investigation-summary-record.v1"
    case_id: str
    plan_id: str
    finding_ids: tuple[str, ...]
    conflict_ids: tuple[str, ...]
    uncertainty_register_id: str
    human_event_ids: tuple[str, ...]
    summary_contract_version: str
    sections: tuple[SummarySectionRecord, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class HumanInvestigationEvent(_Artifact):
    """Human review metadata only; notes are explicitly non-evidence."""

    _kind: ClassVar[str] = "human-investigation-event"
    schema_version: str = "human-investigation-event.v1"
    case_id: str
    actor_id: str
    occurred_at: datetime
    outcome: HumanInvestigationOutcome
    reviewed_finding_ids: tuple[str, ...]
    reviewed_conflict_ids: tuple[str, ...]
    acknowledged_uncertainty_item_ids: tuple[str, ...]
    previous_event_id: str | None = None
    note_text: str | None = None
    note_class: str = "HUMAN_NOTE_NON_EVIDENCE"

    def __post_init__(self) -> None:
        _Artifact.__post_init__(self)
        if self.note_class != "HUMAN_NOTE_NON_EVIDENCE":
            raise ValueError("Human notes must be HUMAN_NOTE_NON_EVIDENCE")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_number(value: str) -> object:
    raise ValueError(f"noncanonical JSON number: {value}")


def _decode_model(cls: type[_Artifact], value: object) -> _Artifact:
    if not isinstance(value, dict) or set(value) != {item.name for item in fields(cls)}:
        raise ValueError("serialized contract must have exactly the declared fields")
    supplied = cast(dict[str, object], value)
    hints = get_type_hints(cls)
    kwargs = {
        item.name: _decode_value(hints[item.name], supplied[item.name])
        for item in fields(cls) if item.init
    }
    # Only the explicitly selected frozen contract type is constructed; no
    # registry dispatch, imported function name or user-supplied code is used.
    model = cast(_Artifact, cast(Any, cls)(**kwargs))
    if (
        supplied["artifact_id"] != model.artifact_id
        or supplied["content_hash"] != model.content_hash
    ):
        raise ValueError("supplied artifact_id/content_hash does not match canonical content")
    return model


def _decode_value(expected: object, value: object) -> object:
    if expected is ScalarValue:
        # W03 encodes Decimal/date/datetime scalar values as strings. Retain
        # that canonical text rather than invent type tags or infer its meaning.
        if value is None or type(value) in (bool, int, str):
            return value
        raise TypeError("source_value must be a W03 canonical scalar")
    origin = get_origin(expected)
    if origin is UnionType:
        for part in get_args(expected):
            try:
                return _decode_value(part, value)
            except (TypeError, ValueError):
                continue
        raise TypeError("serialized optional field has the wrong type")
    if origin is tuple:
        if not isinstance(value, list):
            raise TypeError("serialized tuple field must be an array")
        return tuple(_decode_value(get_args(expected)[0], item) for item in value)
    if expected is type(None) and value is None:
        return None
    if isinstance(expected, type):
        if issubclass(expected, _Artifact):
            return _decode_model(expected, value)
        if issubclass(expected, StrEnum):
            if type(value) is not str:
                raise TypeError("serialized enum must be a string")
            return expected(value)
        if expected is datetime:
            if type(value) is not str:
                raise TypeError("serialized timestamp must be a string")
            return datetime.fromisoformat(value)
        if expected in (bool, int, str) and type(value) is expected:
            return value
    raise TypeError("serialized field has the wrong type")
