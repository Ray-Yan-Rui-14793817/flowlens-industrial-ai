"""Recommendation grounding, schema, degradation, and replay tests for W03-C05."""

from __future__ import annotations

import hashlib
import subprocess
import sys

from flowlens.decision.c05_policy import StressEffect, score_component_names
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.enums import (
    InterventionFamily,
    RecommendationDisposition,
    SimulationStatus,
)
from flowlens.decision.serialization import canonical_json_bytes
from test_c05_policy import (
    C05Fixture,
    make_fixture,
    neutral_records,
    records_for_active,
    with_simulations,
)


def supplier_fixture() -> C05Fixture:
    family = InterventionFamily.SUPPLIER_INTERVENTION
    return with_simulations(
        make_fixture(records_for_active(family)),
        {family: (SimulationStatus.SUCCEEDED, StressEffect.WORSENED)},
    )


def test_investigation_recommendation_is_exactly_grounded_and_categorical() -> None:
    fixture = supplier_fixture()
    first = build_recommendation(*fixture.args())
    second = build_recommendation(*fixture.args())
    selected = next(
        item
        for item in fixture.candidates.candidates
        if item.family is InterventionFamily.SUPPLIER_INTERVENTION
    )

    assert first == second
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert first.disposition is RecommendationDisposition.INVESTIGATION_ONLY
    assert first.selected_candidate_id == selected.candidate_id
    assert first.supporting_evidence_ids == tuple(
        sorted(
            {
                *fixture.diagnosis.supporting_evidence_ids,
                *selected.supporting_evidence_ids,
            }
        )
    )
    assert tuple(item.name for item in first.score_components) == score_component_names()
    assert len(first.score_components) == 21
    assert all(
        type(item.value) in (bool, int, str) and item.unit is None
        for item in first.score_components
    )
    assert "C05_SELECTED_FROM_ACTIVE_RELEVANCE" in first.reason_codes
    assert "C05_UNIQUE_STRESS_SENSITIVE_INVESTIGATION" in first.reason_codes
    limitation_codes = {item.code for item in first.limitations}
    assert {
        "C03_ASSOCIATION_NOT_ALLOCATION",
        "C04_SCENARIO_SCOPE_NOT_ORDER_TARGETED",
        "C04_STRESS_PROBE_NOT_INTERVENTION_EFFICACY",
        "C05_HUMAN_AUTHORITY_REQUIRED",
        "C05_INVESTIGATION_NOT_EXECUTION",
        "C05_NO_OPERATIONAL_ACTION_AUTHORITY",
        "C05_STRESS_PROBE_NOT_INTERVENTION_EFFICACY",
    } <= limitation_codes
    assert first.provenance.producer == "flowlens.decision.c05_recommendation"
    assert first.provenance.producer_version == "w03-c05-decision-v1"


def test_no_action_no_recommendation_and_tie_have_exact_degradation_markers() -> None:
    neutral = make_fixture(neutral_records())
    no_action = build_recommendation(*neutral.args())
    assert no_action.disposition is RecommendationDisposition.NO_ACTION
    assert {
        "C05_NEUTRAL_NO_ACTION",
        "C05_NO_ACTIVE_INTERVENTION_RELEVANCE",
    } <= set(no_action.reason_codes)
    assert "C05_NO_ACTION_NOT_OPERATIONAL_EXECUTION" in {
        item.code for item in no_action.limitations
    }

    insufficient = build_recommendation(*make_fixture().args())
    assert insufficient.disposition is RecommendationDisposition.NO_RECOMMENDATION
    assert "C05_INSUFFICIENT_RECOMMENDATION_BASIS" in insufficient.reason_codes
    assert "C05_INSUFFICIENT_RECOMMENDATION_BASIS" in {
        item.code for item in insufficient.uncertainties
    }


def test_tie_is_visible_and_never_resolved_by_candidate_identifier() -> None:
    from test_c03_signals import CASES, _records_for_case

    case = next(item for item in CASES if item["case_id"] == "C03-G27")
    fixture = make_fixture(list(_records_for_case(case)))
    fixture = with_simulations(
        fixture,
        {
            InterventionFamily.SUPPLIER_INTERVENTION: (
                SimulationStatus.SUCCEEDED,
                StressEffect.WORSENED,
            ),
            InterventionFamily.QUALITY_INTERVENTION: (
                SimulationStatus.SUCCEEDED,
                StressEffect.WORSENED,
            ),
        },
    )
    recommendation = build_recommendation(*fixture.args())
    assert recommendation.disposition is RecommendationDisposition.DEFER_TO_HUMAN
    assert recommendation.selected_candidate_id is None
    assert "C05_TOP_TIE_DEFERRED" in recommendation.reason_codes
    assert "C05_TOP_TIE" in {item.code for item in recommendation.uncertainties}
    assert "C05_TIE_NOT_AUTO_RESOLVED" in {
        item.code for item in recommendation.limitations
    }


def test_reserved_candidate_recommended_is_never_emitted_across_policy_outcomes() -> None:
    fixtures = [
        make_fixture(neutral_records()),
        make_fixture(),
        supplier_fixture(),
    ]
    assert all(
        build_recommendation(*fixture.args()).disposition
        is not RecommendationDisposition.CANDIDATE_RECOMMENDED
        for fixture in fixtures
    )


def test_recommendation_replays_in_fresh_process() -> None:
    local = build_recommendation(*supplier_fixture().args())
    digest = hashlib.sha256(canonical_json_bytes(local)).hexdigest()
    code = """
import hashlib
import sys
sys.path.insert(0, 'tests')
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.serialization import canonical_json_bytes
from test_c05_recommendation import supplier_fixture
value = build_recommendation(*supplier_fixture().args())
print(value.recommendation_id)
print(hashlib.sha256(canonical_json_bytes(value)).hexdigest())
"""
    for _ in range(2):
        completed = subprocess.run(
            [sys.executable, "-c", code],
            check=True,
            capture_output=True,
            text=True,
        )
        assert completed.stdout.splitlines() == [local.recommendation_id, digest]
