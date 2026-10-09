"""Pytest terminal outcomes with exact node IDs, preserving pytest's exit status."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pytest
from plan_non_integration_shards import (
    BASELINE,
    MARKER,
    WEIGHTS,
    ProofError,
    check_seal,
    collect_nodes,
    digest,
    exact_keys,
    integer,
    nodes,
    outside_repository,
    read_json,
    sealed,
    sha,
    validate_plan,
    verify_head,
    write_json,
)

RECEIPT_SCHEMA = "w04-devctrl02-pytest-outcome-receipt-v1"
OUTCOMES = ("passed", "skipped", "xfail", "xpass", "failed", "error")
SHARD_ROLES = {"shadow-shard", "nonint-shard"}
NONINT_ROLES = SHARD_ROLES | {"legacy-nonint", "shadow-nonint-aggregate", "nonint-aggregate"}
INTEGRATION_ROLES = {"legacy-integration", "shadow-integration", "integration-data"}
ACCEPTED_LINUX_SKIPS = sorted(
    f"tests/test_investigation_human_store.py::"
    f"test_j40_j45_windows_junction_surfaces_fail_closed[{surface}]"
    for surface in ("case", "locks", "root")
)


class OutcomeRecorder:
    def __init__(self, assigned: list[str]) -> None:
        self.assigned = assigned
        self.collected: list[str] = []
        self.reports: dict[str, dict[str, pytest.TestReport]] = {}
        self.collection_errors: list[str] = []

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        self.collected = nodes([item.nodeid for item in session.items], sorted_required=False)
        if self.collected != self.assigned:
            pytest.exit("OUTCOME_COLLECTION_MISMATCH", returncode=4)

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        if report.failed:
            self.collection_errors.append(report.nodeid)

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        phases = self.reports.setdefault(report.nodeid, {})
        if report.when in phases:
            raise ProofError("duplicate pytest phase report")
        phases[report.when] = report

    def terminal_outcomes(self) -> dict[str, list[str]]:
        if self.collection_errors or self.collected != self.assigned:
            raise ProofError("collection error or collect-only mismatch")
        if set(self.reports) != set(self.collected):
            raise ProofError("missing or unexpected terminal node report")
        result: dict[str, list[str]] = {outcome: [] for outcome in OUTCOMES}
        for node in self.collected:
            phases = self.reports[node]
            setup, call, teardown = (phases.get(name) for name in ("setup", "call", "teardown"))
            if setup is None or teardown is None:
                raise ProofError("incomplete pytest phase reports")
            if setup.failed or teardown.failed:
                outcome = "error"
            elif call is not None and call.failed:
                # Pytest removes wasxfail from strict XPASS; retain its actual terminal category.
                outcome = "xpass" if str(call.longrepr).startswith("[XPASS(strict)]") else "failed"
            elif setup.skipped:
                outcome = "xfail" if hasattr(setup, "wasxfail") else "skipped"
            elif call is not None and call.skipped:
                outcome = "xfail" if hasattr(call, "wasxfail") else "skipped"
            elif call is not None and call.passed:
                outcome = "xpass" if hasattr(call, "wasxfail") else "passed"
            else:
                raise ProofError("unknown terminal pytest state")
            result[outcome].append(node)
        return result


def junit_facts(path: Path) -> dict[str, int]:
    if path.is_symlink() or not path.is_file():
        raise ProofError("missing or nonregular JUnit")
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise ProofError("malformed JUnit") from exc
    if root.tag not in {"testsuites", "testsuite"}:
        raise ProofError("wrong JUnit root")
    cases = list(root.iter("testcase"))
    if not cases:
        raise ProofError("empty JUnit")
    for suite in root.iter("testsuite"):
        expected = {
            "tests": len(list(suite.iter("testcase"))),
            "failures": len(list(suite.iter("failure"))),
            "errors": len(list(suite.iter("error"))),
            "skipped": len(list(suite.iter("skipped"))),
        }
        for key, count in expected.items():
            try:
                observed = int(suite.attrib[key])
            except (KeyError, ValueError) as exc:
                raise ProofError("invalid JUnit count metadata") from exc
            if observed != count:
                raise ProofError("inconsistent JUnit failure/error/count metadata")
    return {
        "tests": len(cases),
        "failures": len(list(root.iter("failure"))),
        "errors": len(list(root.iter("error"))),
        "skipped": len(list(root.iter("skipped"))),
    }


def make_receipt(
    head: str,
    role: str,
    marker: str,
    shard_id: int | None,
    plan: dict[str, Any],
    assigned: list[str],
    collected: list[str],
    outcomes: dict[str, list[str]],
    exit_code: int,
    junit: Path,
) -> dict[str, Any]:
    payload = {
        "schema_version": RECEIPT_SCHEMA,
        "head_sha": head,
        "proof_role": role,
        "marker_expression": marker,
        "shard_id": shard_id,
        "plan_sha256": plan["plan_sha256"],
        "weights_sha256": plan["weights_sha256"],
        "entry_baseline_nodeids_sha256": plan["entry_baseline_nodeids_sha256"],
        "pytest_version": pytest.__version__,
        "assigned_node_count": len(assigned),
        "assigned_nodeids": assigned,
        "assigned_nodeids_sha256": digest(assigned),
        "collected_node_count": len(collected),
        "collected_nodeids": collected,
        "collected_nodeids_sha256": digest(collected),
        "pytest_exit_code": exit_code,
        "junit_sha256": hashlib.sha256(junit.read_bytes()).hexdigest(),
    }
    for outcome in OUTCOMES:
        payload[f"{outcome}_nodeids"] = outcomes[outcome]
        payload[f"{outcome}_count"] = len(outcomes[outcome])
    return sealed(payload, "receipt_sha256")


def validate_receipt(
    value: dict[str, Any],
    plan: dict[str, Any],
    role: str,
    shard_id: int | None,
    assigned: list[str],
    junit: Path,
) -> None:
    exact_keys(
        value,
        {
            "schema_version",
            "head_sha",
            "proof_role",
            "marker_expression",
            "shard_id",
            "plan_sha256",
            "weights_sha256",
            "entry_baseline_nodeids_sha256",
            "pytest_version",
            "assigned_node_count",
            "assigned_nodeids",
            "assigned_nodeids_sha256",
            "collected_node_count",
            "collected_nodeids",
            "collected_nodeids_sha256",
            "pytest_exit_code",
            "junit_sha256",
            "receipt_sha256",
        }
        | {f"{outcome}_{suffix}" for outcome in OUTCOMES for suffix in ("nodeids", "count")},
        "receipt",
    )
    check_seal(value, "receipt_sha256")
    marker = MARKER if role in NONINT_ROLES else "integration"
    if role not in NONINT_ROLES | INTEGRATION_ROLES:
        raise ProofError("unexpected receipt role")
    if role in SHARD_ROLES:
        if integer(shard_id, "shard ID") not in range(4) or type(value["shard_id"]) is not int:
            raise ProofError("unexpected shard ID")
    elif shard_id is not None:
        raise ProofError("unexpected aggregate/integration shard ID")
    if (
        value["schema_version"] != RECEIPT_SCHEMA
        or value["head_sha"] != plan["head_sha"]
        or value["proof_role"] != role
        or value["marker_expression"] != marker
        or value["shard_id"] != shard_id
        or value["pytest_version"] != plan["pytest_version"]
        or any(
            value[key] != plan[key]
            for key in ("plan_sha256", "weights_sha256", "entry_baseline_nodeids_sha256")
        )
    ):
        raise ProofError("wrong receipt binding")
    sha(value["head_sha"], 40)
    for prefix in ("assigned", "collected"):
        selected = nodes(value[f"{prefix}_nodeids"])
        if (
            selected != assigned
            or integer(value[f"{prefix}_node_count"], "node count", 1) != len(selected)
            or value[f"{prefix}_nodeids_sha256"] != digest(selected)
        ):
            raise ProofError("receipt assigned/collected node mismatch")
    terminal: list[str] = []
    for outcome in OUTCOMES:
        selected = value[f"{outcome}_nodeids"]
        if not isinstance(selected, list):
            raise ProofError("invalid terminal node list")
        if selected:
            nodes(selected)
        if integer(value[f"{outcome}_count"], "outcome count") != len(selected):
            raise ProofError("inconsistent outcome count")
        terminal.extend(selected)
    if len(terminal) != len(set(terminal)) or sorted(terminal) != assigned:
        raise ProofError("terminal outcomes must partition exact collected node IDs")
    integer(value["pytest_exit_code"], "pytest exit code")
    if value["pytest_exit_code"] not in range(6):
        raise ProofError("invalid pytest exit code")
    junit_facts(junit)
    if value["junit_sha256"] != hashlib.sha256(junit.read_bytes()).hexdigest():
        raise ProofError("wrong JUnit digest")


def require_success(
    value: dict[str, Any], junit: Path, *, enforce_skip_policy: bool = True
) -> None:
    facts = junit_facts(junit)
    if (
        value["pytest_exit_code"] != 0
        or value["failed_count"]
        or value["error_count"]
        or facts["failures"]
        or facts["errors"]
        or facts["tests"] != value["collected_node_count"]
        or facts["skipped"] != value["skipped_count"] + value["xfail_count"]
    ):
        raise ProofError("pytest non-zero, failed/error outcome or inconsistent JUnit")
    if enforce_skip_policy:
        expected_skips = (
            sorted(set(ACCEPTED_LINUX_SKIPS) & set(value["collected_nodeids"]))
            if value["marker_expression"] == MARKER
            else []
        )
        if value["skipped_nodeids"] != expected_skips:
            raise ProofError("new skip or silently disappeared accepted skip")


def receipt_summary(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value[key]
        for key in (
            "head_sha",
            "proof_role",
            "shard_id",
            "plan_sha256",
            "weights_sha256",
            "entry_baseline_nodeids_sha256",
            "collected_node_count",
            "collected_nodeids_sha256",
            "pytest_exit_code",
            "junit_sha256",
            "receipt_sha256",
        )
    } | {
        "outcomes": {
            outcome: {
                "count": value[f"{outcome}_count"],
                "nodeids_sha256": digest(value[f"{outcome}_nodeids"]),
            }
            for outcome in OUTCOMES
        },
        "outcome_map_sha256": digest(
            {outcome: value[f"{outcome}_nodeids"] for outcome in OUTCOMES}
        ),
    }


def run_receipt(
    plan_path: Path, expected_head: str, role: str, marker: str, shard_id: int | None, output: Path
) -> int:
    verify_head(expected_head)
    plan = read_json(plan_path)
    validate_plan(plan, read_json(WEIGHTS), read_json(BASELINE), expected_head)
    if (
        role in NONINT_ROLES
        and marker != MARKER
        or role in INTEGRATION_ROLES
        and marker != "integration"
        or role not in SHARD_ROLES | {"legacy-nonint"} | INTEGRATION_ROLES
    ):
        raise ProofError("invalid execution role/marker")
    targets: list[str] = []
    if role in SHARD_ROLES:
        index = integer(shard_id, "shard ID")
        if index not in range(4):
            raise ProofError("unexpected shard ID")
        shard = plan["shards"][index]
        assigned = shard["nodeids"]
        targets = shard["files"]
    else:
        if shard_id is not None:
            raise ProofError("unexpected nonshard ID")
        assigned = collect_nodes(marker)
        if marker == MARKER and assigned != plan["collected_nodeids"]:
            raise ProofError("legacy complete collection differs from plan")
    if collect_nodes(marker, files=targets) != assigned:
        raise ProofError("shard collect-only exact-set mismatch")
    output = outside_repository(output)
    if output.exists():
        raise ProofError("refuse stale receipt directory")
    output.mkdir(parents=True)
    junit = output / "junit.xml"
    recorder = OutcomeRecorder(assigned)
    # Preserve marker selection, fixtures, failure handling and pytest's original exit status.
    exit_code = int(
        pytest.main(["-m", marker, *targets, "--junitxml", str(junit)], plugins=[recorder])
    )
    try:
        receipt = make_receipt(
            expected_head,
            role,
            marker,
            shard_id,
            plan,
            assigned,
            recorder.collected,
            recorder.terminal_outcomes(),
            exit_code,
            junit,
        )
        validate_receipt(receipt, plan, role, shard_id, assigned, junit)
        write_json(output / "receipt.json", receipt)
        print("OUTCOME_RECEIPT " + json.dumps(receipt_summary(receipt), sort_keys=True))
    except (ProofError, OSError) as exc:
        print(f"OUTCOME_RECEIPT_FAIL_CLOSED: {exc}", file=sys.stderr)
        return exit_code if exit_code else 1
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--marker", choices=[MARKER, "integration"], required=True)
    parser.add_argument("--shard-id", type=int)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run_receipt(
            args.plan, args.expected_head, args.role, args.marker, args.shard_id, args.output_dir
        )
    except (ProofError, OSError) as exc:
        print(f"OUTCOME_RECEIPT_FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
