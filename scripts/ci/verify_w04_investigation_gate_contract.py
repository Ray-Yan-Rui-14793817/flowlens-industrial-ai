"""Independent, adversarial W04-C09 V1.1 runner, workflow and replay-source proof."""

from __future__ import annotations

import argparse
import ast
import contextlib
import copy
import hashlib
import io
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import plan_non_integration_shards as planner
import run_w04_investigation_gate as runner

ROOT = Path(__file__).resolve().parents[2]
ENTRY = "1fa841f2ee0d6612774c9f0ced204289df86e7a1"
MANIFEST = ROOT / "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json"
RAW_DIGEST = "d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1"
CONTENT_DIGEST = "937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad"
REPAIR_01_SHA256 = "744640783621660de009a8a1656ebb55bf752802ecb7e8256b8a1d9a8f3ee0ef"
AUTHORIZED_META_CI_FUNCTIONS = {
    "tests/test_ci_change_classifier.py": frozenset(
        {
            "test_workflow_routes_all_classes_to_a_stable_fail_closed_gate",
        }
    ),
    "tests/test_c09_ci_gate.py": frozenset(
        {
            "test_workflow_one_job_exact_schedule_source_manifest_and_environment",
            "test_verification_runs_actual_shell_truth_table",
        }
    ),
}
AUTHORIZED_REPLAY_SYMBOLS = frozenset(
    {
        "DEVCTRL_03_ENTRY_SHA",
        "C09_ENTRY_SHA",
        "W04_C09_MANIFEST_CONTENT_SHA256",
        "FULL_JOBS",
        "_devctrl03_workflow_delta_guard",
        "test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged",
        "_check_native_metadata",
        "_native_metadata_fixture",
        "_validate_w04_c09_gate_summary",
        "test_r46_stage_b_exact_sha_full_native_ci",
    }
)
STAGE_A = (
    ".github/workflows/ci.yml",
    "scripts/ci/run_w04_investigation_gate.py",
    "scripts/ci/verify_w04_investigation_gate_contract.py",
    "tests/test_investigation_replay.py",
    *(
        f"docs/w04/checkpoints/c09/W04_C09_{name}.md"
        for name in (
            "AUTHORIZATION_CONTRACT",
            "HUMAN_AUTHORIZATION",
            "CONTEXT_LOCK",
            "CI_REGRESSION_CONTRACT",
            "HARNESS_SPEC",
            "GPT_REVIEW_CHECKLIST",
        )
    ),
    "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json",
    "docs/w04/checkpoints/c09/specs/authorized_paths.json",
    "tests/test_ci_change_classifier.py",
    "tests/test_c09_ci_gate.py",
)
STAGE_B = ("docs/w04/checkpoints/c09/W04_C09_R_DEVELOPMENT_ROUND_REPORT.md",)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git(*arguments: str, repo: Path = ROOT) -> bytes:
    return subprocess.check_output(["git", *arguments], cwd=repo)


def workflow_blocks(raw: bytes) -> tuple[bytes, dict[str, bytes]]:
    require(raw.count(b"\njobs:\n") == 1, "ambiguous jobs root")
    start = raw.index(b"\njobs:\n") + len(b"\njobs:\n")
    matches = list(re.finditer(rb"(?m)^  ([a-z][a-z0-9-]*):\n", raw[start:]))
    require(bool(matches) and matches[0].start() == 0, "invalid job layout")
    jobs: dict[str, bytes] = {}
    for i, match in enumerate(matches):
        name = match[1].decode()
        require(name not in jobs, "duplicate workflow job")
        end = start + matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        jobs[name] = raw[start + match.start() : end]
    return raw[:start], jobs


def replace_once(raw: bytes, old: bytes, new: bytes) -> bytes:
    require(raw.count(old) == 1, "ambiguous authorized workflow transformation")
    return raw.replace(old, new, 1)


def expected_w04_job(entry: bytes) -> bytes:
    """Derive the complete approved job using only the frozen W03 service/action setup."""
    _, jobs = workflow_blocks(entry)
    block = jobs["w03-ai-loop-gate"]
    block = replace_once(block, b"  w03-ai-loop-gate:\n", b"  w04-investigation-gate:\n")
    block = replace_once(
        block, b"    name: W03 AI loop gate\n", b"    name: W04 investigation gate\n"
    )
    block = replace_once(block, b"    timeout-minutes: 15\n", b"    timeout-minutes: 30\n")
    prefix = block.split(b"      - name: Run frozen W03 semantic regression gate\n")
    require(len(prefix) == 2, "missing frozen W03 gate step")
    steps = b"""      - name: Verify W04 investigation gate contract
        run: uv run python scripts/ci/verify_w04_investigation_gate_contract.py

      - name: Run frozen W04 investigation semantic gate
        env:
          EXPECTED_HEAD: __SOURCE_HEAD__
        run: |
          uv run python scripts/ci/run_w04_investigation_gate.py \\
            --manifest docs/w04/checkpoints/c09/specs/c09_gate_manifest.json \\
            --expected-head "$EXPECTED_HEAD" \\
            --output-json "$RUNNER_TEMP/w04-c09-gate-summary.json"

      - name: Upload W04 investigation exact-SHA proof
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2
        with:
          name: w04-c09-gate-__SOURCE_HEAD__
          path: ${{ runner.temp }}/w04-c09-gate-summary.json
          if-no-files-found: error
          retention-days: 14

"""
    source_head = (
        b"${{ github.event_name == 'pull_request' && "
        b"github.event.pull_request.head.sha || github.sha }}"
    )
    return prefix[0] + steps.replace(b"__SOURCE_HEAD__", source_head)


def expected_verification(entry: bytes) -> bytes:
    _, jobs = workflow_blocks(entry)
    block = replace_once(
        jobs["verification-gate"],
        b", w03-ai-loop-gate]\n",
        b", w03-ai-loop-gate, w04-investigation-gate]\n",
    )
    for old, new in (
        (
            b"          W03_RESULT: ${{ needs['w03-ai-loop-gate'].result }}\n",
            b"          W03_RESULT: ${{ needs['w03-ai-loop-gate'].result }}\n"
            b"          W04_RESULT: ${{ needs['w04-investigation-gate'].result }}\n",
        ),
        (
            b'            test "$W03_RESULT" = skipped\n',
            b'            test "$W03_RESULT" = skipped\n            test "$W04_RESULT" = skipped\n',
        ),
        (
            b'            test "$W03_RESULT" = success\n',
            b'            test "$W03_RESULT" = success\n            test "$W04_RESULT" = success\n',
        ),
    ):
        block = replace_once(block, old, new)
    return block


def validate_workflow(entry: bytes, current: bytes) -> None:
    entry_prefix, before = workflow_blocks(entry)
    prefix, after = workflow_blocks(current)
    require(prefix == entry_prefix, "workflow trigger/header changed")
    require(set(after) == set(before) | {"w04-investigation-gate"}, "workflow job set changed")
    expected_order = list(before)
    expected_order.insert(expected_order.index("compose-smoke"), "w04-investigation-gate")
    require(list(after) == expected_order, "workflow job order changed")
    for name, block in before.items():
        require(
            after[name] == (expected_verification(entry) if name == "verification-gate" else block),
            f"unauthorized existing job delta: {name}",
        )
    require(after["w04-investigation-gate"] == expected_w04_job(entry), "W04 job contract delta")
    for pattern in (rb"uses: ([^\s]+)", rb"image: ([^\s]+)"):
        require(
            set(re.findall(pattern, current)) == set(re.findall(pattern, entry)),
            "new action pin or image",
        )


def workflow_guard(repo: Path = ROOT) -> None:
    path = ".github/workflows/ci.yml"
    for revision in (ENTRY, "HEAD"):
        require(
            git("ls-tree", "-r", "--name-only", revision, "--", ".github/workflows", repo=repo)
            .decode()
            .strip()
            == path,
            "hidden workflow in Git tree",
        )
    actual = sorted(
        p.relative_to(repo).as_posix()
        for p in (repo / ".github/workflows").rglob("*")
        if p.is_file()
    )
    require(actual == [path], "hidden workflow in checkout")
    # The written workflow retains exact LF Git bytes even on Windows.
    validate_workflow(git("show", ENTRY + ":" + path, repo=repo), (repo / path).read_bytes())


def source_units(source: str) -> tuple[list[str], dict[str, tuple[str, ast.AST]]]:
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    units: dict[str, tuple[str, ast.AST]] = {}
    order: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            key = node.name
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            require(
                all(isinstance(t, ast.Name) for t in targets), "unsupported assignment identity"
            )
            key = ",".join(cast(ast.Name, t).id for t in targets)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            key = "module-docstring"
        else:
            key = ast.dump(node, include_attributes=False)
        require(key not in units, "duplicate source-unit identity")
        decorators = getattr(node, "decorator_list", [])
        start = min([node.lineno, *(d.lineno for d in decorators)]) - 1
        units[key] = ("".join(lines[start : node.end_lineno]), node)
        order.append(key)
    return order, units


def validate_replay_sources(entry: str, current: str) -> None:
    old_order, old = source_units(entry)
    new_order, new = source_units(current)
    require(
        [k for k in old_order if k not in AUTHORIZED_REPLAY_SYMBOLS]
        == [k for k in new_order if k not in AUTHORIZED_REPLAY_SYMBOLS],
        "unauthorized replay unit addition/removal/reordering",
    )
    for key in set(old) | set(new):
        if key not in AUTHORIZED_REPLAY_SYMBOLS:
            require(
                key in old and key in new and old[key][0] == new[key][0],
                f"unauthorized replay source delta: {key}",
            )
        elif key in old and isinstance(old[key][1], (ast.FunctionDef, ast.AsyncFunctionDef)):
            require(
                key in new and type(new[key][1]) is type(old[key][1]),
                "authorized function selector removed/renamed",
            )
            for attribute in ("name", "args", "decorator_list", "returns", "type_params"):
                before, after = getattr(old[key][1], attribute), getattr(new[key][1], attribute)

                def structural(value: Any) -> Any:
                    if isinstance(value, ast.AST):
                        return ast.dump(value, include_attributes=False)
                    if isinstance(value, list):
                        return [structural(v) for v in value]
                    return value

                require(
                    structural(before) == structural(after),
                    f"authorized replay signature/decorator drift: {key}",
                )
    require(
        "C09_ENTRY_SHA" in new
        and ast.literal_eval(cast(ast.Assign, new["C09_ENTRY_SHA"][1]).value) == ENTRY,
        "C09 replay entry is not pinned",
    )
    require(
        "W04_C09_MANIFEST_CONTENT_SHA256" in new
        and ast.literal_eval(cast(ast.Assign, new["W04_C09_MANIFEST_CONTENT_SHA256"][1]).value)
        == CONTENT_DIGEST,
        "C09 replay manifest is not pinned",
    )


def replay_source_guard(repo: Path = ROOT) -> None:
    path = "tests/test_investigation_replay.py"
    # Universal-newline text is Git source text; spans include complete decorators and bodies.
    validate_replay_sources(
        git("show", ENTRY + ":" + path, repo=repo).decode(),
        (repo / path).read_text(encoding="utf-8"),
    )


def expected_meta_ci_unit(path: str, name: str, entry: str) -> str:
    """Only the literal Repair-01 additions; every prior assertion stays source-exact."""
    require(name in AUTHORIZED_META_CI_FUNCTIONS[path], "unauthorized meta-CI function")

    def change(old: str, new: str) -> None:
        nonlocal entry
        require(entry.count(old) == 1, "ambiguous Repair-01 source transformation")
        entry = entry.replace(old, new, 1)

    if name == "test_workflow_one_job_exact_schedule_source_manifest_and_environment":
        change(
            '        "w03-ai-loop-gate",\n',
            '        "w03-ai-loop-gate",\n        "w04-investigation-gate",\n',
        )
    else:
        change('"w03-ai-loop-gate]"', '"w03-ai-loop-gate, w04-investigation-gate]"')
    if name == "test_verification_runs_actual_shell_truth_table":
        change(
            "    assert \"W03_RESULT: ${{ needs['w03-ai-loop-gate'].result }}\" in verification\n",
            "    assert \"W03_RESULT: ${{ needs['w03-ai-loop-gate'].result }}\" in verification\n"
            "    assert \"W04_RESULT: ${{ "
            "needs['w04-investigation-gate'].result }}\" in verification\n",
        )
        change(
            '            "W03_RESULT": "skipped" if change == "P" else "success",\n',
            '            "W03_RESULT": "skipped" if change == "P" else "success",\n'
            '            "W04_RESULT": "skipped" if change == "P" else "success",\n',
        )
    return entry


def validate_meta_ci_sources(path: str, entry: str, current: str) -> None:
    old_order, old = source_units(entry)
    new_order, new = source_units(current)
    require(old_order == new_order, "meta-CI top-level unit/name/order drift")
    for name in old_order:
        expected = old[name][0]
        if name in AUTHORIZED_META_CI_FUNCTIONS[path]:
            require(isinstance(old[name][1], ast.FunctionDef), "meta-CI authority is function-only")
            expected = expected_meta_ci_unit(path, name, expected)
        require(new[name][0] == expected, f"unauthorized meta-CI source delta: {path}:{name}")


def meta_ci_source_guard(repo: Path = ROOT) -> None:
    for path in AUTHORIZED_META_CI_FUNCTIONS:
        validate_meta_ci_sources(
            path,
            git("show", ENTRY + ":" + path, repo=repo).decode(),
            (repo / path).read_text(encoding="utf-8"),
        )


def check_meta_ci_source_controls() -> int:
    for path, allowed in AUTHORIZED_META_CI_FUNCTIONS.items():
        entry = git("show", ENTRY + ":" + path).decode()
        current = (ROOT / path).read_text(encoding="utf-8")
        validate_meta_ci_sources(path, entry, current)
        _, units = source_units(current)
        unrelated = next(name for name in units if name.startswith("test_") and name not in allowed)
        unit = units[unrelated][0]
        authorized = sorted(allowed)[0]
        import_unit = next(
            text for text, node in units.values() if isinstance(node, (ast.Import, ast.ImportFrom))
        )
        mutations = (
            current.replace(unit, unit.rstrip() + "\n    raise AssertionError('damage')\n", 1),
            current + "\ndef test_unapproved_extra():\n    pass\n",
            current.replace("def " + authorized + "(", "def test_unapproved_rename(", 1),
            current.replace(import_unit, "import fractions\n", 1),
            current.replace(
                "def " + authorized + "(",
                '@pytest.mark.usefixtures("unapproved")\ndef ' + authorized + "(",
                1,
            ),
            current.replace("def " + authorized + "()", "def " + authorized + "(unapproved)", 1),
        )
        for damaged in mutations:
            require(damaged != current, "meta-CI adversary did not mutate source")
            rejected(
                "meta-CI source mutation",
                lambda damaged=damaged, path=path, entry=entry: validate_meta_ci_sources(
                    path, entry, damaged
                ),
            )
    return 12


def rejected(label: str, action: Any) -> None:
    try:
        action()
    except (ValueError, AssertionError, OSError, UnicodeError, subprocess.CalledProcessError):
        return
    raise ValueError(f"negative control admitted: {label}")


def check_manifest_controls(directory: Path) -> int:
    original = json.loads(MANIFEST.read_bytes())
    count = 0

    def reject_doc(label: str, value: Any) -> None:
        nonlocal count
        path = directory / "manifest.json"
        path.write_bytes(runner.canonical(value) + b"\n")
        rejected(label, lambda: runner.load_manifest(path))
        count += 1

    for level in ("root", "family", "target", "baseline"):
        for extra in (False, True):
            value = copy.deepcopy(original)
            obj = (
                value
                if level == "root"
                else value["baseline"]
                if level == "baseline"
                else value["families"][0]
                if level == "family"
                else value["families"][0]["targets"][0]
            )
            if extra:
                obj["extra"] = 1
            else:
                obj.pop(next(iter(obj)))
            reject_doc(level + str(extra), value)
    for key in (
        "schema_version",
        "gate_version",
        "checkpoint",
        "contract_entry_sha",
        "selector_semantics",
        "total_selectors",
        "total_cases",
    ):
        value = copy.deepcopy(original)
        value[key] = "wrong"
        reject_doc(key, value)
    for key in original["baseline"]:
        value = copy.deepcopy(original)
        value["baseline"][key] = "wrong"
        reject_doc("baseline-" + key, value)
    for damage in ("missing", "reordered", "unknown", "duplicate"):
        value = copy.deepcopy(original)
        if damage == "missing":
            value["families"].pop()
        elif damage == "reordered":
            value["families"].reverse()
        elif damage == "unknown":
            value["families"][0]["id"] = "unknown"
        else:
            value["families"][1] = copy.deepcopy(value["families"][0])
        reject_doc(damage, value)
    value = copy.deepcopy(original)
    value["families"][1]["targets"][0]["selector"] = value["families"][0]["targets"][0]["selector"]
    reject_doc("cross-family duplicate", value)
    for invalid in (0, -1, True, 1.5, "1"):
        rejected("positive count", lambda invalid=invalid: runner.positive_count(invalid))
        count += 1
        value = copy.deepcopy(original)
        value["families"][0]["targets"][0]["expected_cases"] = invalid
        reject_doc("invalid count", value)
    for selector in (
        "tests/test_x.py::*",
        "-k x",
        "-m integration",
        "--collect-only",
        "tests/test_x.py;echo x",
        "tests/test_x.py::TestClass::test_x",
        "tests/test_x.py::test_x[p]",
        "../tests/test_x.py::test_x",
        "tests/test_x.py::test_x && echo x",
    ):
        rejected("selector grammar", lambda selector=selector: runner.validate_selector(selector))
        count += 1
    for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b"{"):
        rejected("JSON parser", lambda raw=raw: runner.parse_json(raw))
        count += 1
    path = directory / "manifest.json"
    path.write_bytes(MANIFEST.read_bytes() + b" ")
    rejected("raw digest", lambda: runner.load_manifest(path))
    value = copy.deepcopy(original)
    value["families"][0]["targets"][0]["selector"] += "_renamed"
    reject_doc("renamed selector/content digest", value)
    return count + 1


def healthy_evidence(family: runner.Family) -> dict[str, Any]:
    nodes = [
        t.selector if t.expected_cases == 1 else t.selector + f"[{i}]"
        for t in family.targets
        for i in range(t.expected_cases)
    ]
    return {
        "schema_version": "w04-c09-pytest-evidence-v1",
        "collected": nodes,
        "collection_errors": 0,
        "deselected": 0,
        "exit_code": 0,
        "reports": [
            {"nodeid": n, "when": phase, "outcome": "passed", "wasxfail": False}
            for n in nodes
            for phase in ("setup", "call", "teardown")
        ],
    }


def check_runner_controls(directory: Path) -> int:
    manifest = runner.load_manifest(MANIFEST)
    family = manifest.families[3]
    healthy = healthy_evidence(family)
    runner.validate_evidence(family, healthy, 0)
    count = 0
    for field in ("collection_errors", "deselected", "exit_code"):
        damaged = copy.deepcopy(healthy)
        damaged[field] = 1
        rejected(field, lambda damaged=damaged: runner.validate_evidence(family, damaged, 0))
        count += 1
    for damage in (
        "partial",
        "duplicate",
        "missing",
        "unexpected",
        "no-call",
        "duplicate-call",
        "phase-order",
        "failure",
        "setup-error",
        "teardown-error",
        "skip",
        "xfail",
        "xpass",
    ):
        damaged = copy.deepcopy(healthy)
        if damage in {"partial", "missing"}:
            damaged["collected"].pop()
        elif damage == "duplicate":
            damaged["collected"][-1] = damaged["collected"][0]
        elif damage == "unexpected":
            damaged["collected"][-1] = "tests/test_wrong.py::test_wrong"
        elif damage == "no-call":
            damaged["reports"].pop(1)
        elif damage == "duplicate-call":
            damaged["reports"].insert(1, copy.deepcopy(damaged["reports"][1]))
        elif damage == "phase-order":
            damaged["reports"].reverse()
        else:
            index = 0 if damage == "setup-error" else 2 if damage == "teardown-error" else 1
            damaged["reports"][index]["outcome"] = "skipped" if damage == "skip" else "failed"
            if damage in {"xfail", "xpass"}:
                damaged["reports"][index]["outcome"] = "passed"
                damaged["reports"][index]["wasxfail"] = True
        rejected(damage, lambda damaged=damaged: runner.validate_evidence(family, damaged, 0))
        count += 1
    rejected("worker nonzero", lambda: runner.validate_evidence(family, healthy, 1))
    output = directory / "summary.json"
    output.write_bytes(b'{"overall":"PASS"}\n')
    rejected("wrong HEAD/stale PASS", lambda: runner.run_gate(MANIFEST, "0" * 40, output, ROOT))
    require(json.loads(output.read_bytes())["overall"] == "FAIL", "stale PASS survived failure")
    output.write_bytes(b'{"overall":"PASS"}\n')
    cli = subprocess.run(
        [
            sys.executable,
            "-B",
            str(Path(runner.__file__).resolve()),
            "--manifest",
            str(MANIFEST),
            "--expected-head",
            "0" * 40,
            "--output-json",
            str(output),
            "--repo",
            str(ROOT),
        ],
        capture_output=True,
        check=False,
    )
    require(
        cli.returncode != 0 and json.loads(output.read_bytes())["overall"] == "FAIL",
        "actual CLI admitted wrong HEAD or retained stale PASS",
    )
    rejected("repository output", lambda: runner.run_gate(MANIFEST, ENTRY, MANIFEST, ROOT))
    calls: list[str] = []

    def successful(f: runner.Family, repo: Path) -> dict[str, object]:
        calls.append(f.id)
        return {
            "id": f.id,
            "status": "PASS",
            "selectors": len(f.targets),
            "tests": f.expected_cases,
        }

    head = git("rev-parse", "HEAD").decode().strip()
    with (
        patch.object(runner, "execute_family", successful),
        contextlib.redirect_stdout(io.StringIO()),
    ):
        summary = runner.run_gate(MANIFEST, head, output, ROOT)
    require(calls == list(runner.FAMILY_IDS), "actual runner family order drift")
    raw = output.read_bytes()
    runner.validate_summary(raw, manifest, head)
    rejected(
        "family result order drift",
        lambda: runner.make_summary(
            manifest, head, list(reversed(cast(list[dict[str, object]], summary["families"])))
        ),
    )
    require(
        raw
        == json.dumps(summary, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        + b"\n",
        "summary is not canonical deterministic JSON",
    )
    for damage in ("seal-wrong", "seal-missing", "order", "timestamp", "count", "head"):
        value: dict[str, Any] = copy.deepcopy(summary)
        if damage == "seal-wrong":
            value["summary_sha256"] = "0" * 64
        elif damage == "seal-missing":
            value.pop("summary_sha256")
        elif damage == "order":
            value["families"].reverse()
        elif damage == "timestamp":
            value["timestamp"] = "unacceptable"
        elif damage == "count":
            value["total_tests"] = 80
        else:
            value["implementation_sha"] = "0" * 40
        rejected(
            damage,
            lambda value=value: runner.validate_summary(
                runner.canonical(value) + b"\n", manifest, head
            ),
        )
        count += 1
    rejected(
        "noncanonical summary order",
        lambda: runner.validate_summary(
            json.dumps(summary, indent=2).encode() + b"\n", manifest, head
        ),
    )
    launches: list[list[str]] = []

    def fake_process(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        launches.append(args)
        spec = runner.parse_family(
            json.loads(Path(args[args.index("--family-spec") + 1]).read_bytes())
        )
        require(
            args[args.index("--family-spec") + 2 :] == [t.selector for t in spec.targets],
            "worker received another family's selectors",
        )
        require(kwargs["env"]["PYTEST_ADDOPTS"] == "", "environment addopts not neutralized")
        path = Path(args[args.index("--worker-evidence") + 1])
        path.write_bytes(runner.canonical(healthy_evidence(spec)) + b"\n")
        return subprocess.CompletedProcess(args, 0)

    with (
        patch("run_w04_investigation_gate.subprocess.run", fake_process),
        contextlib.redirect_stdout(io.StringIO()),
    ):
        for f in manifest.families:
            runner.execute_family(f, ROOT)
    require(
        len(launches) == 9 and len({tuple(a) for a in launches}) == 9,
        "families executed in a shared pytest process",
    )
    return count + 9


def check_actual_workers(directory: Path) -> int:
    repo = directory / "worker-repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "pyproject.toml").write_text('[tool.pytest.ini_options]\naddopts="-k impossible"\n')
    (repo / "tests/test_controls.py").write_text(
        """import builtins
import pytest
@pytest.fixture
def setup_error():
    raise RuntimeError("setup")
@pytest.fixture
def teardown_error():
    yield
    raise RuntimeError("teardown")
def test_isolation():
    assert not hasattr(builtins, "_w04_c09_control_state")
    builtins._w04_c09_control_state = True
def test_failure():
    assert False
def test_setup(setup_error):
    pass
def test_teardown(teardown_error):
    pass
def test_skip():
    pytest.skip("control")
@pytest.mark.xfail(reason="control")
def test_xfail():
    assert False
@pytest.mark.xfail(reason="")
def test_xpass():
    pass
@pytest.mark.parametrize("value", [1,2])
def test_parameter(value):
    assert value > 0
""",
        encoding="utf-8",
    )

    def family(name: str, cases: int = 1) -> runner.Family:
        return runner.Family(
            "CONTROL", cases, (runner.Target("tests/test_controls.py::test_" + name, cases),)
        )

    with contextlib.redirect_stdout(io.StringIO()):
        runner.execute_family(family("isolation"), repo)
        runner.execute_family(family("isolation"), repo)
        runner.execute_family(family("parameter", 2), repo)
        for name in (
            "failure",
            "setup",
            "teardown",
            "skip",
            "xfail",
            "xpass",
            "renamed",
            "parameter",
        ):
            rejected(
                "real worker " + name, lambda name=name: runner.execute_family(family(name), repo)
            )
    (repo / "tests/test_broken.py").write_text("def broken(:\n", encoding="utf-8")
    rejected(
        "actual collection error",
        lambda: runner.execute_family(
            runner.Family("CONTROL", 1, (runner.Target("tests/test_broken.py::test_broken", 1),)),
            repo,
        ),
    )
    return 12


def bash_path() -> str:
    if os.name == "nt":
        git_exe = shutil.which("git")
        require(git_exe is not None, "Git Bash unavailable")
        return str(Path(cast(str, git_exe)).resolve().parents[1] / "bin/bash.exe")
    executable = shutil.which("bash")
    require(executable is not None, "Bash unavailable")
    return cast(str, executable)


def check_workflow_truth(current: bytes) -> int:
    _, jobs = workflow_blocks(current)
    block = jobs["verification-gate"]
    require(block.count(b"        run: |\n") == 1, "ambiguous verification shell")
    script = "\n".join(
        line[10:].decode() for line in block.split(b"        run: |\n")[1].splitlines()
    )
    fields = [
        "CLASS_RESULT",
        "STATIC_RESULT",
        "INTEGRATION_RESULT",
        "NONINT_RESULT",
        "QUALITY_RESULT",
        "COMPOSE_RESULT",
        "W03_RESULT",
        "W04_RESULT",
        "PUBLICATION_RESULT",
    ]
    count = 0

    def execute(env: dict[str, str], expected: bool) -> None:
        nonlocal count
        result = subprocess.run(
            [bash_path(), "--noprofile", "--norc", "-e", "-c", script],
            env=dict(os.environ, **env),
            capture_output=True,
            check=False,
        )
        require((result.returncode == 0) == expected, "actual Verification truth table failed")
        count += 1

    for change_class in ("P", "C", "I", "F", "UNKNOWN"):
        env = {field: "success" for field in fields}
        env["CHANGE_CLASS"] = change_class
        env["PUBLICATION_RESULT"] = "success" if change_class == "P" else "skipped"
        if change_class == "P":
            env.update({field: "skipped" for field in fields[1:-1]})
        execute(env, True)
        for field in fields:
            for status in ("success", "skipped", "failure", "cancelled"):
                if status != env[field]:
                    execute(env | {field: status}, False)
        for w03, w04 in itertools.product(("success", "skipped", "failure", "cancelled"), repeat=2):
            execute(
                env | {"W03_RESULT": w03, "W04_RESULT": w04},
                w03 == env["W03_RESULT"] and w04 == env["W04_RESULT"],
            )
    for invalid in ("", "wrong", "p"):
        execute(env | {"CHANGE_CLASS": invalid}, False)
    return count


def check_source_and_workflow_controls() -> int:
    entry = git("show", ENTRY + ":.github/workflows/ci.yml")
    current = (ROOT / ".github/workflows/ci.yml").read_bytes()
    validate_workflow(entry, current)
    mutations = [
        current.replace(b"timeout-minutes: 65", b"timeout-minutes: 66", 1),
        current.replace(b"timeout-minutes: 30", b"timeout-minutes: 31", 1),
        current.replace(b"max-parallel: 7", b"max-parallel: 8", 1),
        current.replace(b"fail-fast: false", b"fail-fast: true", 1),
        current.replace(b"shard: [0, 1, 2, 3, 4, 5, 6]", b"shard: [0, 1, 2]", 1),
        current.replace(b"actions/checkout@", b"actions/checkout@0", 1),
        current.replace(b"timeout-minutes: 15", b"timeout-minutes: 16", 1),
        current.replace(b"name: W04 investigation gate", b"name: W04 other gate", 1),
        current.replace(b"  w04-investigation-gate:\n", b"  other-gate:\n", 1),
        current + b"\n  hidden-job:\n    runs-on: ubuntu-latest\n",
        current.replace(b"  w04-investigation-gate:\n", b"  w04-investigation-gate:\n" * 2, 1),
        current.replace(b'            test "$W04_RESULT" = success\n', b"", 1),
        current.replace(b'            test "$W04_RESULT" = skipped\n', b"", 1),
        b"# changed trigger\n" + current,
    ]
    for workflow_value in mutations:
        rejected(
            "workflow mutation",
            lambda workflow_value=workflow_value: validate_workflow(entry, workflow_value),
        )
    path = "tests/test_investigation_replay.py"
    original = git("show", ENTRY + ":" + path).decode()
    source = (ROOT / path).read_text(encoding="utf-8")
    validate_replay_sources(original, source)
    for value in (
        source + "\ndef test_extra():\n    pass\n",
        source.replace("import ast\n", "import ast as changed\n", 1),
        source.replace('"""W04-C08 R01-R46:', '"""Changed R01-R46:', 1),
        source.replace('        "run_head",', '        "changed_damage",', 1),
        source.replace('    "run_head",', '    "changed_damage",', 1),
        source.replace(
            "def test_r46_stage_b_exact_sha_full_native_ci(", "def test_renamed_native_ci(", 1
        ),
        source.replace("def _error(", "def _unauthorized_error(", 1),
    ):
        if value != source:
            rejected(
                "C08 source delta", lambda value=value: validate_replay_sources(original, value)
            )
    _, units = source_units(source)
    victim = next(k for k in units if k.startswith("test_r01"))
    unit = units[victim][0]
    value = source.replace(unit, unit.rstrip() + "\n    raise AssertionError('damage')\n", 1)
    rejected("R01 body delta", lambda: validate_replay_sources(original, value))
    return len(mutations) + 7


def check_native_metadata_controls() -> int:
    sys.path.insert(0, str(ROOT / "tests"))
    import test_investigation_replay as replay

    head = "a" * 40
    value = replay._native_metadata_fixture(head)
    replay._check_native_metadata(value, head)
    count = 0
    for field in (
        "implementation_sha",
        "gate_version",
        "overall",
        "total_families",
        "total_selectors",
        "total_tests",
        "manifest_content_sha256",
        "summary_sha256",
    ):
        damaged = copy.deepcopy(value)
        damaged["w04"][field] = "wrong"
        rejected(
            "W04 native " + field,
            lambda damaged=damaged: replay._check_native_metadata(damaged, head),
        )
        count += 1
    for damage in ("order", "count", "missing-seal", "extra"):
        damaged = copy.deepcopy(value)
        summary = damaged["w04"]
        if damage == "order":
            summary["families"].reverse()
        elif damage == "count":
            summary["families"][0]["tests"] = 7
        elif damage == "missing-seal":
            summary.pop("summary_sha256")
        else:
            summary["extra"] = 1
        if damage != "missing-seal":
            payload = {k: v for k, v in summary.items() if k != "summary_sha256"}
            summary["summary_sha256"] = hashlib.sha256(runner.canonical(payload)).hexdigest()
        rejected(
            "W04 native " + damage,
            lambda damaged=damaged: replay._check_native_metadata(damaged, head),
        )
        count += 1
    return count


def validate_changed_paths(
    changed: set[str], subject: str = "", publication_delta: set[str] | None = None
) -> None:
    allowed = set(STAGE_A)
    if changed & set(STAGE_B):
        require(
            subject == "docs(w04-c09): publish regression-hardening proof"
            and publication_delta == set(STAGE_B),
            "Stage-B report cannot be admitted into Stage A",
        )
        allowed.update(STAGE_B)
    require(changed <= allowed, "W04_C09_SCOPE_VIOLATION")


def verify_collection_and_scope() -> dict[str, object]:
    paths = json.loads((ROOT / "docs/w04/checkpoints/c09/specs/authorized_paths.json").read_bytes())
    require(
        paths
        == {
            "schema_version": "w04-c09-authorized-paths-v1",
            "checkpoint": "W04-C09",
            "task_version": "V1.1",
            "repair_01_sha256": REPAIR_01_SHA256,
            "stage_a": list(STAGE_A),
            "stage_b": list(STAGE_B),
        },
        "authorized-path sets drift",
    )
    changed = set(git("diff", "--name-only", ENTRY, "--").decode().splitlines())
    changed.update(git("ls-files", "--others", "--exclude-standard").decode().splitlines())
    validate_changed_paths(
        changed,
        git("log", "-1", "--pretty=%s").decode().strip(),
        set(git("diff", "--name-only", "HEAD^", "HEAD").decode().splitlines()),
    )
    protected = (
        "src",
        "migrations",
        "apps",
        "pyproject.toml",
        "uv.lock",
        "docker-compose.yml",
        "docs/w03",
        "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json",
        "docs/w04/devctrl",
        "docs/w04/devctrl-02",
        "docs/w04/devctrl-03",
        *(f"docs/w04/checkpoints/c{i:02}" for i in range(1, 9)),
        "scripts/ci/classify_change.py",
        "scripts/ci/verify_publication.py",
        "scripts/ci/plan_non_integration_shards.py",
        "scripts/ci/pytest_outcome_receipt.py",
        "scripts/ci/run_non_integration_shard.py",
        "scripts/ci/verify_non_integration_shards.py",
        "scripts/ci/run_w03_ai_loop_gate.py",
        "scripts/ci/verify_w04_source_evolution.py",
    )
    require(not git("diff", ENTRY, "--", *protected), "W04_C09_PROTECTED_OBJECT_DRIFT")
    raw = (ROOT / "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json").read_bytes()
    require(
        hashlib.sha256(raw).hexdigest()
        == "d22a12306f8fe98952b9e35a5f166f29fee968c9aedcff27511da59889c20c2d",
        "source manifest byte drift",
    )
    source = json.loads(raw)
    require(
        [c["checkpoint"] for c in source["checkpoints"]] == [f"W04-C{i:02}" for i in range(1, 9)]
        and all(c["state"] == "CLOSED" for c in source["checkpoints"]),
        "source lifecycle drift",
    )
    for c in source["checkpoints"]:
        for file in c["files"]:
            require(
                git("rev-parse", "HEAD:" + file["path"]).decode().strip() == file["blob_oid"],
                "closed source blob drift",
            )
    nodes = planner.collect_nodes(planner.MARKER)
    files = sorted({n.split("::")[0] for n in nodes})
    require(
        len(nodes) == 2997
        and planner.digest(nodes)
        == "9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a",
        "W04_C09_NODESET_DRIFT",
    )
    require(
        len(files) == 63
        and planner.digest(files)
        == "890fdd5c30c7e2a1e90da8cb8b7123937d3356f1d519f82dff4a941f13659fd7",
        "DEVCTRL-03 file drift",
    )
    head = git("rev-parse", "HEAD").decode().strip()
    weights = planner.read_json(planner.WEIGHTS)
    plan = planner.build_plan(nodes, weights, planner.read_json(planner.BASELINE), head)
    require(
        plan["weights_sha256"] == "a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851"
        and plan["schema_version"] == "w04-devctrl03-non-integration-plan-v1"
        and len(plan["shards"]) == 7,
        "DEVCTRL-03 active plan drift",
    )
    all_nodes = nodes + planner.collect_nodes("integration")
    manifest = runner.load_manifest(MANIFEST)
    for family in manifest.families:
        selected = [
            n
            for n in all_nodes
            if any(n == t.selector or n.startswith(t.selector + "[") for t in family.targets)
        ]
        runner.validate_collection(family, selected)
    return {
        "nodes": 2997,
        "files": 63,
        "node_digest": planner.digest(nodes),
        "weights_digest": plan["weights_sha256"],
        "shards": 7,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        raw = MANIFEST.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == RAW_DIGEST, "manifest raw identity")
        require(
            hashlib.sha256(runner.canonical(json.loads(raw))).hexdigest() == CONTENT_DIGEST,
            "manifest content identity",
        )
        workflow_guard()
        replay_source_guard()
        meta_ci_source_guard()
        with tempfile.TemporaryDirectory(prefix="w04-c09-contract-") as temporary:
            directory = Path(temporary)
            controls = check_manifest_controls(directory) + check_runner_controls(directory)
            controls += check_actual_workers(directory)
        controls += check_source_and_workflow_controls() + check_native_metadata_controls()
        controls += check_meta_ci_source_controls()
        validate_changed_paths(set(STAGE_A))
        rejected(
            "fifteenth Stage-A report path",
            lambda: validate_changed_paths(set(STAGE_A) | set(STAGE_B)),
        )
        rejected(
            "unauthorized path",
            lambda: validate_changed_paths(set(STAGE_A) | {"src/unauthorized.py"}),
        )
        rejected(
            "mixed publication delta",
            lambda: validate_changed_paths(
                set(STAGE_A) | set(STAGE_B),
                "docs(w04-c09): publish regression-hardening proof",
                set(STAGE_B) | {STAGE_A[0]},
            ),
        )
        controls += 3
        truths = check_workflow_truth((ROOT / ".github/workflows/ci.yml").read_bytes())
        collection = verify_collection_and_scope()
        print(
            json.dumps(
                {
                    "gate_contract": "PASS",
                    "c08_replay_source_delta_guard": "PASS",
                    "c09_meta_ci_delta_guard": "PASS",
                    "family_subprocess_isolation": "PASS",
                    "adversarial_controls": controls,
                    "actual_shell_truth_cases": truths,
                    "collection": collection,
                },
                sort_keys=True,
            )
        )
    except (OSError, ValueError, AssertionError, subprocess.CalledProcessError) as error:
        print(f"W04_C09_GATE_CONTRACT_FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
