"""Deterministic template fidelity and replay tests for W03-C08."""

from __future__ import annotations

import hashlib
import subprocess
import sys

from flowlens.decision.c08_context import build_explanation_context
from flowlens.decision.c08_explanation import explain_decision_packet
from flowlens.decision.c08_policy import FINAL_SECTION_KEYS, HUMAN_REVIEW_BOUNDARY
from flowlens.decision.c08_template import render_deterministic_template
from flowlens.decision.serialization import canonical_json_bytes
from test_c08_explanation import make_packet


def test_template_preserves_frozen_meaning_and_boundary() -> None:
    packet = make_packet()
    context = build_explanation_context(packet)
    sections = render_deterministic_template(context)

    assert tuple(item.section_key for item in sections) == FINAL_SECTION_KEYS
    assert context.recommendation.disposition.value in sections[0].text
    if context.recommendation.selected_candidate_id is not None:
        assert context.recommendation.selected_candidate_id in sections[0].text
    assert all(item in sections[1].text for item in context.allowed_evidence_ids)
    assert all(item.code in sections[3].text for item in context.uncertainties)
    assert all(item.message in sections[3].text for item in context.uncertainties)
    assert all(item.code in sections[3].text for item in context.limitations)
    assert all(item.message in sections[3].text for item in context.limitations)
    assert sections[-1].text == HUMAN_REVIEW_BOUNDARY


def test_same_packet_template_is_byte_identical_in_fresh_process() -> None:
    packet = make_packet()
    local = explain_decision_packet(packet)
    digest = hashlib.sha256(canonical_json_bytes(local)).hexdigest()
    code = """
import hashlib
import sys
sys.path.insert(0, 'tests')
from flowlens.decision.c08_explanation import explain_decision_packet
from flowlens.decision.serialization import canonical_json_bytes
from test_c08_explanation import make_packet
result = explain_decision_packet(make_packet())
print(result.explanation_id)
print(hashlib.sha256(canonical_json_bytes(result)).hexdigest())
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )

    assert completed.stdout.splitlines() == [local.explanation_id, digest]
