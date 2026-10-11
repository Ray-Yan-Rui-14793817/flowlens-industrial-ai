"""Frozen vocabulary and immutable receipt for protected investigation replay."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, NoReturn

from flowlens.decision.serialization import canonical_json_text
from flowlens.investigation.enums import SummaryRendererMode

C08_REPLAY_CONTRACT_VERSION: Final = "w04-c08-protected-replay-v1"
C08_REPLAY_RECEIPT_SCHEMA_VERSION: Final = "w04-c08-replay-receipt-v1"
C08_REPLAY_ID_PREFIX: Final = "ireplay_"

C08_LIMITATION_CODES: Final = (
    "C08_FROZEN_ARTIFACT_REPLAY_ONLY",
    "C08_HUMAN_NOTE_NON_EVIDENCE",
    "C08_NO_EVIDENCE_REFRESH",
    "C08_NO_HGT_OR_CAUSAL_EVALUATION",
    "C08_NO_OPERATIONAL_AUTHORITY",
    "C08_PRESENTATION_NOT_AUTHORITY",
)

C08_INVALID_REPLAY_CONTEXT: Final = "C08_INVALID_REPLAY_CONTEXT"
C08_CASE_REPLAY_MISMATCH: Final = "C08_CASE_REPLAY_MISMATCH"
C08_PLANNING_REPLAY_MISMATCH: Final = "C08_PLANNING_REPLAY_MISMATCH"
C08_QUERY_REPLAY_MISMATCH: Final = "C08_QUERY_REPLAY_MISMATCH"
C08_EVIDENCE_REPLAY_MISMATCH: Final = "C08_EVIDENCE_REPLAY_MISMATCH"
C08_FINDINGS_REPLAY_MISMATCH: Final = "C08_FINDINGS_REPLAY_MISMATCH"
C08_HUMAN_CHAIN_REPLAY_MISMATCH: Final = "C08_HUMAN_CHAIN_REPLAY_MISMATCH"
C08_SUMMARY_REPLAY_MISMATCH: Final = "C08_SUMMARY_REPLAY_MISMATCH"
C08_REPLAY_RECEIPT_MISMATCH: Final = "C08_REPLAY_RECEIPT_MISMATCH"

C08_ERROR_CODES: Final = frozenset(
    (
        C08_INVALID_REPLAY_CONTEXT,
        C08_CASE_REPLAY_MISMATCH,
        C08_PLANNING_REPLAY_MISMATCH,
        C08_QUERY_REPLAY_MISMATCH,
        C08_EVIDENCE_REPLAY_MISMATCH,
        C08_FINDINGS_REPLAY_MISMATCH,
        C08_HUMAN_CHAIN_REPLAY_MISMATCH,
        C08_SUMMARY_REPLAY_MISMATCH,
        C08_REPLAY_RECEIPT_MISMATCH,
    )
)


class C08ProtectedReplayError(ValueError):
    """Only a frozen public code; upstream diagnostics never cross this boundary."""

    def __init__(self, code: str) -> None:
        if code not in C08_ERROR_CODES:
            raise ValueError("unknown C08 error code")
        self.code = code
        super().__init__(code)


def fail(code: str) -> NoReturn:
    raise C08ProtectedReplayError(code) from None


@dataclass(frozen=True, slots=True, kw_only=True, init=False)
class InvestigationReplayReceipt:
    """Created only from a validated replay; callers cannot initialize derived claims."""

    schema_version: str = field(init=False)
    replay_contract_version: str = field(init=False)
    replay_id: str = field(init=False)
    replay_core_sha256: str = field(init=False)
    source_chain_sha256: str = field(init=False)
    packet_id: str = field(init=False)
    case_id: str = field(init=False)
    question_ids: tuple[str, ...] = field(init=False)
    plan_id: str = field(init=False)
    query_ids: tuple[str, ...] = field(init=False)
    evidence_slice_ids: tuple[str, ...] = field(init=False)
    finding_ids: tuple[str, ...] = field(init=False)
    conflict_ids: tuple[str, ...] = field(init=False)
    uncertainty_register_id: str = field(init=False)
    human_event_ids: tuple[str, ...] = field(init=False)
    authoritative_summary_id: str = field(init=False)
    authoritative_summary_content_hash: str = field(init=False)
    presented_summary_id: str = field(init=False)
    presented_summary_content_hash: str = field(init=False)
    presented_renderer_mode: SummaryRendererMode = field(init=False)
    limitation_codes: tuple[str, ...] = field(init=False)
    receipt_sha256: str = field(init=False)

    def __init__(self) -> None:
        fail(C08_REPLAY_RECEIPT_MISMATCH)

    def to_json(self) -> str:
        return canonical_json_text(self)
