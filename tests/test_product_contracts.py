"""C01 immutable values, exact schema, canonical identity and pinned semantic vectors."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from enum import StrEnum
from typing import Any, cast

import pytest

from flowlens.decision.serialization import canonical_json_bytes, derive_artifact_id
from flowlens.product import contracts as pc
from test_product_projection import _source, _view

GOLDEN: dict[str, tuple[str, int, str]] = {
    "baseline": (
        "fe30ab2c40cf2fc17ca65fbb2eb810a379ec2effee2166026650cce4e569e7a5",
        536785,
        "e217fe48521dbfd21fcfc15c616b35c569130ba00c9d7656537ce3627a810c11",
    ),
    "unknown": (
        "99c763b798abe7236d1588498be5266c43669556645f74290c91918ffa1af423",
        251233,
        "94e23d1a18068da8fd3b62a5486389749b6d65c3bdabe54c8339d9ba38016027",
    ),
    "conflict": (
        "00b502c5a5901699a543abe87bb2106b2a8d4c37bb49f480316eb759cbdc2d17",
        546865,
        "d898d4de68dd26d47f054503d73718c55ece96afe78310a601348ffc42037e70",
    ),
    "degraded-summary": (
        "58da9068512d8ec8533128a603812f8f6601099d34e91fcdb8d17f2c5d2cf71e",
        536805,
        "ea3ee764f0274211a8b9b93368e97dedf913ee0f5be7f84a7bd51cde0f017127",
    ),
    "decision-review": (
        "88b1993e9903c62941f893c37e83c66a22ebe2dbe74b61fc35aadd513030856b",
        538894,
        "33579535ec462cd791a73abe16543ef31c465b607f25908c976ca58aaeb59d73",
    ),
    "investigation-review": (
        "7dc3e62e734daac742fe7ed81c65d3356bb432d0765beadacacc03b01c1de660",
        537590,
        "ec8368059a9fd9e1b1f6324570b23525208c6805ae38753ea8ae01c9f51dcafe",
    ),
}
SCHEMA_SHA256 = "7276933e8c366c6fe10dcba33791979bacd6c50802cac665edcf28e0d51b5253"


@pytest.mark.parametrize(
    "shape",
    [
        "baseline",
        "unknown",
        "conflict",
        "degraded-summary",
        "decision-review",
        "investigation-review",
    ],
)
def test_pinned_canonical_product_golden_vectors(shape: str) -> None:
    view = _view(shape)
    raw = view.to_json().encode()
    assert (view.view_hash, len(raw), hashlib.sha256(raw).hexdigest()) == GOLDEN[shape]
    assert view.view_id == "pcv_" + view.view_hash
    semantic = json.loads(raw)
    del semantic["view_id"], semantic["view_hash"]
    independent = json.dumps(
        semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    assert hashlib.sha256(independent).hexdigest() == view.view_hash


def test_exact_public_schema_and_fresh_copy() -> None:
    schema = pc.product_schema()
    wire = pc.product_schema_json()
    assert json.loads(wire) == schema
    assert hashlib.sha256(wire.encode()).hexdigest() == SCHEMA_SHA256
    assert schema["$id"] == "flowlens-product-case-view.v1"
    definitions = cast(dict[str, Any], schema["$defs"])
    top = definitions["ProductCaseView"]
    assert set(top["properties"]) == {
        "schema_version",
        "view_id",
        "view_hash",
        "identity",
        "decision",
        "investigation",
        "capability_boundary",
    }
    assert top["properties"]["schema_version"]["enum"] == ["flowlens-product-case-view.v1"]
    for model in (
        pc.ProductCaseIdentity,
        pc.ProductEvidenceView,
        pc.ProductSignalView,
        pc.ProductDiagnosisClaimView,
        pc.ProductCandidateView,
        pc.ProductSimulationView,
        pc.ProductRecommendationView,
        pc.ProductExplanationView,
        pc.DecisionHumanReviewView,
        pc.ProductFindingView,
        pc.ProductConflictView,
        pc.ProductUncertaintyView,
        pc.ProductSummarySectionView,
        pc.InvestigationHumanReviewView,
        pc.ProductDecisionView,
        pc.ProductInvestigationView,
        pc.ProductCapabilityBoundary,
    ):
        entry = definitions[model.__name__]
        assert set(entry["properties"]) == {f.name for f in fields(model)}
        assert set(entry["required"]) == set(entry["properties"])
        assert entry["additionalProperties"] is False
    schema.clear()
    assert pc.product_schema_json() == wire


@pytest.mark.parametrize(
    "name,field",
    [
        ("ProductEvidenceView", "trust_level"),
        ("ProductEvidenceView", "freshness_status"),
        ("ProductSignalView", "signal_type"),
        ("ProductSignalView", "state"),
        ("ProductRecommendationView", "disposition"),
        ("ProductSimulationView", "status"),
        ("ProductExplanationView", "mode"),
        ("DecisionHumanReviewView", "decision"),
        ("ProductFindingView", "status"),
        ("ProductConflictView", "conflict_type"),
        ("ProductUncertaintyView", "uncertainty_type"),
        ("InvestigationHumanReviewView", "outcome"),
        ("ProductSummarySectionView", "renderer_mode"),
    ],
)
def test_schema_preserves_closed_source_enum_values(name: str, field: str) -> None:
    from typing import get_type_hints

    model = getattr(pc, name)
    enum = cast(type[StrEnum], get_type_hints(model)[field])
    schema = cast(dict[str, Any], pc.product_schema()["$defs"])
    assert schema[name]["properties"][field] == {
        "type": "string",
        "enum": [entry.value for entry in enum],
    }


@pytest.mark.parametrize(
    "name",
    [
        "schema_version",
        "view_id",
        "view_hash",
        "identity",
        "decision",
        "investigation",
        "capability_boundary",
    ],
)
def test_public_case_is_frozen_and_slotted(name: str) -> None:
    view = _view()
    assert not hasattr(view, "__dict__")
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        setattr(view, name, None)


@pytest.mark.parametrize(
    "name", ["evidence", "signals", "diagnosis", "candidates", "simulations", "recommendation"]
)
def test_nested_product_envelopes_are_frozen(name: str) -> None:
    value = getattr(_view().decision, name)
    assert not hasattr(value, "__dict__")
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        setattr(value, fields(value)[0].name, None)


@pytest.mark.parametrize("value", [1.5, float("nan"), float("inf"), [], {}, set(), bytearray()])
def test_mutable_and_float_values_are_rejected(value: Any) -> None:
    evidence = _view().decision.evidence.evidence[0]
    with pytest.raises(pc.ProductError):
        replace(evidence, value=value)


def test_naive_time_and_wrong_typed_identity_are_rejected() -> None:
    identity = _view().identity
    for value in (datetime(2026, 1, 1), "2026-01-01", 123, False):
        with pytest.raises(pc.ProductError):
            replace(identity, as_of_time=cast(Any, value))
    with pytest.raises(pc.ProductError):
        replace(identity, order_id=cast(Any, 12))


def test_subclasses_cannot_add_mutable_semantic_state() -> None:
    class MutableSignal(pc.ProductSignalView):
        pass

    original = _view().decision.signals.signals[0]
    kwargs = {f.name: getattr(original, f.name) for f in fields(original)}
    with pytest.raises(pc.ProductError):
        MutableSignal(**kwargs)


@pytest.mark.parametrize(
    "value,expected",
    [
        (Decimal("12.3400"), "12.34"),
        (Decimal("-0.000"), "0"),
        (Decimal("1E+24"), "1000000000000000000000000"),
        (Decimal("0.00000001"), "0.00000001"),
    ],
)
def test_decimal_value_uses_exact_canonical_product_json(value: Decimal, expected: str) -> None:
    original = _source().packet.evidence.evidence[0]
    kwargs = {f.name: getattr(original, f.name) for f in fields(original)}
    kwargs["value"] = value
    identity = {
        key: item
        for key, item in kwargs.items()
        if key not in {"evidence_id", "schema_version", "limitations", "provenance"}
    }
    kwargs["evidence_id"] = derive_artifact_id("evidence", original.schema_version, identity)
    projected = pc.ProductEvidenceView(**kwargs)
    assert json.loads(projected.to_json())["value"] == expected
    assert "evidence_id" in json.loads(projected.to_json())


def test_time_is_exact_utc_and_equivalent_offsets_do_not_change_bytes() -> None:
    identity = _view().identity
    utc = datetime(2026, 1, 2, 3, 4, 5, 123456, tzinfo=UTC)
    offset = utc.astimezone(timezone(timedelta(hours=8)))
    first, second = replace(identity, as_of_time=utc), replace(identity, as_of_time=offset)
    assert first.to_json() == second.to_json()
    assert json.loads(first.to_json())["as_of_time"] == "2026-01-02T03:04:05.123456Z"


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")])
def test_nonfinite_decimal_is_rejected(value: Decimal) -> None:
    with pytest.raises(pc.ProductError):
        replace(_view().decision.evidence.evidence[0], value=value)


@pytest.mark.parametrize("code", list(pc.ProductErrorCode))
def test_public_error_codes_do_not_carry_arbitrary_details(code: pc.ProductErrorCode) -> None:
    error = pc.ProductError(code)
    assert str(error) == code.value and error.args == (code.value,)
    assert error.code is code
    secret = "postgresql://user:SECRET@localhost/db SQL stack C:/private HGT provider"
    safe = pc.ProductError(cast(Any, secret))
    assert str(safe) == "INTERNAL_ERROR" and secret not in repr(safe)


@pytest.mark.parametrize(
    "name,value",
    [
        ("mode", "LIVE"),
        ("human_authority_required", False),
        ("operational_write", "ALLOWED"),
        ("runtime_hgt", "ALLOWED"),
        ("llm_decision_authority", "DECIDE"),
        ("llm_tool_authority", "EXECUTE"),
        ("recommendation_execution", "ALLOWED"),
    ],
)
def test_capability_boundary_cannot_be_relaxed(name: str, value: Any) -> None:
    with pytest.raises(pc.ProductError):
        pc.ProductCapabilityBoundary(**{name: value})


def test_schema_datetime_pattern_matches_wire_utc_only() -> None:
    schema = cast(dict[str, Any], pc.product_schema()["$defs"])
    pattern = schema["ProductCaseIdentity"]["properties"]["as_of_time"]["pattern"]
    assert re.fullmatch(pattern, "2026-01-02T03:04:05.123456Z")
    assert not re.fullmatch(pattern, "2026-01-02T11:04:05.123456+08:00")


def test_view_hash_changes_for_distinct_semantic_worlds() -> None:
    values = [_view(shape) for shape in GOLDEN]
    assert len({v.view_hash for v in values}) == 6
    assert all(pc.PRODUCT_SCHEMA_VERSION == v.schema_version for v in values)
    assert all(canonical_json_bytes(v).decode() == v.to_json() for v in values)
