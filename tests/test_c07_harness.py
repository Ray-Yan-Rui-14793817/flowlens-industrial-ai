"""Adversarial H1-H38 detection, enforcement, and evidence for W03-C07."""

from __future__ import annotations

import ast
import hashlib
import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path
from types import MappingProxyType
from typing import cast

import pytest

from flowlens.data.generation import GeneratedDataset
from flowlens.data.models import DatasetVersion, SalesOrder
from flowlens.data.scenarios.ground_truth import HiddenGroundTruth
from flowlens.data.scenarios.transformer import ScenarioResult
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.enums import RecommendationDisposition, SignalState, SignalType
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.evaluation import C07EvaluationError, evaluate_recommendation
from flowlens.evaluation.c07_replay import dataset_order_ids, derive_affected_order_ids
from test_c05_policy import unsafe_replace
from test_c07_replay import (
    ReplayCase,
    adversarial_packet_fixture,
    packet_from_dataset,
    replay_case,
)

ROOT = Path(__file__).resolve().parents[1]
EVALUATION_SOURCE = ROOT / "src" / "flowlens" / "evaluation"

H1_H38_EVIDENCE = {
    "H1": "test_h1_h5_and_h21_packet_attacks_fail_closed",
    "H2": "test_h1_h5_and_h21_packet_attacks_fail_closed",
    "H3": "test_h1_h5_and_h21_packet_attacks_fail_closed",
    "H4": "test_h1_h5_and_h21_packet_attacks_fail_closed",
    "H5": "test_h1_h5_and_h21_packet_attacks_fail_closed",
    "H6": "test_h6_mutable_row_stale_hash_fails_closed",
    "H7": "test_h7_h8_baseline_metadata_attacks_fail_closed",
    "H8": "test_h7_h8_baseline_metadata_attacks_fail_closed",
    "H9": "test_h9_h11_hgt_identity_attacks_fail_closed",
    "H10": "test_h9_h11_hgt_identity_attacks_fail_closed",
    "H11": "test_h9_h11_hgt_identity_attacks_fail_closed",
    "H12": "test_h12_missing_affected_entity_fails_closed",
    "H13": "test_h13_effectful_packet_for_unaffected_order_fails_closed",
    "H14": "test_h14_h17_baseline_pair_attacks_fail_closed",
    "H15": "test_h14_h17_baseline_pair_attacks_fail_closed",
    "H16": "test_h14_h17_baseline_pair_attacks_fail_closed",
    "H17": "test_h14_h17_baseline_pair_attacks_fail_closed",
    "H18": "test_missing_expected_signal_direction_is_descriptively_false",
    "H19": "test_missing_expected_signal_direction_is_descriptively_false",
    "H20": "test_missing_expected_signal_direction_is_descriptively_false",
    "H21": "test_h21_capacity_pressure_promotion_fails_closed",
    "H22": "test_capacity_arrival_only_is_not_retroactively_observable",
    "H23": "test_new_non_expected_active_family_is_a_false_positive",
    "H24": "test_neutral_new_family_causes_false_escalation_and_semantic_drift",
    "H25": "test_neutral_new_family_causes_false_escalation_and_semantic_drift",
    "H26": "test_output_envelope_rejects_metric_reason_and_limitation_drift",
    "H27": "test_output_envelope_rejects_metric_reason_and_limitation_drift",
    "H28": "test_output_envelope_rejects_metric_reason_and_limitation_drift",
    "H29": "test_same_process_replay_is_byte_identical_and_non_mutating",
    "H30": "test_h30_fresh_process_replay_is_hash_seed_independent",
    "H31": "test_h31_fresh_runtime_imports_do_not_reach_evaluation_or_hgt",
    "H32": "test_h32_evaluation_is_not_a_decision_packet_field",
    "H33": "test_same_process_replay_is_byte_identical_and_non_mutating",
    "H34": "test_same_process_replay_is_byte_identical_and_non_mutating",
    "H35": "test_h35_h38_source_capability_audit",
    "H36": "test_h35_h38_source_capability_audit",
    "H37": "test_h35_h38_source_capability_audit",
    "H38": "test_h35_h38_source_capability_audit",
}


def _evaluate(packet: DecisionPacket, kind: str = "supplier") -> None:
    case = replay_case(kind)
    evaluate_recommendation(
        packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )


def _packet_attack(packet: DecisionPacket, attack: str) -> DecisionPacket:
    if attack == "H1":
        provenance = unsafe_replace(packet.provenance, producer="forged.packet")
        return unsafe_replace(packet, provenance=provenance)
    if attack == "H2":
        provenance = unsafe_replace(
            packet.recommendation.provenance,
            producer="forged.recommendation",
        )
        recommendation = unsafe_replace(packet.recommendation, provenance=provenance)
        return unsafe_replace(packet, recommendation=recommendation)
    if attack == "H3":
        recommendation = unsafe_replace(
            packet.recommendation,
            disposition=RecommendationDisposition.CANDIDATE_RECOMMENDED,
        )
        return unsafe_replace(packet, recommendation=recommendation)
    if attack == "H4":
        run = unsafe_replace(packet.run, dataset_version="dsv_forged")
        return unsafe_replace(packet, run=run)
    if attack == "H5":
        run = unsafe_replace(packet.run, dataset_hash="0" * 64)
        return unsafe_replace(packet, run=run)
    if attack == "H21":
        signal = next(
            item
            for item in packet.signals.signals
            if item.signal_type is SignalType.CAPACITY_PRESSURE
        )
        forged = unsafe_replace(signal, state=SignalState.ACTIVE)
        signals = unsafe_replace(
            packet.signals,
            signals=tuple(
                forged if item is signal else item for item in packet.signals.signals
            ),
        )
        return unsafe_replace(packet, signals=signals)
    raise AssertionError(f"unknown attack {attack}")


@pytest.mark.parametrize("attack", ("H1", "H2", "H3", "H4", "H5"))
def test_h1_h5_and_h21_packet_attacks_fail_closed(attack: str) -> None:
    case = replay_case("supplier")
    with pytest.raises(C07EvaluationError):
        _evaluate(_packet_attack(case.scenario_packet, attack))


def test_h21_capacity_pressure_promotion_fails_closed() -> None:
    case = replay_case("capacity_queue")
    with pytest.raises(C07EvaluationError):
        evaluate_recommendation(
            _packet_attack(case.scenario_packet, "H21"),
            case.scenario,
            baseline_dataset=case.baseline,
            baseline_packet=case.baseline_packet,
        )


def test_h6_mutable_row_stale_hash_fails_closed() -> None:
    case = replay_case("supplier")
    row = cast(SalesOrder, case.scenario.dataset.rows_for("fact_sales_order")[0])
    original = row.priority
    row.priority = "HIGH" if original != "HIGH" else "NORMAL"
    try:
        with pytest.raises(C07EvaluationError, match="C07_SCENARIO_DATASET_HASH_MISMATCH"):
            _evaluate(case.scenario_packet)
    finally:
        row.priority = original


def _metadata_variant(
    dataset: GeneratedDataset,
    *,
    dataset_version_id: str | None = None,
    content_hash: str | None = None,
) -> GeneratedDataset:
    old = dataset.dataset_version
    version = DatasetVersion(
        dataset_version_id=(
            old.dataset_version_id if dataset_version_id is None else dataset_version_id
        ),
        seed=old.seed,
        generator_version=old.generator_version,
        profile=old.profile,
        period_start=old.period_start,
        period_end=old.period_end,
        generated_at=old.generated_at,
        content_hash=old.content_hash if content_hash is None else content_hash,
        row_count_total=old.row_count_total,
    )
    return GeneratedDataset(version, MappingProxyType(dict(dataset.rows_by_table)))


@pytest.mark.parametrize("attack", ("H7", "H8"))
def test_h7_h8_baseline_metadata_attacks_fail_closed(attack: str) -> None:
    case = replay_case("supplier")
    attacked = (
        _metadata_variant(case.baseline, dataset_version_id="dsv_forged")
        if attack == "H7"
        else _metadata_variant(case.baseline, content_hash="0" * 64)
    )
    with pytest.raises(C07EvaluationError):
        evaluate_recommendation(
            case.scenario_packet,
            case.scenario,
            baseline_dataset=attacked,
            baseline_packet=case.baseline_packet,
        )


def _scenario_with_hgt(case_kind: str, attack: str) -> tuple[ReplayCase, ScenarioResult]:
    case = replay_case(case_kind)
    ground_truth = case.scenario.ground_truth
    if attack == "H9":
        forged = unsafe_replace(
            ground_truth,
            scenario_dataset_version_id="dsv_00000000000000000000000000000000",
        )
    elif attack == "H10":
        forged = unsafe_replace(ground_truth, baseline_dataset_version_id="dsv_forged")
    elif attack == "H11_HASH":
        forged = unsafe_replace(ground_truth, hgt_hash="0" * 64)
    elif attack == "H11_ID":
        forged = unsafe_replace(ground_truth, hgt_id="hgt_00000000000000000000000000000000")
    else:
        raise AssertionError(attack)
    return case, unsafe_replace(case.scenario, ground_truth=forged)


@pytest.mark.parametrize("attack", ("H9", "H10", "H11_HASH", "H11_ID"))
def test_h9_h11_hgt_identity_attacks_fail_closed(attack: str) -> None:
    case_object, scenario = _scenario_with_hgt("supplier", attack)
    case = case_object
    with pytest.raises(C07EvaluationError):
        evaluate_recommendation(
            case.scenario_packet,
            scenario,
            baseline_dataset=case.baseline,
            baseline_packet=case.baseline_packet,
        )


def _rebuild_hgt(
    original: HiddenGroundTruth,
    affected: dict[str, tuple[str, ...]],
) -> HiddenGroundTruth:
    return HiddenGroundTruth(
        schema_version=original.schema_version,
        scenario_id=original.scenario_id,
        scenario_type=original.scenario_type,
        scenario_version=original.scenario_version,
        scenario_seed=original.scenario_seed,
        baseline_dataset_version_id=original.baseline_dataset_version_id,
        scenario_dataset_version_id=original.scenario_dataset_version_id,
        window_start=original.window_start,
        window_end=original.window_end,
        parameters=original.parameters,
        target_entity_ids=original.target_entity_ids,
        affected_entities_by_table=affected,
        causal_chain=original.causal_chain,
    )


def test_h12_missing_affected_entity_fails_closed() -> None:
    case = replay_case("supplier")
    affected = dict(case.scenario.ground_truth.affected_entities_by_table)
    affected["fact_sales_order"] = (*affected.get("fact_sales_order", ()), "so_missing")
    ground_truth = _rebuild_hgt(case.scenario.ground_truth, affected)
    scenario = ScenarioResult(case.scenario.dataset, ground_truth)
    with pytest.raises(C07EvaluationError, match="C07_AFFECTED_ORDER_BINDING_MISMATCH"):
        evaluate_recommendation(
            case.scenario_packet,
            scenario,
            baseline_dataset=case.baseline,
            baseline_packet=case.baseline_packet,
        )


def test_h13_effectful_packet_for_unaffected_order_fails_closed() -> None:
    case = replay_case("supplier")
    affected = set(
        derive_affected_order_ids(case.scenario.dataset, case.scenario.ground_truth)
    )
    order_id = next(item for item in dataset_order_ids(case.baseline) if item not in affected)
    scenario_packet = packet_from_dataset(
        case.scenario.dataset,
        order_id,
        case.scenario_packet.run.as_of_time,
    )
    baseline_packet = packet_from_dataset(
        case.baseline,
        order_id,
        case.scenario_packet.run.as_of_time,
    )
    with pytest.raises(C07EvaluationError, match="C07_EFFECTFUL_ORDER_NOT_AFFECTED"):
        evaluate_recommendation(
            scenario_packet,
            case.scenario,
            baseline_dataset=case.baseline,
            baseline_packet=baseline_packet,
        )


@pytest.mark.parametrize("attack", ("H14", "H15", "H16", "H17"))
def test_h14_h17_baseline_pair_attacks_fail_closed(attack: str) -> None:
    case = replay_case("capacity_arrival" if attack == "H16" else "supplier")
    if attack == "H14":
        order_id = next(
            item
            for item in dataset_order_ids(case.baseline)
            if item != case.scenario_packet.run.order_id
        )
        baseline_packet = packet_from_dataset(
            case.baseline,
            order_id,
            case.scenario_packet.run.as_of_time,
        )
    elif attack == "H15":
        baseline_packet = packet_from_dataset(
            case.baseline,
            case.scenario_packet.run.order_id,
            case.scenario_packet.run.as_of_time - timedelta(seconds=1),
        )
    elif attack == "H16":
        baseline_packet = adversarial_packet_fixture(
            case.baseline,
            case.scenario_packet.run.order_id,
            None,
            case.scenario_packet.run.as_of_time,
        )
    else:
        baseline_packet = None
    with pytest.raises(C07EvaluationError):
        evaluate_recommendation(
            case.scenario_packet,
            case.scenario,
            baseline_dataset=case.baseline,
            baseline_packet=baseline_packet,
        )


def _fresh_replay_digest(hash_seed: str) -> str:
    code = (
        "import hashlib; "
        "from test_c07_replay import replay_case; "
        "from flowlens.evaluation import evaluate_recommendation; "
        "from flowlens.decision.serialization import canonical_json_bytes; "
        "c=replay_case('supplier'); "
        "r=evaluate_recommendation(c.scenario_packet,c.scenario,"
        "baseline_dataset=c.baseline,baseline_packet=c.baseline_packet); "
        "print(hashlib.sha256(canonical_json_bytes(r)).hexdigest())"
    )
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = hash_seed
    environment["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT / "tests")))
    completed = subprocess.run(
        (sys.executable, "-c", code),
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return completed.stdout.strip()


def test_h30_fresh_process_replay_is_hash_seed_independent() -> None:
    first = _fresh_replay_digest("1")
    second = _fresh_replay_digest("987654")
    assert first == second
    assert len(first) == 64


@pytest.mark.parametrize(
    "module_name",
    ("flowlens", "flowlens.decision", "flowlens.api", "flowlens.worker"),
)
def test_h31_fresh_runtime_imports_do_not_reach_evaluation_or_hgt(
    module_name: str,
) -> None:
    code = (
        f"import {module_name}; import sys; "
        "bad=[n for n in sys.modules if n.startswith('flowlens.evaluation') or "
        "n=='flowlens.data.scenarios.ground_truth']; "
        "assert not bad, bad"
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run(
        (sys.executable, "-c", code),
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_h32_evaluation_is_not_a_decision_packet_field() -> None:
    assert "evaluation" not in DecisionPacket.__dataclass_fields__
    assert all(
        "RecommendationEvaluation" not in str(field.type)
        for field in DecisionPacket.__dataclass_fields__.values()
    )


def test_h35_h38_source_capability_audit() -> None:
    forbidden_imports = {
        "http",
        "openai",
        "pathlib",
        "random",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
        "time",
        "urllib",
    }
    forbidden_text = (
        "OutcomeEvaluation",
        "ExplanationRecord",
        "create_engine",
        "datetime.now",
        "datetime.utcnow",
        "manifest",
        "sessionmaker",
    )
    for path in sorted(EVALUATION_SOURCE.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        assert not imports & forbidden_imports, path
        assert not any(token in source for token in forbidden_text), path


def test_h1_h38_matrix_is_complete_and_uniquely_addressed() -> None:
    assert tuple(H1_H38_EVIDENCE) == tuple(f"H{index}" for index in range(1, 39))
    assert all(value.startswith("test_") for value in H1_H38_EVIDENCE.values())
    digest = hashlib.sha256(canonical_json_bytes(H1_H38_EVIDENCE)).hexdigest()
    assert len(digest) == 64
