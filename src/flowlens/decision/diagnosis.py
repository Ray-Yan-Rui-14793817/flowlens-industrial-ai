"""Deterministic W03-C03 diagnosis over a canonically rebuilt SignalBundle."""

from __future__ import annotations

from flowlens.decision.c03_policy import C03_PRODUCER_VERSION, SIGNAL_POLICIES
from flowlens.decision.c03_validation import (
    C03BuildError,
    source_refs_for,
    validate_c03_inputs,
)
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import DiagnosisRecord, EvidenceBundle, SignalBundle
from flowlens.decision.enums import ClaimType, SignalState, SignalType, UncertaintyStatus
from flowlens.decision.primitives import (
    ArtifactProvenance,
    DiagnosisClaim,
    EntityRef,
    Uncertainty,
    VersionRef,
)
from flowlens.decision.serialization import canonical_json_bytes, derive_artifact_id
from flowlens.decision.signals import build_signal_bundle


def _problem_code(signals: SignalBundle) -> str:
    delivery = next(
        item for item in signals.signals if item.signal_type is SignalType.DELIVERY_RISK
    )
    if delivery.state is SignalState.ACTIVE:
        return "DELIVERY_COMMITMENT_WARNING"
    if any(item.state is SignalState.ACTIVE for item in signals.signals):
        return "OBSERVED_DELIVERY_RISK_INDICATORS"
    return "INSUFFICIENT_EVIDENCE_FOR_RISK_ASSESSMENT"


def _claims(signals: SignalBundle) -> tuple[DiagnosisClaim, ...]:
    result: list[DiagnosisClaim] = []
    for signal in signals.signals:
        if signal.state is SignalState.INACTIVE:
            continue
        policy = SIGNAL_POLICIES[signal.signal_type]
        if signal.state is SignalState.ACTIVE:
            claim_type = policy.active_claim_type
            statement = policy.active_statement
            if claim_type is None or statement is None:
                raise C03BuildError("C03_SIGNAL_POLICY_MISMATCH", "BLOCKED_CONTRACT")
        else:
            claim_type = ClaimType.UNCERTAINTY_STATEMENT
            statement = policy.unknown_statement
        result.append(
            DiagnosisClaim(
                claim_code=f"C03_{signal.signal_type.value}_{signal.state.value}_V1",
                claim_type=claim_type,
                statement=statement,
                evidence_ids=signal.evidence_ids,
                limitations=signal.limitations,
            )
        )
    return tuple(result)


def _uncertainties(context: DecisionContext, signals: SignalBundle) -> tuple[Uncertainty, ...]:
    result = list(context.uncertainties)
    for signal in signals.signals:
        policy = SIGNAL_POLICIES[signal.signal_type]
        if signal.state is SignalState.UNKNOWN:
            result.append(
                Uncertainty(
                    status=UncertaintyStatus.INSUFFICIENT_EVIDENCE,
                    code=f"C03_UNKNOWN_{signal.signal_type.value}",
                    message=policy.unknown_statement,
                    evidence_ids=signal.evidence_ids,
                )
            )
        if signal.state is SignalState.ACTIVE and "C03_INPUT_INCOMPLETE" in signal.reason_codes:
            result.append(
                Uncertainty(
                    status=UncertaintyStatus.INSUFFICIENT_EVIDENCE,
                    code=f"C03_PARTIAL_{signal.signal_type.value}",
                    message=(
                        "A positive witness exists, but some rule-relevant evidence is incomplete."
                    ),
                    evidence_ids=signal.evidence_ids,
                )
            )
    unique = {
        (item.status.value, item.code, item.message, item.evidence_ids): item for item in result
    }
    return tuple(unique[key] for key in sorted(unique))


def build_diagnosis(
    bundle: EvidenceBundle,
    context: DecisionContext,
    signals: SignalBundle,
) -> DiagnosisRecord:
    """Reject noncanonical supplied signals, then build a structured non-causal diagnosis."""
    index = validate_c03_inputs(bundle, context)
    canonical = build_signal_bundle(bundle, context)
    if not isinstance(signals, SignalBundle) or canonical_json_bytes(
        signals
    ) != canonical_json_bytes(canonical):
        raise C03BuildError("C03_SIGNAL_POLICY_MISMATCH", "BLOCKED_CONTRACT")

    claims = _claims(canonical)
    supporting_signal_ids = tuple(sorted(item.signal_id for item in canonical.signals))
    supporting_evidence_ids = tuple(
        sorted(
            {
                *(evidence_id for item in canonical.signals for evidence_id in item.evidence_ids),
                *(
                    evidence_id
                    for uncertainty in context.uncertainties
                    for evidence_id in uncertainty.evidence_ids
                ),
            }
        )
    )
    uncertainties = _uncertainties(context, canonical)
    reason_codes = tuple(
        sorted(
            {
                "C03_STRUCTURED_NOT_CAUSAL",
                *(code for item in canonical.signals for code in item.reason_codes),
            }
        )
    )
    affected_path = (EntityRef(entity_type="fact_sales_order", entity_id=context.order_id),)
    problem_code = _problem_code(canonical)
    identity = {
        "run_id": context.run_id,
        "snapshot_id": context.snapshot_id,
        "problem_code": problem_code,
        "claims": claims,
        "supporting_signal_ids": supporting_signal_ids,
        "supporting_evidence_ids": supporting_evidence_ids,
        "uncertainties": uncertainties,
        "affected_path": affected_path,
        "reason_codes": reason_codes,
    }
    supporting_evidence = tuple(index.by_id[item] for item in supporting_evidence_ids)
    return DiagnosisRecord(
        diagnosis_id=derive_artifact_id("diagnosis-record", "diagnosis-record.v1", identity),
        schema_version="diagnosis-record.v1",
        run_id=context.run_id,
        snapshot_id=context.snapshot_id,
        problem_code=problem_code,
        claims=claims,
        supporting_signal_ids=supporting_signal_ids,
        supporting_evidence_ids=supporting_evidence_ids,
        uncertainties=uncertainties,
        affected_path=affected_path,
        reason_codes=reason_codes,
        provenance=ArtifactProvenance(
            producer="flowlens.decision.diagnosis",
            producer_version=C03_PRODUCER_VERSION,
            input_artifact_ids=tuple(
                sorted(
                    (
                        bundle.evidence_bundle_id,
                        context.context_id,
                        canonical.signal_bundle_id,
                    )
                )
            ),
            source_refs=source_refs_for(supporting_evidence),
            contract_versions=(
                VersionRef(name="w03-c01", version="v1"),
                VersionRef(name="w03-c02", version="v1"),
                VersionRef(name="w03-c02-context", version="v1"),
                VersionRef(name="w03-c03", version="v1"),
                VersionRef(name="w03-c03-diagnosis", version="v1"),
                VersionRef(name="w03-c03-signals", version="v1"),
            ),
            implementation_sha=None,
        ),
    )


def evaluate_c03(
    bundle: EvidenceBundle, context: DecisionContext
) -> tuple[SignalBundle, DiagnosisRecord]:
    """Run the complete pure C03 signal-plus-diagnosis evaluation."""
    signals = build_signal_bundle(bundle, context)
    return signals, build_diagnosis(bundle, context, signals)
