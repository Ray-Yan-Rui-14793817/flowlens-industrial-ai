"""Immutable transport-neutral product values; no acquisition or execution capability."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from types import UnionType
from typing import (
    Any,
    ClassVar,
    Final,
    Literal,
    TypeAliasType,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from flowlens.decision import contracts as dc
from flowlens.decision import enums as de
from flowlens.decision import primitives as dp
from flowlens.decision.serialization import canonical_json_bytes, canonical_json_text, sha256_hex
from flowlens.investigation import contracts as ic
from flowlens.investigation import enums as ie

PRODUCT_SCHEMA_VERSION: Final = "flowlens-product-case-view.v1"


class ProductErrorCode(StrEnum):
    INVALID_PRODUCT_SOURCE = "INVALID_PRODUCT_SOURCE"
    SOURCE_IDENTITY_MISMATCH = "SOURCE_IDENTITY_MISMATCH"
    SOURCE_SCOPE_MISMATCH = "SOURCE_SCOPE_MISMATCH"
    UNSUPPORTED_PRODUCT_STATE = "UNSUPPORTED_PRODUCT_STATE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ProductError(ValueError):
    """Only a closed public code crosses the product boundary."""

    def __init__(self, code: ProductErrorCode = ProductErrorCode.INTERNAL_ERROR) -> None:
        self.code = code if type(code) is ProductErrorCode else ProductErrorCode.INTERNAL_ERROR
        super().__init__(self.code.value)


def require_exact(value: object, expected: object) -> None:
    """Check exact immutable types recursively; no coercion or subclass state."""
    if isinstance(expected, TypeAliasType):
        require_exact(value, expected.__value__)
        return
    origin = get_origin(expected)
    if origin is UnionType:
        for part in get_args(expected):
            try:
                require_exact(value, part)
                return
            except (TypeError, ValueError):
                pass
        raise TypeError("invalid union value")
    if origin is Literal:
        if not any(type(value) is type(v) and value == v for v in get_args(expected)):
            raise ValueError("unsupported literal")
        return
    if origin is tuple:
        if type(value) is not tuple:
            raise TypeError("exact tuple required")
        for member in value:
            require_exact(member, get_args(expected)[0])
        return
    if not isinstance(expected, type) or type(value) is not expected:
        raise TypeError("exact declared type required")
    if expected is datetime:
        dp.validate_aware_datetime(cast(datetime, value), "timestamp")
    elif expected is Decimal and not cast(Decimal, value).is_finite():
        raise ValueError("finite Decimal required")
    elif is_dataclass(value):
        hints = get_type_hints(expected)
        for item in fields(value):
            require_exact(getattr(value, item.name), hints[item.name])
    elif expected not in (type(None), bool, int, str, date, Decimal) and not issubclass(
        expected, StrEnum
    ):
        raise TypeError("unsupported value")


def source_value(value: object) -> Any:
    """Detach and revalidate every original envelope, including derived claims."""
    if type(value) is tuple:
        return tuple(source_value(v) for v in value)
    if is_dataclass(value) and not isinstance(value, type):
        model = getattr(type(value), "_source_type", None) or type(value)
        original_fields = fields(model)
        converted = {f.name: source_value(getattr(value, f.name)) for f in original_fields}
        rebuilt = cast(Any, model)(**{f.name: converted[f.name] for f in original_fields if f.init})
        if canonical_json_bytes(converted) != canonical_json_bytes(rebuilt):
            raise ValueError("source envelope identity mismatch")
        return rebuilt
    return value


class _ProductValue:
    __slots__ = ()
    _source_type: ClassVar[type[object] | None] = None

    def __post_init__(self) -> None:
        try:
            if type(self) not in _PRODUCT_TYPES:
                raise TypeError("unsupported product subclass")
            require_exact(self, type(self))
            if self._source_type is not None:
                source_value(self)
        except Exception:
            raise ProductError(ProductErrorCode.INVALID_PRODUCT_SOURCE) from None

    def to_json(self) -> str:
        """Serialize a validated immutable value with unchanged W03 primitives."""
        return canonical_json_text(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductEvidenceView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.Evidence
    evidence_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    source_entity: str
    source_record_id: str
    source_field: str
    value: dp.ScalarValue
    observed_at: datetime | None
    available_at: datetime
    as_of_time: datetime
    relationship_type: str
    trust_level: de.TrustLevel
    freshness_status: de.FreshnessStatus
    limitations: tuple[dp.Limitation, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductEvidenceBundleView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.EvidenceBundle
    evidence_bundle_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    snapshot_hash: str
    evidence: tuple[ProductEvidenceView, ...]
    uncertainties: tuple[dp.Uncertainty, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductSignalView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.Signal
    signal_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    signal_type: de.SignalType
    state: de.SignalState
    evidence_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    limitations: tuple[dp.Limitation, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductSignalBundleView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.SignalBundle
    signal_bundle_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    signals: tuple[ProductSignalView, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductDiagnosisClaimView(_ProductValue):
    _source_type: ClassVar[type[object]] = dp.DiagnosisClaim
    claim_code: str
    claim_type: de.ClaimType
    statement: str
    evidence_ids: tuple[str, ...]
    limitations: tuple[dp.Limitation, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductDiagnosisView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.DiagnosisRecord
    diagnosis_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    problem_code: str
    claims: tuple[ProductDiagnosisClaimView, ...]
    supporting_signal_ids: tuple[str, ...]
    supporting_evidence_ids: tuple[str, ...]
    uncertainties: tuple[dp.Uncertainty, ...]
    affected_path: tuple[dp.EntityRef, ...]
    reason_codes: tuple[str, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductCandidateView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.InterventionCandidate
    candidate_id: str
    schema_version: str
    run_id: str
    family: de.InterventionFamily
    registry_key: str
    parameters: tuple[dp.NamedValue, ...]
    supporting_evidence_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    limitations: tuple[dp.Limitation, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductCandidateSetView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.CandidateSet
    candidate_set_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    diagnosis_id: str
    candidates: tuple[ProductCandidateView, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductSimulationView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.SimulationResult
    simulation_id: str
    schema_version: str
    run_id: str
    candidate_id: str
    status: de.SimulationStatus
    baseline_snapshot_id: str
    baseline_snapshot_hash: str
    scenario_id: str | None
    scenario_hash: str | None
    affected_entities: tuple[dp.EntityRef, ...]
    measurements: tuple[dp.NamedValue, ...]
    limitations: tuple[dp.Limitation, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductSimulationBundleView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.SimulationBundle
    simulation_bundle_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    results: tuple[ProductSimulationView, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductRecommendationView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.RecommendationRecord
    recommendation_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    diagnosis_id: str
    candidate_set_id: str
    simulation_bundle_id: str
    policy_version: str
    disposition: de.RecommendationDisposition
    selected_candidate_id: str | None
    candidate_order: tuple[str, ...]
    score_components: tuple[dp.NamedValue, ...]
    reason_codes: tuple[str, ...]
    supporting_evidence_ids: tuple[str, ...]
    uncertainties: tuple[dp.Uncertainty, ...]
    limitations: tuple[dp.Limitation, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductExplanationView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.ExplanationRecord
    explanation_id: str
    schema_version: str
    run_id: str
    packet_id: str
    mode: de.ExplanationMode
    explainer_version: str
    sections: tuple[dp.ExplanationSection, ...]
    referenced_evidence_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    limitations: tuple[dp.Limitation, ...]
    provenance: dp.ArtifactProvenance


@dataclass(frozen=True, slots=True, kw_only=True)
class DecisionHumanReviewView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.HumanDecisionEvent
    decision_event_id: str
    schema_version: str
    run_id: str
    packet_id: str
    decision: de.HumanDecisionType
    actor_id: str
    decided_at: datetime
    accepted_reason_codes: tuple[str, ...]
    rejected_reason_codes: tuple[str, ...]
    comment: str | None
    investigation_priority: str | None
    previous_event_id: str | None
    provenance: dp.ArtifactProvenance
    note_class: Literal["HUMAN_NOTE_NON_EVIDENCE"] = "HUMAN_NOTE_NON_EVIDENCE"


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductFindingView(_ProductValue):
    _source_type: ClassVar[type[object]] = ic.FindingRecord
    schema_version: str
    content_hash: str
    artifact_id: str
    case_id: str
    question_id: str
    finding_code: str
    status: ie.FindingStatus
    supporting_evidence_ids: tuple[str, ...]
    contradicting_evidence_ids: tuple[str, ...]
    related_conflict_ids: tuple[str, ...]
    uncertainty_item_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductConflictView(_ProductValue):
    _source_type: ClassVar[type[object]] = ic.ConflictRecord
    schema_version: str
    content_hash: str
    artifact_id: str
    case_id: str
    question_id: str
    conflict_code: str
    conflict_type: ie.ConflictType
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductUncertaintyView(_ProductValue):
    _source_type: ClassVar[type[object]] = ic.UncertaintyItem
    schema_version: str
    content_hash: str
    artifact_id: str
    case_id: str
    question_id: str
    uncertainty_code: str
    uncertainty_type: ie.UncertaintyType
    related_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductUncertaintyRegisterView(_ProductValue):
    _source_type: ClassVar[type[object]] = ic.UncertaintyRegister
    schema_version: str
    content_hash: str
    artifact_id: str
    case_id: str
    items: tuple[ProductUncertaintyView, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductSummarySectionView(_ProductValue):
    _source_type: ClassVar[type[object]] = ic.SummarySectionRecord
    schema_version: str
    content_hash: str
    artifact_id: str
    section_code: str
    renderer_mode: ie.SummaryRendererMode
    text: str
    grounding_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class InvestigationHumanReviewView(_ProductValue):
    _source_type: ClassVar[type[object]] = ic.HumanInvestigationEvent
    schema_version: str
    content_hash: str
    artifact_id: str
    case_id: str
    actor_id: str
    occurred_at: datetime
    outcome: ie.HumanInvestigationOutcome
    reviewed_finding_ids: tuple[str, ...]
    reviewed_conflict_ids: tuple[str, ...]
    acknowledged_uncertainty_item_ids: tuple[str, ...]
    previous_event_id: str | None
    note_text: str | None
    note_class: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductInvestigationSummaryView(_ProductValue):
    _source_type: ClassVar[type[object]] = ic.InvestigationSummaryRecord
    schema_version: str
    content_hash: str
    artifact_id: str
    case_id: str
    plan_id: str
    finding_ids: tuple[str, ...]
    conflict_ids: tuple[str, ...]
    uncertainty_register_id: str
    human_event_ids: tuple[str, ...]
    summary_contract_version: str
    sections: tuple[ProductSummarySectionView, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductDecisionView(_ProductValue):
    _source_type: ClassVar[type[object]] = dc.DecisionPacket
    packet_id: str
    schema_version: str
    run: dc.DecisionRun
    snapshot: dc.StateSnapshot
    evidence: ProductEvidenceBundleView
    signals: ProductSignalBundleView
    diagnosis: ProductDiagnosisView
    candidates: ProductCandidateSetView
    simulations: ProductSimulationBundleView
    recommendation: ProductRecommendationView
    uncertainties: tuple[dp.Uncertainty, ...]
    limitations: tuple[dp.Limitation, ...]
    provenance: dp.ArtifactProvenance
    explanation: ProductExplanationView | None = None
    human_reviews: tuple[DecisionHumanReviewView, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductInvestigationView(_ProductValue):
    case: ic.InvestigationCase
    questions: tuple[ic.InvestigationQuestion, ...]
    plan: ic.InvestigationPlan
    queries: tuple[ic.EvidenceQuerySpec, ...]
    slices: tuple[ic.EvidenceSlice, ...]
    findings: tuple[ProductFindingView, ...]
    conflicts: tuple[ProductConflictView, ...]
    uncertainty_register: ProductUncertaintyRegisterView
    human_reviews: tuple[InvestigationHumanReviewView, ...]
    summary: ProductInvestigationSummaryView


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductCaseIdentity(_ProductValue):
    order_id: str
    as_of_time: datetime
    dataset_version: str
    dataset_hash: str
    run_id: str
    snapshot_id: str
    snapshot_hash: str
    packet_id: str
    packet_hash: str
    case_id: str
    plan_id: str
    summary_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductCapabilityBoundary(_ProductValue):
    mode: Literal["OFFLINE_SHADOW"] = "OFFLINE_SHADOW"
    human_authority_required: Literal[True] = True
    operational_write: Literal["FORBIDDEN"] = "FORBIDDEN"
    runtime_hgt: Literal["FORBIDDEN"] = "FORBIDDEN"
    llm_decision_authority: Literal["NONE"] = "NONE"
    llm_tool_authority: Literal["NONE"] = "NONE"
    recommendation_execution: Literal["FORBIDDEN"] = "FORBIDDEN"


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductCaseView(_ProductValue):
    schema_version: Literal["flowlens-product-case-view.v1"] = PRODUCT_SCHEMA_VERSION
    view_id: str = field(init=False)
    view_hash: str = field(init=False)
    identity: ProductCaseIdentity
    decision: ProductDecisionView
    investigation: ProductInvestigationView
    capability_boundary: ProductCapabilityBoundary

    def __post_init__(self) -> None:
        object.__setattr__(self, "view_id", "uninitialized")
        object.__setattr__(self, "view_hash", "0" * 64)
        _ProductValue.__post_init__(self)
        from flowlens.product.projection import validate_product_view_sources

        validate_product_view_sources(self)
        # Product identity is derived from the complete admitted semantic world.
        digest = sha256_hex(self.semantic_payload())
        object.__setattr__(self, "view_hash", digest)
        object.__setattr__(self, "view_id", "pcv_" + digest)

    def semantic_payload(self) -> dict[str, object]:
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.name not in ("view_id", "view_hash")
        }


_PRODUCT_TYPES = frozenset(
    value
    for value in tuple(globals().values())
    if isinstance(value, type) and issubclass(value, _ProductValue) and value is not _ProductValue
)


def product_schema() -> dict[str, object]:
    """Fresh deterministic JSON Schema; exact public fields, wire types and enums."""
    definitions: dict[str, object] = {}

    def describe(expected: object) -> dict[str, object]:
        if isinstance(expected, TypeAliasType):
            return describe(expected.__value__)
        origin = get_origin(expected)
        if origin is UnionType:
            return {"anyOf": [describe(t) for t in get_args(expected)]}
        if origin is Literal:
            return {"enum": list(get_args(expected))}
        if origin is tuple:
            return {"type": "array", "items": describe(get_args(expected)[0])}
        if isinstance(expected, type):
            if issubclass(expected, StrEnum):
                return {"type": "string", "enum": [v.value for v in expected]}
            if is_dataclass(expected):
                name = expected.__name__
                if name not in definitions:
                    definitions[name] = {}
                    hints = get_type_hints(expected)
                    properties = {f.name: describe(hints[f.name]) for f in fields(expected)}
                    definitions[name] = {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": properties,
                        "required": list(properties),
                    }
                return {"$ref": "#/$defs/" + name}
            if expected is datetime:
                return {
                    "type": "string",
                    "format": "date-time",
                    "pattern": r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}Z$",
                }
            if expected is date:
                return {"type": "string", "format": "date"}
            if expected is Decimal:
                return {
                    "type": "string",
                    "pattern": r"^-?(0|[1-9][0-9]*)(\.[0-9]*[1-9])?$",
                    "x-canonical-type": "Decimal",
                }
            if expected in (type(None), bool, int, str):
                return {
                    "type": {type(None): "null", bool: "boolean", int: "integer", str: "string"}[
                        expected
                    ]
                }
        raise ProductError(ProductErrorCode.INTERNAL_ERROR)

    root = describe(ProductCaseView)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": PRODUCT_SCHEMA_VERSION,
        **root,
        "$defs": definitions,
        "x-identity": "SHA256(canonical payload excluding view_id/view_hash); pcv_ + hash",
    }


def product_schema_json() -> str:
    return json.dumps(product_schema(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
