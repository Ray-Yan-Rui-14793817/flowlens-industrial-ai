"""Fail-closed exact-SHA proof of the frozen W04-C09 investigation semantic pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pytest

SCHEMA = "w04-c09-regression-manifest-v1"
GATE = "w04-c09-investigation-gate-v1"
SUMMARY_SCHEMA = "w04-c09-gate-summary-v1"
ENTRY = "1fa841f2ee0d6612774c9f0ced204289df86e7a1"
SEMANTICS = "EXACT_FUNCTION_SELECTOR_WITH_FROZEN_EXPANDED_CASE_COUNT"
FROZEN_RAW_SHA256 = "d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1"
FROZEN_CONTENT_SHA256 = "937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad"
FAMILY_IDS = (
    "F01 C01_CONTRACTS_IDENTITY",
    "F02 C02_CASE_BINDING_TEMPORAL",
    "F03 C03_PLANNING_DETERMINISM",
    "F04 C04_AUTHORIZED_NAVIGATION_READ_ONLY",
    "F05 C05_FINDINGS_CONFLICT_UNCERTAINTY",
    "F06 C06_HUMAN_AUTHORITY_AUDIT",
    "F07 C07_SUMMARY_GROUNDING",
    "F08 C08_PROTECTED_REPLAY",
    "F09 SOURCE_EVOLUTION_GOVERNANCE",
)
SELECTOR = re.compile(r"tests/(?:[A-Za-z_]\w*/)*test_\w+\.py::test_\w+", re.ASCII)
SHA = re.compile(r"[0-9a-f]{40}")


class GateError(ValueError):
    """Missing, changed or incomplete evidence is never eligible for PASS."""


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
        raise GateError(f"expected exact object keys: {sorted(keys)}")
    return cast(dict[str, object], value)


def positive_count(value: object) -> int:
    if type(value) is not int or value <= 0:
        raise GateError("expected positive integer case count")
    return value


def validate_selector(value: object) -> str:
    if not isinstance(value, str) or SELECTOR.fullmatch(value) is None:
        raise GateError("expected exact test-function selector under tests/")
    return value


def parse_family(value: object) -> Family:
    family = exact_object(value, {"id", "expected_cases", "targets"})
    if not isinstance(family["id"], str):
        raise GateError("family ID must be text")
    case_count = positive_count(family["expected_cases"])
    targets = family["targets"]
    if not isinstance(targets, list) or not targets:
        raise GateError("family targets must be a nonempty list")
    parsed: list[Target] = []
    seen: set[str] = set()
    for item in targets:
        target = exact_object(item, {"selector", "expected_cases"})
        selector = validate_selector(target["selector"])
        if selector in seen:
            raise GateError("duplicate selector")
        seen.add(selector)
        parsed.append(Target(selector, positive_count(target["expected_cases"])))
    if sum(target.expected_cases for target in parsed) != case_count:
        raise GateError("family expanded count differs from target sum")
    return Family(family["id"], case_count, tuple(parsed))


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
            "baseline",
            "total_selectors",
            "total_cases",
            "families",
        },
    )
    for key, expected in (
        ("schema_version", SCHEMA),
        ("gate_version", GATE),
        ("checkpoint", "W04-C09"),
        ("contract_entry_sha", ENTRY),
        ("selector_semantics", SEMANTICS),
    ):
        if doc[key] != expected:
            raise GateError(f"incorrect frozen {key}")
    if positive_count(doc["total_selectors"]) != 67 or positive_count(doc["total_cases"]) != 81:
        raise GateError("frozen totals must be 67 selectors / 81 cases")
    items = doc["families"]
    if not isinstance(items, list) or len(items) != 9:
        raise GateError("required nine-family set is incomplete")
    seen: set[str] = set()
    families: list[Family] = []
    for expected_id, item in zip(FAMILY_IDS, items, strict=True):
        family = parse_family(item)
        if family.id != expected_id:
            raise GateError("incorrect frozen family ID/order")
        selectors = {target.selector for target in family.targets}
        if seen & selectors:
            raise GateError("duplicate selector across families")
        seen.update(selectors)
        families.append(family)
    if len(seen) != 67 or sum(f.expected_cases for f in families) != 81:
        raise GateError("manifest totals differ from frozen totals")
    # Independently pins the complete baseline object, all keys, selectors, counts and order.
    if hashlib.sha256(canonical(value)).hexdigest() != FROZEN_CONTENT_SHA256:
        raise GateError("frozen manifest content differs")
    if hashlib.sha256(raw).hexdigest() != FROZEN_RAW_SHA256:
        raise GateError("frozen manifest bytes differ")
    return Manifest(tuple(families), FROZEN_RAW_SHA256)


def verify_head(expected: str, repo: Path) -> str:
    if SHA.fullmatch(expected) is None:
        raise GateError("expected-head must be 40 lowercase hex characters")
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    if actual != expected:
        raise GateError(f"exact source HEAD mismatch: expected {expected}, observed {actual}")
    return actual


def validate_collection(family: Family, collected: object) -> list[str]:
    if not isinstance(collected, list) or not all(isinstance(n, str) for n in collected):
        raise GateError("missing exact collection")
    nodes = cast(list[str], collected)
    if len(nodes) != len(set(nodes)) or len(nodes) != family.expected_cases:
        raise GateError("duplicate or changed family leaf collection")
    matched: set[str] = set()
    for target in family.targets:
        leaves = [
            n
            for n in nodes
            if n == target.selector or (n.startswith(target.selector + "[") and n.endswith("]"))
        ]
        if len(leaves) != target.expected_cases:
            raise GateError(f"missing/renamed selector or count drift: {target.selector}")
        matched.update(leaves)
    if matched != set(nodes):
        raise GateError("unexpected collected leaf")
    return nodes


class EvidenceRecorder:
    """Observes collection and every terminal phase inside one fresh pytest worker."""

    def __init__(self, output: Path, family: Family) -> None:
        self.output = output
        self.family = family
        self.collected: list[str] = []
        self.collection_errors = 0
        self.deselected = 0
        self.reports: list[dict[str, object]] = []

    def pytest_deselected(self, items: list[pytest.Item]) -> None:
        self.deselected += len(items)

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        if report.failed:
            self.collection_errors += 1

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        self.collected = [item.nodeid for item in session.items]
        try:
            validate_collection(self.family, self.collected)
            if self.collection_errors or self.deselected:
                raise GateError("collection error or deselection")
        except GateError as error:
            pytest.exit(str(error), returncode=2)

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        self.reports.append(
            {
                "nodeid": report.nodeid,
                "when": report.when,
                "outcome": report.outcome,
                "wasxfail": hasattr(report, "wasxfail"),
            }
        )

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        self.output.write_bytes(
            canonical(
                {
                    "schema_version": "w04-c09-pytest-evidence-v1",
                    "collected": self.collected,
                    "collection_errors": self.collection_errors,
                    "deselected": self.deselected,
                    "reports": self.reports,
                    "exit_code": int(exitstatus),
                }
            )
            + b"\n"
        )


def validate_evidence(family: Family, evidence: object, exit_code: int) -> None:
    doc = exact_object(
        evidence,
        {
            "schema_version",
            "collected",
            "collection_errors",
            "deselected",
            "reports",
            "exit_code",
        },
    )
    if doc["schema_version"] != "w04-c09-pytest-evidence-v1" or exit_code != 0:
        raise GateError("pytest failure")
    for key in ("exit_code", "collection_errors", "deselected"):
        if type(doc[key]) is not int or doc[key] != 0:
            raise GateError("pytest exit, collection or deselection failure")
    nodes = validate_collection(family, doc["collected"])
    reports = doc["reports"]
    if not isinstance(reports, list):
        raise GateError("missing execution reports")
    phases: dict[str, list[str]] = {n: [] for n in nodes}
    for item in reports:
        report = exact_object(item, {"nodeid", "when", "outcome", "wasxfail"})
        node, phase = report["nodeid"], report["when"]
        if (
            not isinstance(node, str)
            or node not in phases
            or not isinstance(phase, str)
            or phase not in {"setup", "call", "teardown"}
            or report["outcome"] != "passed"
            or report["wasxfail"] is not False
        ):
            raise GateError("failure/error/skip/xfail/xpass or unexpected phase")
        phases[node].append(phase)
    if any(value != ["setup", "call", "teardown"] for value in phases.values()):
        raise GateError("incomplete or duplicate terminal phases")


def execute_family(family: Family, repo: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="w04-c09-family-") as directory:
        evidence, spec = Path(directory) / "evidence.json", Path(directory) / "family.json"
        spec.write_bytes(
            canonical(
                {
                    "id": family.id,
                    "expected_cases": family.expected_cases,
                    "targets": [
                        {"selector": t.selector, "expected_cases": t.expected_cases}
                        for t in family.targets
                    ],
                }
            )
            + b"\n"
        )
        environment = dict(os.environ, PYTEST_ADDOPTS="", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(Path(__file__).resolve()),
                "--worker-evidence",
                str(evidence),
                "--family-spec",
                str(spec),
                *(t.selector for t in family.targets),
            ],
            cwd=repo,
            env=environment,
            check=False,
        )
        if not evidence.is_file():
            raise GateError(f"missing pytest evidence: {family.id}")
        validate_evidence(family, parse_json(evidence.read_bytes()), result.returncode)
    print(f"{family.id}: PASS ({len(family.targets)} selectors / {family.expected_cases} cases)")
    return {
        "id": family.id,
        "status": "PASS",
        "selectors": len(family.targets),
        "tests": family.expected_cases,
    }


def make_summary(
    manifest: Manifest, head: str, families: list[dict[str, object]]
) -> dict[str, object]:
    expected = [
        {"id": f.id, "status": "PASS", "selectors": len(f.targets), "tests": f.expected_cases}
        for f in manifest.families
    ]
    if families != expected:
        raise GateError("family result, subprocess order or totals drift")
    summary: dict[str, object] = {
        "schema_version": SUMMARY_SCHEMA,
        "gate_version": GATE,
        "implementation_sha": head,
        "manifest_sha256": manifest.sha256,
        "manifest_content_sha256": FROZEN_CONTENT_SHA256,
        "total_families": 9,
        "total_selectors": 67,
        "total_tests": 81,
        "families": families,
        "overall": "PASS",
    }
    return summary | {"summary_sha256": hashlib.sha256(canonical(summary)).hexdigest()}


def validate_summary(raw: bytes, manifest: Manifest, head: str) -> dict[str, object]:
    families = [
        {"id": f.id, "status": "PASS", "selectors": len(f.targets), "tests": f.expected_cases}
        for f in manifest.families
    ]
    expected = make_summary(manifest, head, families)
    if raw != canonical(expected) + b"\n" or parse_json(raw) != expected:
        raise GateError("summary bytes/content/self-seal are not exact canonical proof")
    return expected


def run_gate(
    manifest_path: Path, expected_head: str, output: Path, repo: Path
) -> dict[str, object]:
    if output.resolve().is_relative_to(repo.resolve()):
        raise GateError("summary output must be outside the source repository")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Invalidate any earlier PASS before reading HEAD/manifest or executing any test.
    output.write_bytes(canonical({"schema_version": SUMMARY_SCHEMA, "overall": "FAIL"}) + b"\n")
    head = verify_head(expected_head, repo)
    manifest = load_manifest(manifest_path)
    families = [execute_family(family, repo) for family in manifest.families]
    verify_head(expected_head, repo)
    if load_manifest(manifest_path) != manifest:
        raise GateError("manifest changed during proof")
    summary = make_summary(manifest, head, families)
    raw = canonical(summary) + b"\n"
    validate_summary(raw, manifest, head)
    output.write_bytes(raw)
    print(raw.decode("utf-8"), end="")
    return summary


def main(argv: list[str] | None = None) -> int:
    args_list = sys.argv[1:] if argv is None else argv
    try:
        if args_list[:1] == ["--worker-evidence"]:
            worker = argparse.ArgumentParser(description="One isolated pytest family worker")
            worker.add_argument("--worker-evidence", type=Path, required=True)
            worker.add_argument("--family-spec", type=Path, required=True)
            worker.add_argument("selectors", nargs="+")
            args = worker.parse_args(args_list)
            if any(
                p.resolve().is_relative_to(Path.cwd().resolve())
                for p in (
                    args.worker_evidence,
                    args.family_spec,
                )
            ):
                raise GateError("worker proof files must be outside the source repository")
            family = parse_family(parse_json(args.family_spec.read_bytes()))
            if args.selectors != [t.selector for t in family.targets]:
                raise GateError("worker received selectors outside its exact family")
            os.environ["PYTEST_ADDOPTS"] = ""
            os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
            return int(
                pytest.main(
                    ["-o", "addopts=", "-q", "--tb=short", *args.selectors],
                    plugins=[EvidenceRecorder(args.worker_evidence, family)],
                )
            )
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--manifest", type=Path, required=True)
        parser.add_argument("--expected-head", required=True)
        parser.add_argument("--output-json", type=Path, required=True)
        parser.add_argument("--repo", type=Path, default=Path.cwd())
        args = parser.parse_args(args_list)
        run_gate(args.manifest, args.expected_head, args.output_json, args.repo)
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"W04 investigation gate FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
