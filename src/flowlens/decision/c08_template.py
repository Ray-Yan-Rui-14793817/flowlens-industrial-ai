"""Deterministic packet-only explanation template for W03-C08."""

from __future__ import annotations

from flowlens.decision.c08_context import ExplanationContextV1
from flowlens.decision.c08_policy import HUMAN_REVIEW_BOUNDARY
from flowlens.decision.primitives import ExplanationSection
from flowlens.decision.serialization import canonical_primitive


def _render_scalar(value: object) -> str:
    rendered = canonical_primitive(value)
    return "null" if rendered is None else str(rendered)


def render_deterministic_template(
    context: ExplanationContextV1,
) -> tuple[ExplanationSection, ...]:
    """Render all five final sections deterministically from context only."""

    recommendation = context.recommendation
    selected = "none"
    if recommendation.selected_candidate_id is not None:
        if (
            recommendation.selected_candidate_family is None
            or recommendation.selected_candidate_registry_key is None
        ):
            raise ValueError("selected candidate context is incomplete")
        selected = (
            f"{recommendation.selected_candidate_id} "
            f"({recommendation.selected_candidate_family.value}; "
            f"{recommendation.selected_candidate_registry_key})"
        )
    recommendation_text = (
        f"Frozen disposition: {recommendation.disposition.value}. "
        f"Selected candidate: {selected}. "
        f"Candidate order: {', '.join(recommendation.candidate_order)}."
    )

    claims = "; ".join(
        f"{item.claim_code} [{item.claim_type.value}]: {item.statement} "
        f"(evidence: {', '.join(item.evidence_ids) or 'none'})"
        for item in context.diagnosis.claims
    ) or "none"
    evidence_text = (
        f"Diagnosis: {context.diagnosis.problem_code}. Claims: {claims}. "
        f"Referenced evidence: {', '.join(context.allowed_evidence_ids) or 'none'}. "
        f"Referenced reason codes: {', '.join(context.allowed_reason_codes) or 'none'}."
    )

    simulations = "; ".join(
        f"{item.candidate_id} [{item.family.value}] status {item.status.value}; "
        + (
            "measurements "
            + ", ".join(
                f"{measurement.name}={_render_scalar(measurement.value)}"
                + (f" {measurement.unit}" if measurement.unit else "")
                for measurement in item.measurements
            )
            if item.measurements
            else "no measurements"
        )
        for item in context.simulations
    ) or "No simulation results are present."
    simulation_text = (
        f"Modeled simulation context: {simulations}. These are modeled comparisons only."
    )

    uncertainties = "; ".join(
        f"{item.status.value}/{item.code}: {item.message}"
        for item in context.uncertainties
    ) or "none"
    limitations = "; ".join(
        f"{item.code}: {item.message}" for item in context.limitations
    ) or "none"
    uncertainty_text = f"Uncertainties: {uncertainties}. Limitations: {limitations}."

    return (
        ExplanationSection(
            section_key="recommendation_summary",
            text=recommendation_text,
        ),
        ExplanationSection(
            section_key="evidence_and_diagnosis",
            text=evidence_text,
        ),
        ExplanationSection(
            section_key="simulation_context",
            text=simulation_text,
        ),
        ExplanationSection(
            section_key="uncertainties_and_limitations",
            text=uncertainty_text,
        ),
        ExplanationSection(
            section_key="human_review_boundary",
            text=HUMAN_REVIEW_BOUNDARY,
        ),
    )
