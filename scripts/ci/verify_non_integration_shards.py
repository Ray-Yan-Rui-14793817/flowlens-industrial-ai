"""Fail-closed exact shard aggregation and same-SHA legacy/shadow outcome equivalence."""

from __future__ import annotations

import argparse
import copy
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from plan_non_integration_shards import (
    BASELINE,
    MARKER,
    SHARD_COUNT,
    WEIGHTS,
    ProofError,
    collect_nodes,
    enforce_entry,
    outside_repository,
    read_json,
    validate_plan,
    verify_head,
    write_json,
)
from pytest_outcome_receipt import (
    OUTCOMES,
    make_receipt,
    receipt_summary,
    require_success,
    validate_receipt,
)


def read_evidence(directory: Path) -> tuple[dict[str, Any], Path]:
    if (
        directory.is_symlink()
        or not directory.is_dir()
        or {path.name for path in directory.iterdir()} != {"receipt.json", "junit.xml"}
    ):
        raise ProofError("missing, ambiguous or unexpected receipt/JUnit artifact")
    return read_json(directory / "receipt.json"), directory / "junit.xml"


def aggregate(plan: dict[str, Any], receipts_dir: Path, role: str, output: Path) -> dict[str, Any]:
    if role not in {"shadow-shard", "nonint-shard"}:
        raise ProofError("unexpected shard role")
    if (
        receipts_dir.is_symlink()
        or not receipts_dir.is_dir()
        or {path.name for path in receipts_dir.iterdir()}
        != {f"shard-{i}" for i in range(SHARD_COUNT)}
    ):
        raise ProofError("missing, duplicate or unexpected shard artifact")
    all_nodes: list[str] = []
    outcomes: dict[str, list[str]] = {key: [] for key in OUTCOMES}
    suites = ET.Element("testsuites")
    summaries = []
    for index in range(SHARD_COUNT):
        receipt, junit = read_evidence(receipts_dir / f"shard-{index}")
        assigned = plan["shards"][index]["nodeids"]
        validate_receipt(receipt, plan, role, index, assigned, junit)
        require_success(receipt, junit)
        all_nodes.extend(receipt["collected_nodeids"])
        for key in OUTCOMES:
            outcomes[key].extend(receipt[f"{key}_nodeids"])
        xml = ET.parse(junit).getroot()
        if xml.tag == "testsuite":
            suites.append(copy.deepcopy(xml))
        else:
            for suite in xml:
                if suite.tag != "testsuite":
                    raise ProofError("unexpected JUnit element")
                suites.append(copy.deepcopy(suite))
        summaries.append(receipt_summary(receipt))
    if len(all_nodes) != len(set(all_nodes)) or sorted(all_nodes) != plan["collected_nodeids"]:
        raise ProofError("missing, duplicate or unexpected node across shards")
    enforce_entry(sorted(all_nodes), read_json(BASELINE))
    output = outside_repository(output)
    if output.exists():
        raise ProofError("refuse stale aggregate directory")
    output.mkdir(parents=True)
    junit = output / "junit.xml"
    ET.ElementTree(suites).write(junit, encoding="utf-8", xml_declaration=True)
    aggregate_role = "shadow-nonint-aggregate" if role == "shadow-shard" else "nonint-aggregate"
    receipt = make_receipt(
        plan["head_sha"],
        aggregate_role,
        MARKER,
        None,
        plan,
        sorted(all_nodes),
        sorted(all_nodes),
        {key: sorted(value) for key, value in outcomes.items()},
        0,
        junit,
    )
    validate_receipt(receipt, plan, aggregate_role, None, plan["collected_nodeids"], junit)
    require_success(receipt, junit)
    write_json(output / "receipt.json", receipt)
    print(
        "SHARD_AGGREGATE "
        + json.dumps(
            receipt_summary(receipt)
            | {
                "exact_union": "PASS",
                "exact_once": "PASS",
                "entry_no_loss": "PASS",
                "shards": summaries,
            },
            sort_keys=True,
        )
    )
    return receipt


def compare_outcomes(left: dict[str, Any], right: dict[str, Any]) -> None:
    for field in (
        "head_sha",
        "plan_sha256",
        "weights_sha256",
        "marker_expression",
        "entry_baseline_nodeids_sha256",
        "assigned_nodeids",
        "collected_nodeids",
    ):
        if left[field] != right[field]:
            raise ProofError(f"SHADOW_EQUIVALENCE_FAILED: {field} mismatch")
    for outcome in OUTCOMES:
        if left[f"{outcome}_nodeids"] != right[f"{outcome}_nodeids"]:
            raise ProofError(f"SHADOW_EQUIVALENCE_FAILED: {outcome} exact node set mismatch")


def equivalence(
    plan: dict[str, Any],
    legacy_nonint: Path,
    legacy_integration: Path,
    shadow_nonint: Path,
    shadow_integration: Path,
) -> dict[str, Any]:
    integration = collect_nodes("integration")
    roles = [
        (legacy_nonint, "legacy-nonint", plan["collected_nodeids"]),
        (shadow_nonint, "shadow-nonint-aggregate", plan["collected_nodeids"]),
        (legacy_integration, "legacy-integration", integration),
        (shadow_integration, "shadow-integration", integration),
    ]
    receipts = []
    for directory, role, assigned in roles:
        receipt, junit = read_evidence(directory)
        validate_receipt(receipt, plan, role, None, assigned, junit)
        require_success(receipt, junit)
        receipts.append(receipt)
    enforce_entry(plan["collected_nodeids"], read_json(BASELINE))
    compare_outcomes(receipts[0], receipts[1])
    compare_outcomes(receipts[2], receipts[3])
    result = {
        "schema_version": "w04-devctrl02-shadow-equivalence-v1",
        "head_sha": plan["head_sha"],
        "plan_sha256": plan["plan_sha256"],
        "coverage_equivalence": "PASS",
        "terminal_outcome_equivalence": "PASS",
        "entry_no_loss": "PASS",
        "overall": "PASS",
        "receipts": [receipt_summary(receipt) for receipt in receipts],
    }
    print("SHADOW_EQUIVALENCE " + json.dumps(result, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    aggregation = sub.add_parser("aggregate")
    aggregation.add_argument("--receipts-dir", type=Path, required=True)
    aggregation.add_argument("--role", choices=["shadow-shard", "nonint-shard"], required=True)
    aggregation.add_argument("--output-dir", type=Path, required=True)
    equivalent = sub.add_parser("equivalence")
    for name in ("legacy-nonint", "legacy-integration", "shadow-nonint", "shadow-integration"):
        equivalent.add_argument(f"--{name}-dir", type=Path, required=True)
    equivalent.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    try:
        verify_head(args.expected_head)
        plan = read_json(args.plan)
        validate_plan(plan, read_json(WEIGHTS), read_json(BASELINE), args.expected_head)
        if collect_nodes(MARKER) != plan["collected_nodeids"]:
            raise ProofError("plan union differs from exact current collection")
        if args.command == "aggregate":
            aggregate(plan, args.receipts_dir, args.role, args.output_dir)
        else:
            result = equivalence(
                plan,
                args.legacy_nonint_dir,
                args.legacy_integration_dir,
                args.shadow_nonint_dir,
                args.shadow_integration_dir,
            )
            write_json(outside_repository(args.output_json), result)
        return 0
    except (ProofError, OSError) as exc:
        print(f"SHARD_VERIFICATION_FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
