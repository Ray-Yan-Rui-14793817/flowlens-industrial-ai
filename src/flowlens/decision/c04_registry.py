"""Frozen four-family intervention registry for W03-C04."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Final

from flowlens.decision.c03_validation import source_refs_for
from flowlens.decision.c04_validation import validate_c04_inputs
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import (
    CandidateSet,
    DiagnosisRecord,
    EvidenceBundle,
    InterventionCandidate,
    SignalBundle,
)
from flowlens.decision.enums import InterventionFamily, SignalState, SignalType
from flowlens.decision.primitives import (
    ArtifactProvenance,
    Limitation,
    NamedValue,
    VersionRef,
)
from flowlens.decision.serialization import derive_artifact_id

REGISTRY_VERSION: Final = "w03-c04-registry-v1"
SCENARIO_ADAPTER_VERSION: Final = "w03-c04-scenario-adapter-v1"
STRESS_SCENARIO_VERSION: Final = "w03-c04-stress-v1"
MEASUREMENT_SCHEMA_VERSION: Final = "w03-c04-measurements-v1"

LIMITATION_MESSAGES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "C04_BASELINE_COMPARATOR_ONLY": (
            "The baseline candidate is a neutral comparator, not an operational recommendation."
        ),
        "C04_CAPACITY_PRESSURE_UNKNOWN_IN_C03_V1": (
            "C03 v1 does not establish allocatable capacity pressure."
        ),
        "C04_NO_FORMAL_RELEASE_INFERENCE": (
            "The modeled quality observations do not establish formal quality release."
        ),
        "C04_QUEUE_DELAY_NOT_CAPACITY_PROOF": (
            "A queue-delay proxy does not prove capacity pressure or root cause."
        ),
        "C04_SCENARIO_SCOPE_NOT_ORDER_TARGETED": (
            "Frozen W2 scenario selection is not guaranteed to target the current order."
        ),
        "C04_STRESS_PROBE_NOT_INTERVENTION_EFFICACY": (
            "The modeled stress probe is for human investigation and is not intervention efficacy."
        ),
        "C04_SUPPLIER_ASSOCIATION_NOT_ALLOCATION": (
            "Material association does not establish order-specific supplier allocation."
        ),
    }
)

_SIGNAL_GROUPS: Final = {
    InterventionFamily.SUPPLIER_INTERVENTION: (
        SignalType.MATERIAL_TIMING_RISK,
        SignalType.SUPPLIER_LATE_RECEIPT,
    ),
    InterventionFamily.QUALITY_INTERVENTION: (
        SignalType.QUALITY_DISPOSITION_UNKNOWN,
        SignalType.QUALITY_FAILURE,
        SignalType.REWORK_PRESENT,
    ),
    InterventionFamily.CAPACITY_INTERVENTION: (
        SignalType.CAPACITY_PRESSURE,
        SignalType.QUEUE_DELAY,
    ),
}

_REGISTRY_KEYS: Final = {
    InterventionFamily.NO_ACTION: "c04.no-action.v1",
    InterventionFamily.SUPPLIER_INTERVENTION: "c04.supplier-stress-probe.v1",
    InterventionFamily.QUALITY_INTERVENTION: "c04.quality-stress-probe.v1",
    InterventionFamily.CAPACITY_INTERVENTION: "c04.capacity-stress-probe.v1",
}

_PARAMETERS: Final = {
    InterventionFamily.NO_ACTION: (("mode", "BASELINE_IDENTITY", None),),
    InterventionFamily.SUPPLIER_INTERVENTION: (
        ("additional_delay_business_days_max", 8, "business_day"),
        ("additional_delay_business_days_min", 3, "business_day"),
        ("affected_critical_material_count", 5, "count"),
        ("affected_supplier_count", 2, "count"),
        ("late_probability_delta", Decimal("0.25"), None),
        ("seed_policy", "SHA256_CANDIDATE_ID_63BIT", None),
        ("window_policy", "FULL_CLOSED_DATASET_PERIOD", None),
    ),
    InterventionFamily.QUALITY_INTERVENTION: (
        ("affected_product_count", 2, "count"),
        ("affected_work_center_count", 1, "count"),
        ("failure_probability_multiplier", Decimal("2.2"), None),
        ("rework_duration_multiplier_max", Decimal("1.5"), None),
        ("rework_duration_multiplier_min", Decimal("1.2"), None),
        ("rework_probability_delta", Decimal("0.30"), None),
        ("seed_policy", "SHA256_CANDIDATE_ID_63BIT", None),
        ("window_policy", "FULL_CLOSED_DATASET_PERIOD", None),
    ),
    InterventionFamily.CAPACITY_INTERVENTION: (
        ("affected_work_center_count", 2, "count"),
        ("arrival_volume_multiplier", Decimal("1.5"), None),
        ("queue_time_multiplier", Decimal("1.7"), None),
        ("seed_policy", "SHA256_CANDIDATE_ID_63BIT", None),
        ("window_policy", "FULL_CLOSED_DATASET_PERIOD", None),
    ),
}

_BASE_REASONS: Final = {
    InterventionFamily.NO_ACTION: ("C04_BASELINE_COMPARATOR", "C04_REGISTRY_V1"),
    InterventionFamily.SUPPLIER_INTERVENTION: (
        "C04_REGISTRY_V1",
        "C04_STRESS_PROBE_NOT_ACTION_EFFECT",
        "C04_SUPPLIER_STRESS_PROBE",
    ),
    InterventionFamily.QUALITY_INTERVENTION: (
        "C04_QUALITY_STRESS_PROBE",
        "C04_REGISTRY_V1",
        "C04_STRESS_PROBE_NOT_ACTION_EFFECT",
    ),
    InterventionFamily.CAPACITY_INTERVENTION: (
        "C04_CAPACITY_STRESS_PROBE",
        "C04_REGISTRY_V1",
        "C04_STRESS_PROBE_NOT_ACTION_EFFECT",
    ),
}

_LIMITATION_CODES: Final = {
    InterventionFamily.NO_ACTION: ("C04_BASELINE_COMPARATOR_ONLY",),
    InterventionFamily.SUPPLIER_INTERVENTION: (
        "C04_SCENARIO_SCOPE_NOT_ORDER_TARGETED",
        "C04_STRESS_PROBE_NOT_INTERVENTION_EFFICACY",
        "C04_SUPPLIER_ASSOCIATION_NOT_ALLOCATION",
    ),
    InterventionFamily.QUALITY_INTERVENTION: (
        "C04_NO_FORMAL_RELEASE_INFERENCE",
        "C04_SCENARIO_SCOPE_NOT_ORDER_TARGETED",
        "C04_STRESS_PROBE_NOT_INTERVENTION_EFFICACY",
    ),
    InterventionFamily.CAPACITY_INTERVENTION: (
        "C04_CAPACITY_PRESSURE_UNKNOWN_IN_C03_V1",
        "C04_QUEUE_DELAY_NOT_CAPACITY_PROOF",
        "C04_SCENARIO_SCOPE_NOT_ORDER_TARGETED",
        "C04_STRESS_PROBE_NOT_INTERVENTION_EFFICACY",
    ),
}


def _provenance(
    input_ids: tuple[str, ...],
    evidence: tuple[object, ...],
    *,
    producer: str,
) -> ArtifactProvenance:
    return ArtifactProvenance(
        producer=producer,
        producer_version=REGISTRY_VERSION,
        input_artifact_ids=tuple(sorted(input_ids)),
        source_refs=source_refs_for(evidence),  # type: ignore[arg-type]
        contract_versions=(
            VersionRef(name="w03-c01", version="v1"),
            VersionRef(name="w03-c02", version="v1"),
            VersionRef(name="w03-c03", version="v1"),
            VersionRef(name="w03-c04-registry", version="v1"),
        ),
        implementation_sha=None,
    )


def build_candidate_set(
    bundle: EvidenceBundle,
    context: DecisionContext,
    signals: SignalBundle,
    diagnosis: DiagnosisRecord,
) -> CandidateSet:
    """Build all four frozen investigation families from canonical C03 inputs."""

    canonical = validate_c04_inputs(bundle, context, signals, diagnosis)
    by_type = {item.signal_type: item for item in canonical.signals.signals}
    candidates: list[InterventionCandidate] = []
    for family in InterventionFamily:
        if family is InterventionFamily.NO_ACTION:
            evidence_ids = canonical.diagnosis.supporting_evidence_ids
            active = False
        else:
            relevant = tuple(by_type[item] for item in _SIGNAL_GROUPS[family])
            evidence_ids = tuple(
                sorted({value for signal in relevant for value in signal.evidence_ids})
            )
            active = any(signal.state is SignalState.ACTIVE for signal in relevant)
        reason_codes = set(_BASE_REASONS[family])
        if family is not InterventionFamily.NO_ACTION:
            reason_codes.add(
                "C04_RELEVANT_SIGNAL_ACTIVE" if active else "C04_RELEVANCE_NOT_ESTABLISHED"
            )
        parameters = tuple(
            NamedValue(name=name, value=value, unit=unit)
            for name, value, unit in _PARAMETERS[family]
        )
        reasons = tuple(sorted(reason_codes))
        identity = {
            "run_id": context.run_id,
            "family": family,
            "registry_key": _REGISTRY_KEYS[family],
            "parameters": parameters,
            "supporting_evidence_ids": evidence_ids,
            "reason_codes": reasons,
        }
        selected = tuple(canonical.index.by_id[item] for item in evidence_ids)
        candidates.append(
            InterventionCandidate(
                candidate_id=derive_artifact_id(
                    "intervention-candidate", "intervention-candidate.v1", identity
                ),
                schema_version="intervention-candidate.v1",
                run_id=context.run_id,
                family=family,
                registry_key=_REGISTRY_KEYS[family],
                parameters=parameters,
                supporting_evidence_ids=evidence_ids,
                reason_codes=reasons,
                limitations=tuple(
                    Limitation(code=code, message=LIMITATION_MESSAGES[code])
                    for code in _LIMITATION_CODES[family]
                ),
                provenance=_provenance(
                    (
                        bundle.evidence_bundle_id,
                        context.context_id,
                        canonical.signals.signal_bundle_id,
                        canonical.diagnosis.diagnosis_id,
                    ),
                    selected,
                    producer="flowlens.decision.c04_registry",
                ),
            )
        )
    ordered = tuple(sorted(candidates, key=lambda item: item.candidate_id))
    identity = {
        "run_id": context.run_id,
        "snapshot_id": context.snapshot_id,
        "diagnosis_id": canonical.diagnosis.diagnosis_id,
        "candidate_ids": tuple(item.candidate_id for item in ordered),
    }
    return CandidateSet(
        candidate_set_id=derive_artifact_id("candidate-set", "candidate-set.v1", identity),
        schema_version="candidate-set.v1",
        run_id=context.run_id,
        snapshot_id=context.snapshot_id,
        diagnosis_id=canonical.diagnosis.diagnosis_id,
        candidates=ordered,
        provenance=_provenance(
            tuple(
                sorted(
                    (
                        bundle.evidence_bundle_id,
                        context.context_id,
                        canonical.signals.signal_bundle_id,
                        canonical.diagnosis.diagnosis_id,
                        *(item.candidate_id for item in ordered),
                    )
                )
            ),
            bundle.evidence,
            producer="flowlens.decision.c04_registry",
        ),
    )
