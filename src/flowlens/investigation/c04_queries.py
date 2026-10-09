"""Pure deterministic queries from frozen W03 and exactly bound W04 planning."""

from __future__ import annotations

from dataclasses import replace
from typing import Final

from flowlens.decision.c06_validation import validate_c05_packet
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.primitives import validate_structural_dataclass
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.investigation.c02_binding import (
    C02_FUTURE_INFORMATION,
    C02_INVALID_DECISION_PACKET,
    C02BindingError,
    validate_investigation_case_binding,
)
from flowlens.investigation.c03_planning import validate_investigation_planning
from flowlens.investigation.c04_registry import C04_ROOT_KEY_NAME, C04_SOURCE_REGISTRY
from flowlens.investigation.contracts import (
    EntityKey,
    EvidenceQuerySpec,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
)

C04_INVALID_DECISION_PACKET: Final = "C04_INVALID_DECISION_PACKET"
C04_CASE_BINDING_MISMATCH: Final = "C04_CASE_BINDING_MISMATCH"
C04_PLANNING_BINDING_MISMATCH: Final = "C04_PLANNING_BINDING_MISMATCH"
C04_QUERY_SET_MISMATCH: Final = "C04_QUERY_SET_MISMATCH"
C04_QUERY_NOT_AUTHORIZED: Final = "C04_QUERY_NOT_AUTHORIZED"
C04_SOURCE_UNAVAILABLE: Final = "C04_SOURCE_UNAVAILABLE"
C04_SOURCE_CONTEXT_MISMATCH: Final = "C04_SOURCE_CONTEXT_MISMATCH"
C04_READ_ONLY_VIOLATION: Final = "C04_READ_ONLY_VIOLATION"
C04_RESULT_LIMIT_EXCEEDED: Final = "C04_RESULT_LIMIT_EXCEEDED"
C04_TEMPORAL_VIOLATION: Final = "C04_TEMPORAL_VIOLATION"
C04_EVIDENCE_BINDING_MISMATCH: Final = "C04_EVIDENCE_BINDING_MISMATCH"


class C04EvidenceError(ValueError):
    """A stable C04 failure, without inherited validator or database error text."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _validate_inputs(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
) -> None:
    if type(packet) is not DecisionPacket:
        raise C04EvidenceError(C04_INVALID_DECISION_PACKET)
    try:
        validate_c05_packet(packet)
    except Exception:
        raise C04EvidenceError(C04_INVALID_DECISION_PACKET) from None
    if type(case) is not InvestigationCase:
        raise C04EvidenceError(C04_CASE_BINDING_MISMATCH)
    try:
        validate_investigation_case_binding(packet, case)
    except C02BindingError as error:
        code = (
            C04_INVALID_DECISION_PACKET
            if error.code in (C02_INVALID_DECISION_PACKET, C02_FUTURE_INFORMATION)
            else C04_CASE_BINDING_MISMATCH
        )
        raise C04EvidenceError(code) from None
    except Exception:
        raise C04EvidenceError(C04_CASE_BINDING_MISMATCH) from None
    if (
        type(questions) is not tuple
        or any(type(question) is not InvestigationQuestion for question in questions)
        or type(plan) is not InvestigationPlan
    ):
        raise C04EvidenceError(C04_PLANNING_BINDING_MISMATCH)
    try:
        validate_investigation_planning(packet, case, questions, plan)
    except Exception:
        raise C04EvidenceError(C04_PLANNING_BINDING_MISMATCH) from None


def _project_queries(
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
) -> tuple[EvidenceQuerySpec, ...]:
    by_id = {question.artifact_id: question for question in questions}
    root = (EntityKey(key_name=C04_ROOT_KEY_NAME, key_value=case.subject_id),)
    queries: list[EvidenceQuerySpec] = []
    for step in plan.steps:
        question = by_id[step.question_id]
        for family in step.expected_evidence_families:
            policy = C04_SOURCE_REGISTRY.get(family)
            if (
                policy is None
                or family not in question.required_evidence_families
                or family not in question.allowed_traversal_families
            ):
                raise C04EvidenceError(C04_QUERY_NOT_AUTHORIZED)
            for profile in policy.profiles:
                if profile.trust_class not in question.allowed_trust_classes:
                    raise C04EvidenceError(C04_QUERY_NOT_AUTHORIZED)
                queries.append(EvidenceQuerySpec(
                    case_id=case.artifact_id,
                    plan_id=plan.artifact_id,
                    step_id=step.artifact_id,
                    question_id=question.artifact_id,
                    source_family_code=family,
                    entity_keys=root,
                    as_of_time=case.as_of_time,
                    requested_fields=profile.requested_fields,
                    allowed_trust_classes=(profile.trust_class,),
                    expected_relationship_code=profile.relationship_code,
                ))
    return tuple(queries)


def build_evidence_query_specs(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
) -> tuple[EvidenceQuerySpec, ...]:
    """Project only the eleven closed profiles selected by an exact C03 plan."""
    _validate_inputs(packet, case, questions, plan)
    return _project_queries(case, questions, plan)


def validate_evidence_query_specs(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
) -> None:
    """Revalidate original and nested identities and compare complete envelopes."""
    expected = build_evidence_query_specs(packet, case, questions, plan)
    if type(queries) is not tuple or any(type(query) is not EvidenceQuerySpec for query in queries):
        raise C04EvidenceError(C04_QUERY_SET_MISMATCH)
    try:
        for query in queries:
            if type(query.entity_keys) is not tuple or any(
                type(key) is not EntityKey for key in query.entity_keys
            ):
                raise C04EvidenceError(C04_QUERY_SET_MISMATCH)
            keys = tuple(replace(key) for key in query.entity_keys)
            detached = replace(query, entity_keys=keys)
            validate_structural_dataclass(query)
            if canonical_json_bytes(query) != canonical_json_bytes(detached):
                raise C04EvidenceError(C04_QUERY_SET_MISMATCH)
        if canonical_json_bytes(queries) != canonical_json_bytes(expected):
            raise C04EvidenceError(C04_QUERY_SET_MISMATCH)
    except (AttributeError, TypeError, ValueError):
        raise C04EvidenceError(C04_QUERY_SET_MISMATCH) from None
