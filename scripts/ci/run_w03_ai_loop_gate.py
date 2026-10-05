"""Fail-closed, exact-SHA development proof for the frozen W03 C09 critical pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pytest

SCHEMA = "w03-c09-regression-manifest-v1.1"
GATE = "w03-c09-ai-loop-gate-v1"
ENTRY = "d71d5baeb0862f2706358c26e182554b3807e8f6"
SEMANTICS = "EXACT_FUNCTION_SELECTOR_WITH_FROZEN_EXPANDED_CASE_COUNT"
# Canonical content identity independently freezes every selector, count and order.
FROZEN_CONTENT_SHA256 = "bc9be2ad3cee34e7ed67dfed28814a548e2e45a07bed12828555c0ede818c120"
FAMILY_IDS = (
    "F01 CORE_CONTRACTS",
    "F02 TEMPORAL_SEMANTIC_TRUST",
    "F03 SIGNAL_DIAGNOSIS_FAIL_CLOSED",
    "F04 COUNTERFACTUAL_ISOLATION",
    "F05 RECOMMENDATION_ABSTENTION",
    "F06 HUMAN_AUTHORITY_AUDIT",
    "F07 PROTECTED_EVALUATION_REPLAY",
    "F08 LLM_GROUNDING_SCHEMA_INJECTION",
    "F09 REAL_DATASET_BINDING_DIRECTION",
    "F10 RUNTIME_CAPABILITY_ISOLATION",
)
SELECTOR = re.compile(r"tests/(?:[A-Za-z_]\w*/)*test_\w+\.py::test_\w+", re.ASCII)
SHA = re.compile(r"[0-9a-f]{40}")


class GateError(ValueError):
    """An invalid or incomplete proof; never eligible for semantic PASS."""


@dataclass(frozen=True)
class Target:
    selector: str
    expected_cases: int


@dataclass(frozen=True)
class Family:
    id: str
    expected_cases: int
    targets: tuple[Target, ...]


@dataclass(frozen=True)
class Manifest:
    families: tuple[Family, ...]
    sha256: str


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise GateError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def invalid_constant(value: str) -> object:
    raise GateError(f"invalid JSON constant: {value}")


def parse_json(raw: bytes) -> object:
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def exact_object(value: object, keys: set[str]) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise GateError(f"expected object with exact keys: {sorted(keys)}")
    return cast(dict[str, object], value)


def positive_count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise GateError("expected positive integer case count")
    return value


def validate_selector(value: object) -> str:
    if not isinstance(value, str) or SELECTOR.fullmatch(value) is None:
        raise GateError("expected exact test-function selector under tests/")
    return value


def load_manifest(path: Path) -> Manifest:
    raw = path.read_bytes()
    value = parse_json(raw)
    doc = exact_object(
        value,
        {
            "schema_version",
            "gate_version",
            "checkpoint",
            "contract_entry_sha",
            "selector_semantics",
            "total_selectors",
            "total_cases",
            "families",
        },
    )
    for key, expected in (
        ("schema_version", SCHEMA),
        ("gate_version", GATE),
        ("checkpoint", "W03-C09"),
        ("contract_entry_sha", ENTRY),
        ("selector_semantics", SEMANTICS),
    ):
        if doc[key] != expected:
            raise GateError(f"incorrect frozen {key}")
    if positive_count(doc["total_selectors"]) != 38 or positive_count(doc["total_cases"]) != 85:
        raise GateError("frozen totals must be 38 selectors / 85 cases")
    items = doc["families"]
    if not isinstance(items, list) or len(items) != len(FAMILY_IDS):
        raise GateError("required ten-family set is incomplete")
    seen: set[str] = set()
    families: list[Family] = []
    for expected_id, item in zip(FAMILY_IDS, items, strict=True):
        family = exact_object(item, {"id", "expected_cases", "targets"})
        if family["id"] != expected_id:
            raise GateError("incorrect frozen family ID/order or duplicate family")
        case_count = positive_count(family["expected_cases"])
        targets = family["targets"]
        if not isinstance(targets, list) or not targets:
            raise GateError("family targets must be a nonempty list")
        parsed: list[Target] = []
        for item_target in targets:
            target = exact_object(item_target, {"selector", "expected_cases"})
            selector = validate_selector(target["selector"])
            if selector in seen:
                raise GateError(f"duplicate selector: {selector}")
            seen.add(selector)
            parsed.append(Target(selector, positive_count(target["expected_cases"])))
        if sum(target.expected_cases for target in parsed) != case_count:
            raise GateError("family expected_cases differs from target sum")
        families.append(Family(expected_id, case_count, tuple(parsed)))
    if len(seen) != 38 or sum(family.expected_cases for family in families) != 85:
        raise GateError("manifest selector/case totals differ from frozen totals")
    if hashlib.sha256(canonical(value)).hexdigest() != FROZEN_CONTENT_SHA256:
        raise GateError("frozen selector/count content or order differs")
    return Manifest(tuple(families), hashlib.sha256(raw).hexdigest())


def verify_head(expected: str, repo: Path) -> str:
    if SHA.fullmatch(expected) is None:
        raise GateError("expected-head must be 40 lowercase hex characters")
    actual = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, stdout=subprocess.PIPE, text=True
    ).stdout.strip()
    if actual != expected:
        raise GateError(f"exact source HEAD mismatch: expected {expected}, observed {actual}")
    return actual


class EvidenceRecorder:
    """Pytest hook observer in the isolated worker; records all three execution phases."""

    def __init__(self, output: Path) -> None:
        self.output = output
        self.collected: list[str] = []
        self.collection_errors = 0
        self.reports: list[dict[str, object]] = []

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        self.collected = [item.nodeid for item in session.items]

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        if report.failed:
            self.collection_errors += 1

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        self.reports.append(
            {
                "nodeid": report.nodeid,
                "when": report.when,
                "outcome": report.outcome,
                # Presence also catches an XPASS whose xfail reason is the empty string.
                "wasxfail": hasattr(report, "wasxfail"),
            }
        )

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        self.output.write_bytes(
            canonical(
                {
                    "schema_version": "w03-c09-pytest-evidence-v1",
                    "collected": self.collected,
                    "collection_errors": self.collection_errors,
                    "reports": self.reports,
                    "exit_code": int(exitstatus),
                }
            )
            + b"\n"
        )


def validate_evidence(family: Family, evidence: object, exit_code: int) -> list[dict[str, object]]:
    doc = exact_object(
        evidence, {"schema_version", "collected", "collection_errors", "reports", "exit_code"}
    )
    if (
        doc["schema_version"] != "w03-c09-pytest-evidence-v1"
        or exit_code != 0
        or type(doc["exit_code"]) is not int
        or doc["exit_code"] != 0
        or type(doc["collection_errors"]) is not int
        or doc["collection_errors"] != 0
    ):
        raise GateError("pytest exit or collection failure")
    collected = doc["collected"]
    reports = doc["reports"]
    if (
        not isinstance(collected, list)
        or not collected
        or not all(isinstance(node, str) for node in collected)
        or not isinstance(reports, list)
    ):
        raise GateError("missing/zero collected leaf cases or execution reports")
    nodes = cast(list[str], collected)
    if len(nodes) != len(set(nodes)) or len(nodes) != family.expected_cases:
        raise GateError("duplicate leaf cases or family expanded-count drift")
    targets: list[dict[str, object]] = []
    matched: set[str] = set()
    for target in family.targets:
        leaves = [
            node
            for node in nodes
            if node == target.selector
            or (node.startswith(target.selector + "[") and node.endswith("]"))
        ]
        if len(leaves) != target.expected_cases:
            raise GateError(f"missing selector or expanded-count drift: {target.selector}")
        matched.update(leaves)
        targets.append({"selector": target.selector, "tests": len(leaves), "nodeids": leaves})
    if matched != set(nodes):
        raise GateError("unexpected collected leaf outside frozen selectors")
    phases: dict[str, list[str]] = {node: [] for node in nodes}
    for item in reports:
        report = exact_object(item, {"nodeid", "when", "outcome", "wasxfail"})
        node = report["nodeid"]
        phase = report["when"]
        if (
            not isinstance(node, str)
            or node not in phases
            or not isinstance(phase, str)
            or phase not in {"setup", "call", "teardown"}
            or report["outcome"] != "passed"
            or report["wasxfail"] is not False
        ):
            raise GateError("failure/error/skip/xfail/xpass or unexpected execution report")
        phases[node].append(phase)
    if any(value != ["setup", "call", "teardown"] for value in phases.values()):
        raise GateError("incomplete or duplicate leaf execution phases")
    return targets


def execute_family(family: Family, repo: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="w03-c09-pytest-") as directory:
        evidence_path = Path(directory) / "evidence.json"
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker-evidence",
                str(evidence_path),
                *(target.selector for target in family.targets),
            ],
            cwd=repo,
            check=False,
        )
        if not evidence_path.is_file():
            raise GateError(f"missing pytest evidence: {family.id}")
        targets = validate_evidence(
            family, parse_json(evidence_path.read_bytes()), result.returncode
        )
    print(f"{family.id}: PASS ({len(family.targets)} selectors / {family.expected_cases} cases)")
    return {
        "id": family.id,
        "status": "PASS",
        "selectors": len(family.targets),
        "tests": family.expected_cases,
        "targets": targets,
    }


def write_summary(output: Path, summary: object) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical(summary) + b"\n")


def run_gate(
    manifest_path: Path, expected_head: str, output: Path, repo: Path
) -> dict[str, object]:
    if output.resolve().is_relative_to(repo.resolve()):
        raise GateError("summary output must be temporary and outside the source repository")
    # Invalidate a stale PASS before any proof; a partial run can never leave PASS evidence.
    write_summary(
        output,
        {"schema_version": "w03-c09-gate-summary-v1", "gate_version": GATE, "overall": "FAIL"},
    )
    head = verify_head(expected_head, repo)
    manifest = load_manifest(manifest_path)
    families = [execute_family(family, repo) for family in manifest.families]
    # Recheck identities after test execution, before issuing PASS.
    verify_head(expected_head, repo)
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != manifest.sha256:
        raise GateError("manifest bytes changed during proof")
    summary: dict[str, object] = {
        "schema_version": "w03-c09-gate-summary-v1",
        "gate_version": GATE,
        "implementation_sha": head,
        "manifest_sha256": manifest.sha256,
        "families": families,
        "overall": "PASS",
    }
    write_summary(output, summary)
    print(canonical(summary).decode("utf-8"))
    return summary


def main(argv: list[str] | None = None) -> int:
    args_list = sys.argv[1:] if argv is None else argv
    if args_list[:1] == ["--worker-evidence"]:
        worker = argparse.ArgumentParser(description="Internal isolated pytest evidence worker")
        worker.add_argument("--worker-evidence", type=Path, required=True)
        worker.add_argument("selectors", nargs="+")
        args = worker.parse_args(args_list)
        if args.worker_evidence.resolve().is_relative_to(Path.cwd().resolve()):
            raise GateError("worker evidence must be outside the source repository")
        selectors = [validate_selector(item) for item in args.selectors]
        return int(
            pytest.main(
                ["-q", "--tb=short", *selectors], plugins=[EvidenceRecorder(args.worker_evidence)]
            )
        )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(args_list)
    try:
        run_gate(args.manifest, args.expected_head, args.output_json, args.repo)
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"W03 AI loop gate FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
