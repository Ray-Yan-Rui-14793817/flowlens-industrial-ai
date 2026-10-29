# C01 product surface contract

PRODUCT_SCHEMA_VERSION = flowlens-product-case-view.v1
PRODUCT_MODE = OFFLINE / SHADOW / HUMAN-IN-THE-LOOP

ProductCaseView fields: schema_version, view_id, view_hash, identity, decision,
investigation, capability_boundary. ProductCaseIdentity preserves order_id,
as_of_time, dataset_version, dataset_hash, run_id, snapshot_id, snapshot_hash,
packet_id, case_id, plan_id, summary_id and source packet hash.
product_schema() describes all exact field names/types/enums without dependencies;
product_schema_json() is its canonical machine-readable encoding.

Public product value concepts mirror their exact source envelopes with original
field names, IDs, enum types, provenance, uncertainty and limitations:
ProductEvidenceView, ProductSignalView, ProductDiagnosisClaimView,
ProductCandidateView, ProductSimulationView, ProductRecommendationView,
ProductExplanationView, DecisionHumanReviewView, ProductFindingView,
ProductConflictView, ProductUncertaintyView, ProductSummarySectionView and
InvestigationHumanReviewView. Supporting product bundle/diagnosis/register/summary
views preserve complete source members. ProductDecisionView mirrors the packet
and adds optional explanation plus ordered decision Human reviews.
ProductInvestigationView groups explicit case/questions/plan/queries/slices,
findings/conflicts/uncertainty, investigation Human reviews and summary.
DecisionHumanReviewView adds fixed HUMAN_NOTE_NON_EVIDENCE classification to
the W03 comment. W04 note_class is retained. No generic Human review enum.

ProductSourceBundle accepts only DecisionPacket, optional ExplanationRecord,
tuple of HumanDecisionEvent, InvestigationCase, tuple of InvestigationQuestion,
InvestigationPlan, tuples of EvidenceQuerySpec/EvidenceSlice/FindingRecord/
ConflictRecord, UncertaintyRegister, tuple of HumanInvestigationEvent and
InvestigationSummaryRecord. Exact immutable types and original nested identities
are revalidated. Reuse unchanged W03 packet/Human and W04 case/planning/evidence/
finding/Human/summary validators. Bind packet/run/snapshot, order/as-of,
case packet hash, all question/query/slice/finding/conflict/uncertainty references,
both event chains and exact summary references. No missing artifact is fetched
or invented; W04 summary admission retains its nonempty Human-chain requirement.

Preserve exact TrustLevel/FreshnessStatus/SignalType/SignalState/
RecommendationDisposition/SimulationStatus/ExplanationMode/HumanDecisionType/
FindingStatus/ConflictType/UncertaintyType/HumanInvestigationOutcome/
SummaryRendererMode. Source tuple order is unchanged, especially candidate
order and append chains. No new probability, score, root cause, evidence,
candidate, reason, resolved conflict, promoted trust, certainty or authority.
UNKNOWN stays UNKNOWN. No HGT/evaluation truth or operational action.

Frozen models contain exact immutable typed values/tuples; reject mutable
containers, subclasses with added state, floats, nonfinite Decimal and naive time.
Unchanged W03 canonical primitives: aware datetime to UTC with six microsecond
digits and Z; Decimal to exact non-exponent string with insignificant fractional
zeros removed and negative zero normalized; enums to exact values, tuple order
retained. UTF-8 JSON, lexical keys, no escaping Unicode or separator whitespace.
Hash all semantic ProductCaseView fields except view_id/view_hash:
view_hash = SHA256(canonical semantic payload); view_id = pcv_ + view_hash.
W03 serialization/prefix registry stay frozen. Pin six canonical hash/byte vectors:
baseline, UNKNOWN, conflict, degraded summary, decision review, investigation review.

ProductCapabilityBoundary is fixed: mode OFFLINE_SHADOW; human_authority_required
true; operational_write/runtime_hgt/recommendation_execution FORBIDDEN;
llm_decision_authority/llm_tool_authority NONE. No I/O, DB, file/network/provider,
environment/random/wall-clock/HGT capability. ProductError exposes only bounded
INVALID_PRODUCT_SOURCE, SOURCE_IDENTITY_MISMATCH, SOURCE_SCOPE_MISMATCH,
UNSUPPORTED_PRODUCT_STATE, INTERNAL_ERROR; never arbitrary exception text,
credentials, SQL, stack traces, filesystem/provider secrets or HGT.
HTTP status mapping and UI belong to later authorized checkpoints.
