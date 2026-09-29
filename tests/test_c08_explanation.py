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
from flowlens.decision.serialization import canonical_json_bytes
from test_c05_recommendation import supplier_fixture


def make_packet() -> DecisionPacket:
    fixture = supplier_fixture()
    recommendation = build_recommendation(*fixture.args())
    return build_decision_packet(*fixture.args(), recommendation=recommendation)


def valid_output(context: ExplanationContextV1) -> str:
    selected = context.recommendation.selected_candidate_id
    family = context.recommendation.selected_candidate_family
    selected_text = "No selected candidate."
    if selected is not None and family is not None:
        selected_text = f"Selected candidate {selected} with family {family.value}."
    evidence_ids = list(context.allowed_evidence_ids[:1])
    reason_codes = list(context.allowed_reason_codes[:1])
    return json.dumps(
        {
            "schema_version": OUTPUT_SCHEMA_VERSION,
            "sections": [
                {
                    "section_key": "recommendation_summary",
                    "text": (
                        f"Frozen disposition: {context.recommendation.disposition.value}. "
                        f"{selected_text}"
                    ),
                    "evidence_ids": [],
                    "reason_codes": reason_codes,
                },
                {
                    "section_key": "evidence_and_diagnosis",
                    "text": (
                        f"Diagnosis remains {context.diagnosis.problem_code} and uses "
                        "allowed packet evidence."
                    ),
                    "evidence_ids": evidence_ids,
                    "reason_codes": reason_codes,
                },
                {
                    "section_key": "simulation_context",
                    "text": "Modeled comparisons remain bounded context for human review.",
                    "evidence_ids": [],
                    "reason_codes": [],
                },
                {
                    "section_key": "uncertainties_and_limitations",
                    "text": ("Uncertainties and limitations remain unresolved for human review."),
                    "evidence_ids": [],
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
        "There is no uncertainty in the packet. The root cause is supplier delay.",
        "The packet is not empty. Supplier delay caused the outcome.",
        "There is no missing evidence. Confidence is 90%.",
        "The recommendation is not executable. The simulation guarantees success.",
        "There is no operational request. Quality release is approved.",
        "There is no allocation today. Use order-specific procurement allocation.",
    ),
)
def test_unrelated_negation_cannot_bypass_high_risk_claims(text: str) -> None:
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


def test_safe_causality_boundary_is_accepted() -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    payload = json.loads(valid_output(context))
    payload["sections"][3]["text"] = "Causality remains unresolved."
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
