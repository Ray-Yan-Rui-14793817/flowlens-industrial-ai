"""Deterministic and bounded ExplanationContextV1 projection tests."""

from __future__ import annotations

from flowlens.decision.c08_context import build_explanation_context
from flowlens.decision.c08_policy import CONTEXT_SCHEMA_VERSION
from flowlens.decision.enums import SignalState
from flowlens.decision.serialization import canonical_json_bytes, canonical_json_text
from test_c08_explanation import make_packet


def test_context_is_deterministic_canonical_and_packet_only() -> None:
    packet = make_packet()
    before = canonical_json_bytes(packet)

    first = build_explanation_context(packet)
    second = build_explanation_context(packet)

    assert first == second
    assert first.schema_version == CONTEXT_SCHEMA_VERSION
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert canonical_json_bytes(packet) == before
    rendered = canonical_json_text(first).lower()
    for token in (
        "recommendation_evaluation",
        "outcome_evaluation",
        "hidden_ground_truth",
        "ground_truth",
        "hgt_",
    ):
        assert token not in rendered


def test_context_allowlists_are_exact_sorted_unions() -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    relevant = {
        item.candidate_id
        for item in packet.candidates.candidates
        if item.candidate_id == packet.recommendation.selected_candidate_id
        or "C04_RELEVANT_SIGNAL_ACTIVE" in item.reason_codes
    }
    expected_evidence = {
        *packet.recommendation.supporting_evidence_ids,
        *packet.diagnosis.supporting_evidence_ids,
        *(item for claim in packet.diagnosis.claims for item in claim.evidence_ids),
        *(
            item
            for signal in packet.signals.signals
            if signal.state is not SignalState.INACTIVE
            for item in signal.evidence_ids
        ),
        *(
            item
            for candidate in packet.candidates.candidates
            if candidate.candidate_id in relevant
            for item in candidate.supporting_evidence_ids
        ),
        *(item for uncertainty in packet.uncertainties for item in uncertainty.evidence_ids),
    }
    expected_reasons = {
        *packet.recommendation.reason_codes,
        *packet.diagnosis.reason_codes,
        *(
            item
            for signal in packet.signals.signals
            if signal.state is not SignalState.INACTIVE
            for item in signal.reason_codes
        ),
        *(
            item
            for candidate in packet.candidates.candidates
            if candidate.candidate_id in relevant
            for item in candidate.reason_codes
        ),
    }

    assert context.allowed_evidence_ids == tuple(sorted(expected_evidence))
    assert context.allowed_reason_codes == tuple(sorted(expected_reasons))
    assert tuple(item.evidence_id for item in context.evidence) == tuple(
        sorted(expected_evidence)
    )


def test_context_preserves_claim_trust_freshness_unknowns_and_limitations() -> None:
    packet = make_packet()
    context = build_explanation_context(packet)

    assert {item.claim_type for item in context.diagnosis.claims} == {
        item.claim_type for item in packet.diagnosis.claims
    }
    assert {(item.trust_level, item.freshness_status) for item in context.evidence} == {
        (item.trust_level, item.freshness_status)
        for item in packet.evidence.evidence
        if item.evidence_id in context.allowed_evidence_ids
    }
    assert {(item.status, item.code, item.message) for item in context.uncertainties} == {
        (item.status, item.code, item.message) for item in packet.uncertainties
    }
    assert {(item.code, item.message) for item in context.limitations} == {
        (item.code, item.message) for item in packet.limitations
    }
