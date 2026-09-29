"""W03-C08 bounded explanation orchestration and C01 artifact construction."""

from __future__ import annotations

import json

from flowlens.decision.c03_validation import source_refs_for
from flowlens.decision.c08_context import ExplanationContextV1, build_explanation_context
from flowlens.decision.c08_policy import (
    BASE_LIMITATION_CODES,
    BASE_REASON_CODES,
    EXPLAINER_VERSION,
    HUMAN_REVIEW_BOUNDARY,
    LIMITATION_MESSAGES,
    PROMPT_SHA256,
    PROMPT_VERSION,
    PROVIDER_POLICY_VERSION,
    REQUESTED_MODEL,
    RUNTIME_SYSTEM_PROMPT,
    C08ExplainerMode,
    provider_output_schema,
)
from flowlens.decision.c08_provider import (
    C08ProviderError,
    ExplanationProvider,
    OpenAIExplanationProvider,
    ProviderRequest,
)
from flowlens.decision.c08_template import render_deterministic_template
from flowlens.decision.c08_validation import (
    C08BuildError,
    ValidatedProviderOutput,
    assert_packet_unchanged,
    validate_decision_packet,
    validate_provider_output,
)
from flowlens.decision.contracts import DecisionPacket, ExplanationRecord
from flowlens.decision.enums import ExplanationMode
from flowlens.decision.primitives import (
    ArtifactProvenance,
    ExplanationSection,
    Limitation,
    VersionRef,
)
from flowlens.decision.serialization import canonical_json_text, derive_artifact_id


def _request(context: ExplanationContextV1) -> ProviderRequest:
    return ProviderRequest(
        system_prompt=RUNTIME_SYSTEM_PROMPT,
        context_json=canonical_json_text(context),
        output_schema_json=json.dumps(
            provider_output_schema(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
    )


def _llm_sections(output: ValidatedProviderOutput) -> tuple[ExplanationSection, ...]:
    return (
        *(
            ExplanationSection(section_key=item.section_key, text=item.text)
            for item in output.sections
        ),
        ExplanationSection(
            section_key="human_review_boundary",
            text=HUMAN_REVIEW_BOUNDARY,
        ),
    )


def _c08_limitations(mode: ExplanationMode) -> tuple[Limitation, ...]:
    codes = set(BASE_LIMITATION_CODES)
    if mode is ExplanationMode.BOUNDED_LLM:
        codes.add("C08_LLM_SEMANTIC_NOT_BYTE_DETERMINISTIC")
    elif mode is ExplanationMode.DEGRADED_TEMPLATE:
        codes.add("C08_LLM_FALLBACK_USED")
    return tuple(Limitation(code=code, message=LIMITATION_MESSAGES[code]) for code in sorted(codes))


def _system_reason_codes(
    mode: ExplanationMode,
    *,
    schema_repair_used: bool,
) -> set[str]:
    codes = set(BASE_REASON_CODES)
    if mode is ExplanationMode.DETERMINISTIC_TEMPLATE:
        codes.add("C08_DETERMINISTIC_TEMPLATE")
    elif mode is ExplanationMode.DEGRADED_TEMPLATE:
        codes.add("C08_EXPLANATION_DEGRADED")
    if schema_repair_used:
        codes.add("C08_SCHEMA_REPAIR_USED")
    return codes


def _build_record(
    packet: DecisionPacket,
    *,
    mode: ExplanationMode,
    sections: tuple[ExplanationSection, ...],
    referenced_evidence_ids: tuple[str, ...],
    referenced_reason_codes: tuple[str, ...],
    provider_used: bool,
    resolved_model: str | None,
    schema_repair_used: bool,
) -> ExplanationRecord:
    reason_codes = tuple(
        sorted(
            {
                *referenced_reason_codes,
                *_system_reason_codes(mode, schema_repair_used=schema_repair_used),
            }
        )
    )
    limitations = tuple(
        sorted(
            {*packet.limitations, *_c08_limitations(mode)},
            key=lambda item: (item.code, item.message),
        )
    )
    evidence_ids = tuple(sorted(set(referenced_evidence_ids)))
    evidence_by_id = {item.evidence_id: item for item in packet.evidence.evidence}
    source_refs = source_refs_for(tuple(evidence_by_id[item] for item in evidence_ids))
    identity = {
        "run_id": packet.run.run_id,
        "packet_id": packet.packet_id,
        "mode": mode,
        "explainer_version": EXPLAINER_VERSION,
        "sections": sections,
        "referenced_evidence_ids": evidence_ids,
        "reason_codes": reason_codes,
        "limitations": limitations,
    }
    provider_value = "openai" if provider_used else "none"
    requested_model = REQUESTED_MODEL if provider_used else "none"
    contract_versions = tuple(
        sorted(
            (
                VersionRef(name="w03-c01", version="v1"),
                VersionRef(name="w03-c05-packet", version="v1"),
                VersionRef(name="w03-c08", version="v1"),
                VersionRef(name="w03-c08-context", version="v1"),
                VersionRef(name="w03-c08-output", version="v1"),
                VersionRef(
                    name="w03-c08-prompt",
                    version=(
                        f"{PROMPT_VERSION.removeprefix('w03-c08-runtime-prompt-')}:{PROMPT_SHA256}"
                    ),
                ),
                VersionRef(name="w03-c08-provider", version=provider_value),
                VersionRef(name="w03-c08-provider-policy", version=PROVIDER_POLICY_VERSION),
                VersionRef(name="w03-c08-reasoning-effort", version="none"),
                VersionRef(name="w03-c08-requested-model", version=requested_model),
                VersionRef(name="w03-c08-resolved-model", version=resolved_model or "none"),
                VersionRef(name="w03-c08-temperature", version="omitted"),
            ),
            key=lambda item: (item.name, item.version),
        )
    )
    return ExplanationRecord(
        explanation_id=derive_artifact_id("explanation-record", "explanation-record.v1", identity),
        schema_version="explanation-record.v1",
        run_id=packet.run.run_id,
        packet_id=packet.packet_id,
        mode=mode,
        explainer_version=EXPLAINER_VERSION,
        sections=sections,
        referenced_evidence_ids=evidence_ids,
        reason_codes=reason_codes,
        limitations=limitations,
        provenance=ArtifactProvenance(
            producer="flowlens.decision.c08_explanation",
            producer_version=EXPLAINER_VERSION,
            input_artifact_ids=(packet.packet_id,),
            source_refs=source_refs,
            contract_versions=contract_versions,
            implementation_sha=None,
        ),
    )


def _template_record(
    packet: DecisionPacket,
    context: ExplanationContextV1,
    *,
    degraded: bool,
    provider_used: bool,
    resolved_model: str | None,
) -> ExplanationRecord:
    mode = ExplanationMode.DEGRADED_TEMPLATE if degraded else ExplanationMode.DETERMINISTIC_TEMPLATE
    return _build_record(
        packet,
        mode=mode,
        sections=render_deterministic_template(context),
        referenced_evidence_ids=context.allowed_evidence_ids,
        referenced_reason_codes=context.allowed_reason_codes,
        provider_used=provider_used,
        resolved_model=resolved_model,
        schema_repair_used=False,
    )


def explain_decision_packet(
    packet: DecisionPacket,
    *,
    provider: ExplanationProvider | None = None,
    mode: C08ExplainerMode = "template",
) -> ExplanationRecord:
    """Explain one immutable packet without adding decision authority."""

    if mode not in ("template", "openai"):
        raise C08BuildError("C08_EXPLAINER_MODE_INVALID", "BLOCKED_CONTRACT")
    before = validate_decision_packet(packet)
    context = build_explanation_context(packet)

    if mode == "template":
        result = _template_record(
            packet,
            context,
            degraded=False,
            provider_used=False,
            resolved_model=None,
        )
        assert_packet_unchanged(packet, before)
        return result

    selected_provider = provider or OpenAIExplanationProvider.from_environment()
    if selected_provider is None:
        result = _template_record(
            packet,
            context,
            degraded=False,
            provider_used=False,
            resolved_model=None,
        )
        assert_packet_unchanged(packet, before)
        return result

    request = _request(context)
    resolved_model: str | None = None
    try:
        first = selected_provider.generate(request)
    except C08ProviderError:
        result = _template_record(
            packet,
            context,
            degraded=True,
            provider_used=True,
            resolved_model=resolved_model,
        )
        assert_packet_unchanged(packet, before)
        return result
    resolved_model = first.resolved_model

    schema_repair_used = False
    try:
        output = validate_provider_output(first.output_text, context)
    except C08BuildError as error:
        if not error.repairable_schema:
            result = _template_record(
                packet,
                context,
                degraded=True,
                provider_used=True,
                resolved_model=resolved_model,
            )
            assert_packet_unchanged(packet, before)
            return result
        schema_repair_used = True
        try:
            second = selected_provider.generate(request)
        except C08ProviderError:
            result = _template_record(
                packet,
                context,
                degraded=True,
                provider_used=True,
                resolved_model=resolved_model,
            )
            assert_packet_unchanged(packet, before)
            return result
        resolved_model = second.resolved_model or resolved_model
        try:
            output = validate_provider_output(second.output_text, context)
        except C08BuildError:
            result = _template_record(
                packet,
                context,
                degraded=True,
                provider_used=True,
                resolved_model=resolved_model,
            )
            assert_packet_unchanged(packet, before)
            return result

    referenced_evidence = tuple(
        sorted({item for section in output.sections for item in section.evidence_ids})
    )
    referenced_reasons = tuple(
        sorted({item for section in output.sections for item in section.reason_codes})
    )
    result = _build_record(
        packet,
        mode=ExplanationMode.BOUNDED_LLM,
        sections=_llm_sections(output),
        referenced_evidence_ids=referenced_evidence,
        referenced_reason_codes=referenced_reasons,
        provider_used=True,
        resolved_model=resolved_model,
        schema_repair_used=schema_repair_used,
    )
    assert_packet_unchanged(packet, before)
    return result
