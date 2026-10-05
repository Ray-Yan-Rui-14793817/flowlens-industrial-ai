"""Fail-closed canonical input validation for W03-C04."""

from __future__ import annotations

from dataclasses import dataclass

from flowlens.decision.c03_validation import C03BuildError, EvidenceIndex, validate_c03_inputs
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import (
    CandidateSet,
    DecisionRun,
    DiagnosisRecord,
    EvidenceBundle,
    SignalBundle,
    StateSnapshot,
)
from flowlens.decision.diagnosis import build_diagnosis
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.decision.signals import build_signal_bundle


class C04BuildError(ValueError):
    """A deterministic fail-closed C04 contract or integrity error."""

    def __init__(self, code: str, state: str) -> None:
        self.code = code
        self.state = state
        super().__init__(f"{state}: {code}")


@dataclass(frozen=True, slots=True)
class CanonicalC04Inputs:
    index: EvidenceIndex
    signals: SignalBundle
    diagnosis: DiagnosisRecord


def validate_c04_inputs(
    bundle: EvidenceBundle,
    context: DecisionContext,
    signals: SignalBundle,
    diagnosis: DiagnosisRecord,
) -> CanonicalC04Inputs:
    """Rebuild C03 outputs and reject every noncanonical supplied artifact."""

    try:
        index = validate_c03_inputs(bundle, context)
        canonical_signals = build_signal_bundle(bundle, context)
        canonical_diagnosis = build_diagnosis(bundle, context, canonical_signals)
    except (C03BuildError, TypeError, ValueError) as error:
        raise C04BuildError("C04_NONCANONICAL_C03_INPUT", "BLOCKED_CONTRACT") from error
    if (
        not isinstance(signals, SignalBundle)
        or not isinstance(diagnosis, DiagnosisRecord)
        or canonical_json_bytes(signals) != canonical_json_bytes(canonical_signals)
        or canonical_json_bytes(diagnosis) != canonical_json_bytes(canonical_diagnosis)
    ):
        raise C04BuildError("C04_NONCANONICAL_C03_INPUT", "BLOCKED_CONTRACT")
    return CanonicalC04Inputs(index, canonical_signals, canonical_diagnosis)


def validate_run_snapshot(
    run: DecisionRun,
    snapshot: StateSnapshot,
    context: DecisionContext,
) -> None:
    if not isinstance(run, DecisionRun) or not isinstance(snapshot, StateSnapshot):
        raise C04BuildError("C04_SIMULATION_BINDING_MISMATCH", "BLOCKED_CONTRACT")
    if (
        run.run_id != snapshot.run_id
        or run.run_id != context.run_id
        or snapshot.snapshot_id != context.snapshot_id
        or run.order_id != snapshot.order_id
        or run.order_id != context.order_id
        or run.as_of_time != snapshot.as_of_time
        or run.as_of_time != context.as_of_time
        or run.dataset_version != snapshot.dataset_version
        or run.dataset_hash != snapshot.dataset_hash
        or snapshot.snapshot_hash != context.snapshot_hash
    ):
        raise C04BuildError("C04_SIMULATION_BINDING_MISMATCH", "BLOCKED_CONTRACT")


def validate_candidate_set(actual: CandidateSet, expected: CandidateSet) -> None:
    if not isinstance(actual, CandidateSet) or canonical_json_bytes(actual) != canonical_json_bytes(
        expected
    ):
        raise C04BuildError("C04_NONCANONICAL_CANDIDATE_SET", "BLOCKED_CONTRACT")
