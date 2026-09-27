"""Frozen W03-C06 policy and C01 schema-preservation tests."""

from dataclasses import fields

import pytest

from flowlens.decision.c06_policy import (
    C06_ERROR_CODES,
    C06_NONCANONICAL_C05_PACKET,
    HUMAN_DECISION_POLICY_VERSION,
    HUMAN_DECISION_PRODUCER,
    HUMAN_DECISION_STORE_VERSION,
    HUMAN_DECISION_WORKFLOW_VERSION,
    C06Error,
)
from flowlens.decision.contracts import HumanDecisionEvent
from flowlens.decision.enums import HumanDecisionType


def test_frozen_policy_versions_and_producer() -> None:
    assert HUMAN_DECISION_POLICY_VERSION == "w03-c06-human-v1"
    assert HUMAN_DECISION_STORE_VERSION == "w03-c06-store-v1"
    assert HUMAN_DECISION_WORKFLOW_VERSION == "w03-c06-workflow-v1"
    assert HUMAN_DECISION_PRODUCER == "flowlens.decision.c06_human"


def test_c06_error_codes_are_stable_sorted_and_unique() -> None:
    assert C06_ERROR_CODES == tuple(sorted(set(C06_ERROR_CODES)))
    assert {
        "C06_NONCANONICAL_C05_PACKET",
        "C06_PACKET_BINDING_MISMATCH",
        "C06_DECISION_TIME_BEFORE_RUN",
        "C06_REASON_CODE_UNKNOWN",
        "C06_REASON_CODE_OVERLAP",
        "C06_PREVIOUS_EVENT_MISMATCH",
        "C06_CHAIN_RUN_MISMATCH",
        "C06_CHAIN_PACKET_MISMATCH",
        "C06_CHAIN_TIME_REGRESSION",
        "C06_STORE_ROOT_INVALID",
        "C06_STORE_BUSY",
        "C06_STORE_DIRTY",
        "C06_STORE_CORRUPT",
        "C06_STORE_FORK",
        "C06_STORE_CYCLE",
        "C06_EVENT_ID_COLLISION",
        "C06_STORE_IO_FAILURE",
    } <= set(C06_ERROR_CODES)


def test_typed_error_exposes_code_and_state() -> None:
    error = C06Error(C06_NONCANONICAL_C05_PACKET)
    assert error.code == C06_NONCANONICAL_C05_PACKET
    assert error.state == "BLOCKED_CONTRACT"
    assert str(error) == "BLOCKED_CONTRACT: C06_NONCANONICAL_C05_PACKET"
    with pytest.raises(ValueError, match="unknown C06 error code"):
        C06Error("NOT_A_C06_CODE")


def test_c01_human_decision_enum_and_schema_are_unchanged() -> None:
    assert tuple(item.value for item in HumanDecisionType) == ("ACCEPT", "REJECT", "DEFER")
    assert tuple(field.name for field in fields(HumanDecisionEvent)) == (
        "decision_event_id",
        "schema_version",
        "run_id",
        "packet_id",
        "decision",
        "actor_id",
        "decided_at",
        "accepted_reason_codes",
        "rejected_reason_codes",
        "comment",
        "investigation_priority",
        "previous_event_id",
        "provenance",
    )
