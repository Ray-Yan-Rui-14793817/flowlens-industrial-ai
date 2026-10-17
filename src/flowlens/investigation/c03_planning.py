"""Bounded, pure W04-C03 planning from an exactly bound frozen W03 packet."""

from __future__ import annotations

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Final, NoReturn

from flowlens.decision.c03_policy import COMMON_LIMITATION_CODES, SIGNAL_POLICIES
from flowlens.decision.c06_validation import validate_c05_packet
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.enums import (
    ClaimType,
    SignalState,
    SignalType,
    TrustLevel,
    UncertaintyStatus,
)
from flowlens.decision.primitives import EntityRef, validate_structural_dataclass
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.investigation.c02_binding import (
    C02_FUTURE_INFORMATION,
    C02_INVALID_DECISION_PACKET,
    C02BindingError,
    validate_investigation_case_binding,
)
from flowlens.investigation.contracts import (
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
    InvestigationStep,
)

C03_PLANNER_CONTRACT_VERSION: Final = "w04-c03-v1"
C03_INVALID_DECISION_PACKET: Final = "C03_INVALID_DECISION_PACKET"
C03_CASE_BINDING_MISMATCH: Final = "C03_CASE_BINDING_MISMATCH"
C03_W03_SEMANTIC_MISMATCH: Final = "C03_W03_SEMANTIC_MISMATCH"
C03_QUESTION_SET_MISMATCH: Final = "C03_QUESTION_SET_MISMATCH"
C03_PLAN_BINDING_MISMATCH: Final = "C03_PLAN_BINDING_MISMATCH"

_SIGNAL_TYPES: Final = tuple(sorted(SignalType, key=lambda family: family.value))
_PARTIAL_MESSAGE: Final = (
    "A positive witness exists, but some rule-relevant evidence is incomplete."
)


class C03PlanningError(ValueError):
    """A stable planning failure without inherited W03 or C02 error text."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class _QuestionPolicy:
    required_evidence_families: tuple[str, ...]
    allowed_traversal_families: tuple[str, ...]
    allowed_trust_classes: tuple[TrustLevel, ...]
    forbidden_inference_codes: tuple[str, ...]


def _trust_classes(family: SignalType) -> tuple[TrustLevel, ...]:
    if family in (SignalType.SUPPLIER_LATE_RECEIPT, SignalType.MATERIAL_TIMING_RISK):
        return (TrustLevel.ASSOCIATIVE_EVIDENCE, TrustLevel.DIRECT_FACT, TrustLevel.UNKNOWN)
    if family in (
        SignalType.QUALITY_DISPOSITION_UNKNOWN, SignalType.QUEUE_DELAY, SignalType.DELIVERY_RISK,
    ):
        return (TrustLevel.DERIVED_FACT, TrustLevel.DIRECT_FACT, TrustLevel.UNKNOWN)
    return (TrustLevel.DIRECT_FACT, TrustLevel.UNKNOWN)


_QUESTION_REGISTRY: Final = MappingProxyType(
    {
        family: _QuestionPolicy(
            required_evidence_families=SIGNAL_POLICIES[family].entities,
            allowed_traversal_families=SIGNAL_POLICIES[family].entities,
            allowed_trust_classes=_trust_classes(family),
            forbidden_inference_codes=tuple(
                sorted(set(COMMON_LIMITATION_CODES) | set(
                    SIGNAL_POLICIES[family].domain_limitation_codes
                ))
            ),
        )
        for family in _SIGNAL_TYPES
    }
)


def _semantic_mismatch() -> NoReturn:
    raise C03PlanningError(C03_W03_SEMANTIC_MISMATCH)


def _validate_semantics(packet: DecisionPacket) -> None:
    signals = packet.signals.signals
    if tuple(signal.signal_type for signal in signals) != _SIGNAL_TYPES:
        _semantic_mismatch()

    if any(
        signal.signal_type == SignalType.DELIVERY_RISK and signal.state == SignalState.ACTIVE
        for signal in signals
    ):
        problem = "DELIVERY_COMMITMENT_WARNING"
    elif any(signal.state == SignalState.ACTIVE for signal in signals):
        problem = "OBSERVED_DELIVERY_RISK_INDICATORS"
    else:
        problem = "INSUFFICIENT_EVIDENCE_FOR_RISK_ASSESSMENT"

    diagnosis = packet.diagnosis
    if (
        diagnosis.problem_code != problem
        or diagnosis.supporting_signal_ids != tuple(sorted(signal.signal_id for signal in signals))
        or diagnosis.affected_path != (
            EntityRef(entity_type="fact_sales_order", entity_id=packet.run.order_id),
        )
        or diagnosis.reason_codes != tuple(sorted(
            {code for signal in signals for code in signal.reason_codes}
            | {"C03_STRUCTURED_NOT_CAUSAL"}
        ))
    ):
        _semantic_mismatch()

    expected_claims: list[tuple[object, ...]] = []
    for signal in signals:
        if signal.state == SignalState.INACTIVE:
            continue
        policy = SIGNAL_POLICIES[signal.signal_type]
        if signal.state == SignalState.ACTIVE:
            claim_type = policy.active_claim_type
            statement = policy.active_statement
            if claim_type is None or statement is None:
                _semantic_mismatch()
        else:
            claim_type = ClaimType.UNCERTAINTY_STATEMENT
            statement = policy.unknown_statement
        expected_claims.append((
            f"C03_{signal.signal_type.value}_{signal.state.value}_V1",
            claim_type, statement, signal.evidence_ids, signal.limitations,
        ))

        uncertainty_code: str | None = None
        uncertainty_message: str | None = None
        if signal.state == SignalState.UNKNOWN:
            uncertainty_code = f"C03_UNKNOWN_{signal.signal_type.value}"
            uncertainty_message = policy.unknown_statement
        elif "C03_INPUT_INCOMPLETE" in signal.reason_codes:
            uncertainty_code = f"C03_PARTIAL_{signal.signal_type.value}"
            uncertainty_message = _PARTIAL_MESSAGE
        if uncertainty_code is not None:
            matching = tuple(
                item for item in diagnosis.uncertainties if item.code == uncertainty_code
            )
            if len(matching) != 1 or (
                matching[0].status != UncertaintyStatus.INSUFFICIENT_EVIDENCE
                or matching[0].message != uncertainty_message
                or matching[0].evidence_ids != signal.evidence_ids
            ):
                _semantic_mismatch()

    actual_claims = tuple(
        (claim.claim_code, claim.claim_type, claim.statement, claim.evidence_ids, claim.limitations)
        for claim in diagnosis.claims
    )
    if actual_claims != tuple(expected_claims):
        _semantic_mismatch()


def _validate_inputs(packet: DecisionPacket, case: InvestigationCase) -> None:
    if type(packet) is not DecisionPacket:
        raise C03PlanningError(C03_INVALID_DECISION_PACKET)
    try:
        validate_c05_packet(packet)
    except Exception:
        raise C03PlanningError(C03_INVALID_DECISION_PACKET) from None
    if type(case) is not InvestigationCase:
        raise C03PlanningError(C03_CASE_BINDING_MISMATCH)
    try:
        validate_investigation_case_binding(packet, case)
    except C02BindingError as error:
        code = (
            C03_INVALID_DECISION_PACKET
            if error.code in (C02_INVALID_DECISION_PACKET, C02_FUTURE_INFORMATION)
            else C03_CASE_BINDING_MISMATCH
        )
        raise C03PlanningError(code) from None
    except Exception:
        raise C03PlanningError(C03_CASE_BINDING_MISMATCH) from None
    _validate_semantics(packet)


def _project_questions(
    packet: DecisionPacket, case: InvestigationCase,
) -> tuple[InvestigationQuestion, ...]:
    questions: list[InvestigationQuestion] = []
    for signal in packet.signals.signals:
        if signal.state == SignalState.INACTIVE:
            continue
        family = signal.signal_type
        policy = _QUESTION_REGISTRY[family]
        triggers = {
            packet.diagnosis.diagnosis_id,
            signal.signal_id,
            f"C03_{family.value}_{signal.state.value}_V1",
        }
        if signal.state == SignalState.UNKNOWN:
            triggers.add(f"C03_UNKNOWN_{family.value}")
        elif "C03_INPUT_INCOMPLETE" in signal.reason_codes:
            triggers.add(f"C03_PARTIAL_{family.value}")
        questions.append(InvestigationQuestion(
            case_id=case.artifact_id,
            question_code=f"W04_C03_{family.value}_{signal.state.value}",
            trigger_refs=tuple(sorted(triggers)),
            required_evidence_families=policy.required_evidence_families,
            allowed_traversal_families=policy.allowed_traversal_families,
            allowed_trust_classes=policy.allowed_trust_classes,
            as_of_time=case.as_of_time,
            forbidden_inference_codes=policy.forbidden_inference_codes,
        ))
    return tuple(questions)


def _validate_questions(
    questions: tuple[InvestigationQuestion, ...],
    expected: tuple[InvestigationQuestion, ...],
) -> None:
    if type(questions) is not tuple or any(
        type(question) is not InvestigationQuestion for question in questions
    ):
        raise C03PlanningError(C03_QUESTION_SET_MISMATCH)
    try:
        for question in questions:
            detached = replace(question)
            validate_structural_dataclass(question)
            if canonical_json_bytes(question) != canonical_json_bytes(detached):
                raise C03PlanningError(C03_QUESTION_SET_MISMATCH)
        if canonical_json_bytes(questions) != canonical_json_bytes(expected):
            raise C03PlanningError(C03_QUESTION_SET_MISMATCH)
    except (AttributeError, TypeError, ValueError):
        raise C03PlanningError(C03_QUESTION_SET_MISMATCH) from None


def _project_plan(
    case: InvestigationCase, questions: tuple[InvestigationQuestion, ...],
) -> InvestigationPlan:
    return InvestigationPlan(
        case_id=case.artifact_id,
        as_of_time=case.as_of_time,
        planner_contract_version=C03_PLANNER_CONTRACT_VERSION,
        steps=tuple(
            InvestigationStep(
                case_id=case.artifact_id,
                question_id=question.artifact_id,
                ordinal=ordinal,
                depends_on_step_ids=(),
                expected_evidence_families=question.required_evidence_families,
            )
            for ordinal, question in enumerate(questions, start=1)
        ),
    )


def _validate_plan(plan: InvestigationPlan, expected: InvestigationPlan) -> None:
    if type(plan) is not InvestigationPlan:
        raise C03PlanningError(C03_PLAN_BINDING_MISMATCH)
    try:
        if type(plan.steps) is not tuple or any(
            type(step) is not InvestigationStep for step in plan.steps
        ):
            raise C03PlanningError(C03_PLAN_BINDING_MISMATCH)
        # Each detached step rejects malformed init tuples before original
        # traversal. A detached plan alone would retain stale nested identities.
        steps: list[InvestigationStep] = []
        for step in plan.steps:
            steps.append(replace(step))
            validate_structural_dataclass(step)
        detached = replace(plan, steps=tuple(steps))
        validate_structural_dataclass(plan)
        original = canonical_json_bytes(plan)
        if original != canonical_json_bytes(detached) or original != canonical_json_bytes(expected):
            raise C03PlanningError(C03_PLAN_BINDING_MISMATCH)
    except (AttributeError, TypeError, ValueError):
        raise C03PlanningError(C03_PLAN_BINDING_MISMATCH) from None


def build_investigation_questions(
    packet: DecisionPacket, case: InvestigationCase,
) -> tuple[InvestigationQuestion, ...]:
    """Select only frozen registry questions after packet, binding and semantic checks."""
    _validate_inputs(packet, case)
    return _project_questions(packet, case)


def build_investigation_plan(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
) -> InvestigationPlan:
    """Require the exact question projection and create an immutable dependency-free plan."""
    _validate_inputs(packet, case)
    expected = _project_questions(packet, case)
    _validate_questions(questions, expected)
    return _project_plan(case, expected)


def validate_investigation_planning(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
) -> None:
    """Compare full original and revalidated envelopes with the deterministic projection."""
    _validate_inputs(packet, case)
    expected_questions = _project_questions(packet, case)
    _validate_questions(questions, expected_questions)
    _validate_plan(plan, _project_plan(case, expected_questions))
