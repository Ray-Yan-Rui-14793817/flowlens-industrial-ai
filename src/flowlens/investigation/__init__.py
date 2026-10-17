"""Pure immutable W04-C01 investigation contracts; no execution capability."""

from flowlens.decision.enums import TrustLevel
from flowlens.decision.serialization import (
    canonical_json_bytes,
    canonical_json_text,
    canonical_primitive,
    sha256_hex,
)
from flowlens.investigation.contracts import (
    ConflictRecord,
    EntityKey,
    EvidenceObservation,
    EvidenceQuerySpec,
    EvidenceSlice,
    FindingRecord,
    HumanInvestigationEvent,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
    InvestigationStep,
    InvestigationSummaryRecord,
    SummarySectionRecord,
    UncertaintyItem,
    UncertaintyRegister,
)
from flowlens.investigation.enums import (
    ConflictType,
    FindingStatus,
    HumanInvestigationOutcome,
    SummaryRendererMode,
    UncertaintyType,
)

__all__ = [
    "ConflictRecord", "ConflictType", "EntityKey", "EvidenceObservation",
    "EvidenceQuerySpec", "EvidenceSlice", "FindingRecord", "FindingStatus",
    "HumanInvestigationEvent", "HumanInvestigationOutcome", "InvestigationCase",
    "InvestigationPlan", "InvestigationQuestion", "InvestigationStep",
    "InvestigationSummaryRecord", "SummaryRendererMode", "SummarySectionRecord",
    "TrustLevel", "UncertaintyItem", "UncertaintyRegister", "UncertaintyType",
    "canonical_json_bytes", "canonical_json_text", "canonical_primitive", "sha256_hex",
]
