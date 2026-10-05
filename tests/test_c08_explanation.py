"""End-to-end bounded explanation behavior for W03-C08."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass

import pytest

from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.c08_context import ExplanationContextV1, build_explanation_context
from flowlens.decision.c08_explanation import explain_decision_packet
from flowlens.decision.c08_policy import FINAL_SECTION_KEYS, OUTPUT_SCHEMA_VERSION
from flowlens.decision.c08_provider import (
    C08ProviderRefusal,
    C08ProviderTransportError,
    ProviderRequest,
    ProviderResponse,
)
from flowlens.decision.contracts import DecisionPacket, ExplanationRecord
from flowlens.decision.enums import ExplanationMode
from flowlens.decision.serialization import canonical_json_bytes, canonical_json_text
from test_c05_recommendation import supplier_fixture


def make_packet() -> DecisionPacket:
    fixture = supplier_fixture()
    recommendation = build_recommendation(*fixture.args())
    return build_decision_packet(*fixture.args(), recommendation=recommendation)


def _token(value: object) -> str:
    return canonical_json_text(value)


def valid_output(context: ExplanationContextV1) -> str:
    recommendation = context.recommendation
    if recommendation.selected_candidate_id is None:
        selection = "Selected candidate: none."
    else:
        assert recommendation.selected_candidate_family is not None
        assert recommendation.selected_candidate_registry_key is not None
        selection = (
            f"Selected candidate: id {_token(recommendation.selected_candidate_id)}; "
            f"family {recommendation.selected_candidate_family.value}; registry "
            f"{_token(recommendation.selected_candidate_registry_key)}."
        )
    recommendation_text = " ".join(
        (
            f"Recommendation disposition: {recommendation.disposition.value}.",
            selection,
            f"Candidate order: {_token(recommendation.candidate_order)}.",
        )
    )

    claim = context.diagnosis.claims[0]
    signal = context.signals[0]
    evidence = context.evidence[0]
    diagnosis_text = " ".join(
        (
            f"Diagnosis problem code: {_token(context.diagnosis.problem_code)}.",
            f"Claim: code {_token(claim.claim_code)}; type {claim.claim_type.value}.",
            f"Signal: type {signal.signal_type.value}; state {signal.state.value}.",
            (
                f"Evidence: id {_token(evidence.evidence_id)}; "
                f"source entity {_token(evidence.source_entity)}; "
                f"source record {_token(evidence.source_record_id)}; "
                f"source field {_token(evidence.source_field)}; "
                f"value {_token(evidence.value)}; "
                f"observed at {_token(evidence.observed_at)}; "
                f"available at {_token(evidence.available_at)}; "
                f"relationship {evidence.relationship_type}; trust {evidence.trust_level.value}; "
                f"freshness {evidence.freshness_status.value}."
            ),
        )
    )
    diagnosis_evidence_ids = sorted(
        {*claim.evidence_ids, *signal.evidence_ids, evidence.evidence_id}
    )

    simulation = next(item for item in context.simulations if item.measurements)
    measurement = simulation.measurements[0]
    simulation_text = " ".join(
        (
            "Simulations are modeled comparisons for human review.",
            (
                f"Simulation: candidate {_token(simulation.candidate_id)}; "
                f"family {simulation.family.value}; status {simulation.status.value}."
            ),
            (
                f"Measurement: candidate {_token(simulation.candidate_id)}; "
                f"name {_token(measurement.name)}; value {_token(measurement.value)}; "
                f"unit {_token(measurement.unit)}."
            ),
        )
    )

    uncertainty = next(
        item
        for item in context.uncertainties
        if item.status.value in {"UNKNOWN", "INSUFFICIENT_EVIDENCE"}
    )
    limitation = context.limitations[0]
    uncertainty_text = " ".join(
        (
            "Uncertainties and limitations require human review.",
            f"Uncertainty: code {_token(uncertainty.code)}; status {uncertainty.status.value}.",
            f"Limitation: code {_token(limitation.code)}.",
        )
    )
    return json.dumps(
        {
            "schema_version": OUTPUT_SCHEMA_VERSION,
            "sections": [
                {
                    "section_key": "recommendation_summary",
                    "text": recommendation_text,
                    "evidence_ids": [],
                    "reason_codes": list(recommendation.reason_codes),
                },
                {
                    "section_key": "evidence_and_diagnosis",
                    "text": diagnosis_text,
                    "evidence_ids": diagnosis_evidence_ids,
                    "reason_codes": list(signal.reason_codes),
                },
                {
                    "section_key": "simulation_context",
                    "text": simulation_text,
                    "evidence_ids": [],
                    "reason_codes": [],
                },
                {
                    "section_key": "uncertainties_and_limitations",
                    "text": uncertainty_text,
                    "evidence_ids": list(uncertainty.evidence_ids),
                    "reason_codes": [],
                },
            ],
        },
        separators=(",", ":"),
    )


@dataclass
class FakeProvider:
    outcomes: list[ProviderResponse | Exception]

    def __post_init__(self) -> None:
        self.calls: list[ProviderRequest] = []

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        self.calls.append(request)
        if not self.outcomes:
            raise AssertionError("unexpected provider call")
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def responses(values: Iterable[str]) -> list[ProviderResponse | Exception]:
    return [ProviderResponse(output_text=item, resolved_model="gpt-5.6-terra") for item in values]


def test_template_mode_constructs_valid_c01_identity_without_provider() -> None:
    packet = make_packet()
    before = canonical_json_bytes(packet)
    provider = FakeProvider([])

    first = explain_decision_packet(packet, provider=provider, mode="template")
    second = explain_decision_packet(packet, provider=provider, mode="template")

    assert first == second
    assert first.mode is ExplanationMode.DETERMINISTIC_TEMPLATE
    assert first.schema_version == "explanation-record.v1"
    assert first.run_id == packet.run.run_id
    assert first.packet_id == packet.packet_id
    assert first.explanation_id.startswith("exp_")
    assert tuple(item.section_key for item in first.sections) == FINAL_SECTION_KEYS
    assert provider.calls == []
    assert canonical_json_bytes(packet) == before


def test_valid_provider_output_is_bounded_llm_and_records_resolved_model() -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    provider = FakeProvider(responses([valid_output(context)]))

    result = explain_decision_packet(packet, provider=provider, mode="openai")

    assert result.mode is ExplanationMode.BOUNDED_LLM
    assert len(provider.calls) == 1
    assert "C08_SCHEMA_REPAIR_USED" not in result.reason_codes
    assert "C08_LLM_SEMANTIC_NOT_BYTE_DETERMINISTIC" in {item.code for item in result.limitations}
    versions = {item.name: item.version for item in result.provenance.contract_versions}
    assert versions["w03-c08-provider"] == "openai"
    assert versions["w03-c08-requested-model"] == "gpt-5.6-terra"
    assert versions["w03-c08-resolved-model"] == "gpt-5.6-terra"


def test_one_schema_repair_can_succeed() -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    provider = FakeProvider(responses(["not-json", valid_output(context)]))

    result = explain_decision_packet(packet, provider=provider, mode="openai")

    assert result.mode is ExplanationMode.BOUNDED_LLM
    assert len(provider.calls) == 2
    assert provider.calls[0] == provider.calls[1]
    assert "C08_SCHEMA_REPAIR_USED" in result.reason_codes


def test_schema_repair_followed_by_ungrounded_output_degrades_at_two_calls() -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    payload = json.loads(valid_output(context))
    payload["sections"][1]["text"] = "The supplier is overseas."
    provider = FakeProvider(
        responses(["not-json", json.dumps(payload, separators=(",", ":"))])
    )
    before = canonical_json_bytes(packet)
    frozen_recommendation = packet.recommendation

    result = explain_decision_packet(packet, provider=provider, mode="openai")

    assert result.mode is ExplanationMode.DEGRADED_TEMPLATE
    assert len(provider.calls) == 2
    assert canonical_json_bytes(packet) == before
    assert packet.recommendation == frozen_recommendation


def test_second_schema_failure_degrades_after_exactly_two_calls() -> None:
    provider = FakeProvider(responses(["not-json", "still-not-json"]))

    result = explain_decision_packet(make_packet(), provider=provider, mode="openai")

    assert result.mode is ExplanationMode.DEGRADED_TEMPLATE
    assert len(provider.calls) == 2
    assert "C08_EXPLANATION_DEGRADED" in result.reason_codes
    assert "C08_LLM_FALLBACK_USED" in {item.code for item in result.limitations}


@pytest.mark.parametrize(
    "failure",
    (
        C08ProviderTransportError("timeout"),
        C08ProviderRefusal("refused"),
    ),
)
def test_expected_provider_failure_degrades_without_retry(failure: Exception) -> None:
    provider = FakeProvider([failure])

    result = explain_decision_packet(make_packet(), provider=provider, mode="openai")

    assert result.mode is ExplanationMode.DEGRADED_TEMPLATE
    assert len(provider.calls) == 1


@pytest.mark.parametrize("failure", (RuntimeError("bug"), AssertionError("bug")))
def test_unexpected_provider_programming_failure_propagates(
    failure: Exception,
) -> None:
    provider = FakeProvider([failure])

    with pytest.raises(type(failure), match="bug"):
        explain_decision_packet(make_packet(), provider=provider, mode="openai")

    assert len(provider.calls) == 1


def test_expected_provider_failure_during_schema_repair_degrades_at_two_calls() -> None:
    provider = FakeProvider(
        [
            *responses(["not-json"]),
            C08ProviderTransportError("repair transport failure"),
        ]
    )

    result = explain_decision_packet(make_packet(), provider=provider, mode="openai")

    assert result.mode is ExplanationMode.DEGRADED_TEMPLATE
    assert len(provider.calls) == 2


@pytest.mark.parametrize(
    "text",
    (
        "The supplier is overseas.",
        "Supplier delay led to the late delivery.",
        "The delay resulted from the supplier issue.",
        "The delivery was late because of the supplier.",
        "The intervention is likely to succeed.",
        "There is a high chance the intervention will work.",
        "The uncertainty has cleared.",
        "No ambiguity remains.",
        "The supplier status is now understood.",
        "There is no uncertainty in the packet. The root cause is supplier delay.",
        "The packet is not empty. Supplier delay caused the outcome.",
        "There is no missing evidence. Confidence is 90%.",
        "The recommendation is not executable. The simulation guarantees success.",
        "There is no operational request. Quality release is approved.",
        "There is no allocation today. Use order-specific procurement allocation.",
    ),
)
def test_arbitrary_or_high_risk_prose_degrades_without_schema_repair(text: str) -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    payload = json.loads(valid_output(context))
    payload["sections"][1]["text"] = text
    provider = FakeProvider(
        responses([json.dumps(payload, separators=(",", ":")), valid_output(context)])
    )
    before = canonical_json_bytes(packet)
    frozen_recommendation = packet.recommendation

    result = explain_decision_packet(packet, provider=provider, mode="openai")

    assert result.mode is ExplanationMode.DEGRADED_TEMPLATE
    assert len(provider.calls) == 1
    assert "C08_SCHEMA_REPAIR_USED" not in result.reason_codes
    assert canonical_json_bytes(packet) == before
    assert packet.recommendation == frozen_recommendation
    selected = frozen_recommendation.selected_candidate_id
    if selected is not None:
        assert selected in result.sections[0].text


def test_fixed_safe_uncertainty_boundary_is_accepted() -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    payload = json.loads(valid_output(context))
    payload["sections"][3]["text"] = (
        "Uncertainties and limitations require human review."
    )
    payload["sections"][3]["evidence_ids"] = []
    provider = FakeProvider(responses([json.dumps(payload, separators=(",", ":"))]))

    result = explain_decision_packet(packet, provider=provider, mode="openai")

    assert result.mode is ExplanationMode.BOUNDED_LLM
    assert len(provider.calls) == 1


@pytest.mark.parametrize("failure_type", (RuntimeError, AssertionError))
def test_unexpected_validator_failure_propagates(
    monkeypatch: pytest.MonkeyPatch,
    failure_type: type[Exception],
) -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    provider = FakeProvider(responses([valid_output(context)]))

    def fail_validation(*_args: object, **_kwargs: object) -> object:
        raise failure_type("validator bug")

    monkeypatch.setattr(
        "flowlens.decision.c08_explanation.validate_provider_output",
        fail_validation,
    )

    with pytest.raises(failure_type, match="validator bug"):
        explain_decision_packet(packet, provider=provider, mode="openai")

    assert len(provider.calls) == 1


def test_unexpected_orchestration_failure_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    provider = FakeProvider(responses([valid_output(context)]))

    def fail_build(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("orchestration bug")

    monkeypatch.setattr("flowlens.decision.c08_explanation._build_record", fail_build)

    with pytest.raises(AssertionError, match="orchestration bug"):
        explain_decision_packet(packet, provider=provider, mode="openai")

    assert len(provider.calls) == 1


def test_missing_api_key_uses_deterministic_template(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FLOWLENS_OPENAI_API_KEY", raising=False)

    result = explain_decision_packet(make_packet(), mode="openai")

    assert result.mode is ExplanationMode.DETERMINISTIC_TEMPLATE
    versions = {item.name: item.version for item in result.provenance.contract_versions}
    assert versions["w03-c08-provider"] == "none"
    assert versions["w03-c08-requested-model"] == "none"


def test_explanation_record_has_complete_referenced_source_provenance() -> None:
    packet = make_packet()
    result: ExplanationRecord = explain_decision_packet(packet)
    selected = {
        ref
        for evidence in packet.evidence.evidence
        if evidence.evidence_id in result.referenced_evidence_ids
        for ref in evidence.provenance.source_refs
    }

    assert set(result.provenance.source_refs) == selected
    assert set(packet.limitations).issubset(result.limitations)


def test_repeated_successful_llm_results_preserve_semantic_contract() -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    output = valid_output(context)
    provider = FakeProvider(responses([output, output]))

    first = explain_decision_packet(packet, provider=provider, mode="openai")
    second = explain_decision_packet(packet, provider=provider, mode="openai")

    assert first.mode is second.mode is ExplanationMode.BOUNDED_LLM
    assert tuple(item.section_key for item in first.sections) == FINAL_SECTION_KEYS
    assert tuple(item.section_key for item in second.sections) == FINAL_SECTION_KEYS
    assert first.referenced_evidence_ids == second.referenced_evidence_ids
    assert first.reason_codes == second.reason_codes
    assert packet.recommendation.disposition.value in first.sections[0].text
    assert packet.recommendation.disposition.value in second.sections[0].text
