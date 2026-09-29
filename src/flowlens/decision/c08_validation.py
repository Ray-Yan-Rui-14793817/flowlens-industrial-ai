"""Fail-closed packet, schema, grounding, and safety validation for W03-C08."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, fields, is_dataclass
from typing import Final, Never

from flowlens.decision.c03_validation import source_refs_for
from flowlens.decision.c05_policy import PACKET_POLICY_VERSION
from flowlens.decision.c08_context import ExplanationContextV1
from flowlens.decision.c08_policy import (
    ARTIFACT_ID_PATTERN,
    CAUSAL_CLAIM_PATTERN,
    FORBIDDEN_INFERENCE_PATTERN,
    INJECTION_OR_CAPABILITY_PATTERN,
    MAX_SECTION_TEXT_CHARS,
    MAX_TOTAL_MODEL_TEXT_CHARS,
    MODEL_SECTION_KEYS,
    NUMERIC_OR_TEMPORAL_PATTERN,
    OUTPUT_SCHEMA_VERSION,
    PROBABILITY_CLAIM_PATTERN,
    SIMULATION_EFFICACY_PATTERN,
)
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.enums import InterventionFamily, RecommendationDisposition
from flowlens.decision.primitives import VersionRef
from flowlens.decision.serialization import canonical_json_bytes, canonical_json_text

_EXPECTED_PACKET_CONTRACTS: Final = (
    VersionRef(name="w03-c01", version="v1"),
    VersionRef(name="w03-c02", version="v1"),
    VersionRef(name="w03-c03", version="v1"),
    VersionRef(name="w03-c04", version="v1"),
    VersionRef(name="w03-c05-decision", version="v1"),
    VersionRef(name="w03-c05-evaluation", version="v1"),
    VersionRef(name="w03-c05-packet", version="v1"),
)
_HGT_TOKENS: Final = (
    "hidden_ground_truth",
    "ground_truth",
    "hgt_",
    "recommendation_evaluation",
    "recommendationevaluation",
    "outcome_evaluation",
    "outcomeevaluation",
)
_UNKNOWN_RESOLUTION_PATTERN: Final = re.compile(
    r"\b(?:is|was|has been|now)\s+(?:resolved|confirmed|known|established|certain)\b",
    re.IGNORECASE,
)


class C08BuildError(ValueError):
    """A stable C08 contract, schema, grounding, temporal, or isolation failure."""

    def __init__(self, code: str, state: str, *, repairable_schema: bool = False) -> None:
        self.code = code
        self.state = state
        self.repairable_schema = repairable_schema
        super().__init__(f"{state}: {code}")


@dataclass(frozen=True, slots=True)
class ValidatedSection:
    section_key: str
    text: str
    evidence_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ValidatedProviderOutput:
    schema_version: str
    sections: tuple[ValidatedSection, ...]


def _schema_fail(code: str = "C08_OUTPUT_SCHEMA_INVALID") -> Never:
    raise C08BuildError(code, "EXPLANATION_DEGRADED", repairable_schema=True)


def _grounding_fail(code: str) -> Never:
    raise C08BuildError(code, "EXPLANATION_DEGRADED")


def _revalidate(value: object) -> None:
    if not is_dataclass(value) or isinstance(value, type):
        return
    for field in fields(value):
        item = getattr(value, field.name)
        if isinstance(item, tuple):
            for member in item:
                _revalidate(member)
        else:
            _revalidate(item)
    post_init = getattr(type(value), "__post_init__", None)
    if post_init is not None:
        post_init(value)


def validate_decision_packet(packet: DecisionPacket) -> bytes:
    """Revalidate the immutable C01/C05 envelope and return its canonical bytes."""

    if not isinstance(packet, DecisionPacket):
        raise C08BuildError("C08_INVALID_PACKET_TYPE", "BLOCKED_CONTRACT")
    try:
        _revalidate(packet)
        packet_bytes = canonical_json_bytes(packet)
    except (TypeError, ValueError) as error:
        raise C08BuildError("C08_NONCANONICAL_PACKET", "BLOCKED_CONTRACT") from error

    provenance = packet.provenance
    expected_inputs = tuple(
        sorted(
            (
                packet.run.run_id,
                packet.snapshot.snapshot_id,
                packet.evidence.evidence_bundle_id,
                packet.signals.signal_bundle_id,
                packet.diagnosis.diagnosis_id,
                packet.candidates.candidate_set_id,
                packet.simulations.simulation_bundle_id,
                packet.recommendation.recommendation_id,
            )
        )
    )
    if (
        packet.schema_version != "decision-packet.v1"
        or provenance.producer != "flowlens.decision.c05_packet"
        or provenance.producer_version != PACKET_POLICY_VERSION
        or provenance.input_artifact_ids != expected_inputs
        or provenance.source_refs != source_refs_for(packet.evidence.evidence)
        or provenance.contract_versions != _EXPECTED_PACKET_CONTRACTS
    ):
        raise C08BuildError("C08_C05_PACKET_PROVENANCE_INVALID", "BLOCKED_CONTRACT")

    as_of_time = packet.run.as_of_time
    if any(
        item.available_at > as_of_time
        or (item.observed_at is not None and item.observed_at > as_of_time)
        for item in packet.evidence.evidence
    ) or any(ref.available_at > as_of_time for ref in provenance.source_refs):
        raise C08BuildError("C08_FUTURE_INPUT", "BLOCKED_TEMPORAL")

    lowered = packet_bytes.decode("utf-8").lower()
    if any(token in lowered for token in _HGT_TOKENS):
        raise C08BuildError("C08_HGT_OR_EVALUATION_INPUT_PROHIBITED", "BLOCKED_HGT")
    return packet_bytes


def assert_packet_unchanged(packet: DecisionPacket, before: bytes) -> None:
    if canonical_json_bytes(packet) != before:
        raise C08BuildError("C08_PACKET_MUTATION", "BLOCKED_CONTRACT")


def _string_list(value: object, *, code: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(type(item) is not str for item in value):
        _schema_fail(code)
    result: tuple[str, ...] = tuple(value)
    if result != tuple(sorted(set(result))):
        _schema_fail(code)
    return result


def _parse_schema(raw_output: str) -> ValidatedProviderOutput:
    if type(raw_output) is not str:
        _schema_fail("C08_OUTPUT_NOT_TEXT")
    try:
        value = json.loads(raw_output)
    except json.JSONDecodeError as error:
        raise C08BuildError(
            "C08_OUTPUT_NOT_JSON", "EXPLANATION_DEGRADED", repairable_schema=True
        ) from error
    if type(value) is not dict or set(value) != {"schema_version", "sections"}:
        _schema_fail()
    if value["schema_version"] != OUTPUT_SCHEMA_VERSION:
        _schema_fail()
    sections = value["sections"]
    if type(sections) is not list or len(sections) != len(MODEL_SECTION_KEYS):
        _schema_fail()

    validated: list[ValidatedSection] = []
    for expected_key, section in zip(MODEL_SECTION_KEYS, sections, strict=True):
        if type(section) is not dict or set(section) != {
            "section_key",
            "text",
            "evidence_ids",
            "reason_codes",
        }:
            _schema_fail()
        if section["section_key"] != expected_key:
            _schema_fail("C08_SECTION_ORDER_INVALID")
        text = section["text"]
        if (
            type(text) is not str
            or not text
            or text != text.strip()
            or len(text) > MAX_SECTION_TEXT_CHARS
            or not text.isascii()
            or re.search(r"[A-Za-z]", text) is None
        ):
            _schema_fail("C08_SECTION_TEXT_INVALID")
        validated.append(
            ValidatedSection(
                section_key=expected_key,
                text=text,
                evidence_ids=_string_list(
                    section["evidence_ids"], code="C08_EVIDENCE_REFERENCE_ORDER_INVALID"
                ),
                reason_codes=_string_list(
                    section["reason_codes"], code="C08_REASON_REFERENCE_ORDER_INVALID"
                ),
            )
        )
    if sum(len(item.text) for item in validated) > MAX_TOTAL_MODEL_TEXT_CHARS:
        _schema_fail("C08_TOTAL_TEXT_LENGTH_INVALID")
    return ValidatedProviderOutput(
        schema_version=OUTPUT_SCHEMA_VERSION,
        sections=tuple(validated),
    )


def _known_identifiers(context: ExplanationContextV1) -> set[str]:
    return {
        context.run_id,
        context.packet_id,
        *context.allowed_evidence_ids,
        *context.recommendation.candidate_order,
        *(item.candidate_id for item in context.simulations),
    }


def _numeric_tokens(value: object) -> set[str]:
    return set(NUMERIC_OR_TEMPORAL_PATTERN.findall(canonical_json_text(value)))


def _assert_no_high_risk_match(pattern: re.Pattern[str], text: str, code: str) -> None:
    if pattern.search(text):
        _grounding_fail(code)


def _validate_recommendation_summary(
    section: ValidatedSection,
    context: ExplanationContextV1,
) -> None:
    text = section.text
    recommendation = context.recommendation
    dispositions = {item.value for item in RecommendationDisposition}
    present_dispositions = {item for item in dispositions if item in text}
    if recommendation.disposition.value not in present_dispositions or present_dispositions != {
        recommendation.disposition.value
    }:
        _grounding_fail("C08_RECOMMENDATION_DRIFT")

    selected_id = recommendation.selected_candidate_id
    candidate_ids = set(recommendation.candidate_order)
    mentioned_ids = candidate_ids & set(ARTIFACT_ID_PATTERN.findall(text))
    if selected_id is None:
        if mentioned_ids:
            _grounding_fail("C08_RECOMMENDATION_DRIFT")
    elif mentioned_ids - {selected_id}:
        _grounding_fail("C08_RECOMMENDATION_DRIFT")

    family_values = {item.value for item in InterventionFamily}
    mentioned_families = {item for item in family_values if item in text}
    selected_family = recommendation.selected_candidate_family
    allowed_families = {selected_family.value} if selected_family is not None else set()
    if recommendation.disposition is RecommendationDisposition.NO_ACTION:
        allowed_families.add(InterventionFamily.NO_ACTION.value)
    if mentioned_families - allowed_families:
        _grounding_fail("C08_RECOMMENDATION_DRIFT")


def validate_provider_output(
    raw_output: str,
    context: ExplanationContextV1,
) -> ValidatedProviderOutput:
    """Validate exact transport schema plus grounding and unsupported claims."""

    output = _parse_schema(raw_output)
    allowed_evidence = set(context.allowed_evidence_ids)
    allowed_reasons = set(context.allowed_reason_codes)
    known_ids = _known_identifiers(context)
    allowed_numeric = _numeric_tokens(context)

    for section in output.sections:
        if not set(section.evidence_ids).issubset(allowed_evidence):
            _grounding_fail("C08_EVIDENCE_REFERENCE_NOT_ALLOWED")
        if not set(section.reason_codes).issubset(allowed_reasons):
            _grounding_fail("C08_REASON_REFERENCE_NOT_ALLOWED")
        _assert_no_high_risk_match(
            SIMULATION_EFFICACY_PATTERN,
            section.text,
            "C08_SIMULATION_EFFICACY_OVERCLAIM",
        )
        _assert_no_high_risk_match(CAUSAL_CLAIM_PATTERN, section.text, "C08_POSITIVE_CAUSAL_CLAIM")
        _assert_no_high_risk_match(
            PROBABILITY_CLAIM_PATTERN,
            section.text,
            "C08_CONFIDENCE_OR_GUARANTEE_CLAIM",
        )
        _assert_no_high_risk_match(
            FORBIDDEN_INFERENCE_PATTERN,
            section.text,
            "C08_FORBIDDEN_OPERATIONAL_INFERENCE",
        )
        identifiers = set(ARTIFACT_ID_PATTERN.findall(section.text))
        if not identifiers.issubset(known_ids):
            _grounding_fail("C08_UNKNOWN_IDENTIFIER")
        if not set(NUMERIC_OR_TEMPORAL_PATTERN.findall(section.text)).issubset(allowed_numeric):
            _grounding_fail("C08_UNSUPPORTED_NUMERIC_OR_TEMPORAL_CLAIM")
        if INJECTION_OR_CAPABILITY_PATTERN.search(section.text):
            _grounding_fail("C08_PROMPT_INJECTION_OR_CAPABILITY_REQUEST")

    _validate_recommendation_summary(output.sections[0], context)
    if any(
        item.status.value in {"UNKNOWN", "INSUFFICIENT_EVIDENCE"} for item in context.uncertainties
    ) and any(_UNKNOWN_RESOLUTION_PATTERN.search(item.text) for item in output.sections):
        _grounding_fail("C08_UNKNOWN_RESOLUTION")
    return output
