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
CLOSEOUT_STAGE_A_SHA = "3cd8023dbe79ca8360a3075dd3b169921e31f7a5"
CLOSEOUT_REVIEW_READY_SHA = "f4c528e1daf86aa1a010bce82665e43c55560384"
CLOSEOUT_VERIFIER_PATH = "scripts/ci/verify_w04_investigation_gate_contract.py"
CLOSEOUT_PREP_SUBJECT = "ci(w04-c09): admit bounded closeout lifecycle"
CLOSEOUT_FINAL_SUBJECT = "docs(w04-c09): close investigation regression gate"
CLOSEOUT_FINAL_PATHS = (
    "docs/w04/checkpoints/c09/W04_C09_GPT_INDEPENDENT_REVIEW_R1.md",
    "docs/w04/checkpoints/c09/W04_C09_HUMAN_ACCEPTANCE.md",
    "docs/w04/checkpoints/c09/W04_C09_CLOSEOUT_AUTHORIZATION.md",
    "docs/w04/checkpoints/c09/W04_C09_CLOSEOUT_CONTEXT_LOCK.md",
    "docs/w04/checkpoints/c09/W04_C09_FINAL_CLOSEOUT_REPORT.md",
)


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


def validate_closeout_lifecycle(
    history: list[dict[str, Any]], working: set[str], changed: set[str]
) -> str:
    """Admit only the two immutable anchors and their single Prep / Final children."""
    require(1 <= len(history) <= 4, "extra post-REVIEW_READY commit")
    for record in history:
        require(set(record) == {"sha", "parents", "subject", "delta"}, "lifecycle record shape")
        require(
            re.fullmatch(r"[0-9a-f]{40}", record["sha"]) is not None
            and record["sha"] != "0" * 40,
            "invalid lifecycle SHA",
        )
    require(len({r["sha"] for r in history}) == len(history), "duplicate lifecycle SHA")
    first = history[0]
    require(
        first["sha"] == CLOSEOUT_STAGE_A_SHA
        and first["parents"] == [ENTRY]
        and first["subject"] == "ci(w04-c09): add investigation regression gate"
        and set(first["delta"]) == set(STAGE_A),
        "Stage-A immutable anchor drift",
    )
    state, expected = "STAGE_A", set(STAGE_A)
    if len(history) >= 2:
        publication = history[1]
        require(
            publication["sha"] == CLOSEOUT_REVIEW_READY_SHA
            and publication["parents"] == [CLOSEOUT_STAGE_A_SHA]
            and publication["subject"] == "docs(w04-c09): publish regression-hardening proof"
            and publication["delta"] == {STAGE_B[0]: "A"},
            "REVIEW_READY immutable publication anchor drift",
        )
        state = "REVIEW_READY"
        expected.update(STAGE_B)
    if len(history) >= 3:
        prep = history[2]
        require(
            prep["parents"] == [CLOSEOUT_REVIEW_READY_SHA]
            and prep["subject"] == CLOSEOUT_PREP_SUBJECT
            and prep["delta"] == {CLOSEOUT_VERIFIER_PATH: "M"},
            "invalid exact Closeout-Prep-01 parent/subject/delta",
        )
        state = "CLOSEOUT_PREP_01"
    if len(history) == 4:
        final = history[3]
        require(
            final["parents"] == [history[2]["sha"]]
            and final["subject"] == CLOSEOUT_FINAL_SUBJECT
            and final["delta"] == {path: "A" for path in CLOSEOUT_FINAL_PATHS},
            "invalid exact final-closeout parent/subject/delta",
        )
        state = "FINAL_CLOSEOUT"
        expected.update(CLOSEOUT_FINAL_PATHS)
    require(changed == expected, "closeout cumulative path-set drift")
    # The sole uncommitted development candidate is the authorized verifier at REVIEW_READY.
    require(
        working <= {CLOSEOUT_VERIFIER_PATH} if state == "REVIEW_READY" else not working,
        "unauthorized working-tree lifecycle delta",
    )
    return state


def closeout_lifecycle_guard(changed: set[str], repo: Path = ROOT) -> str:
    head = git("rev-parse", "HEAD", repo=repo).decode().strip()
    revisions = [CLOSEOUT_STAGE_A_SHA]
    if head != CLOSEOUT_STAGE_A_SHA:
        git("merge-base", "--is-ancestor", CLOSEOUT_REVIEW_READY_SHA, head, repo=repo)
        revisions.append(CLOSEOUT_REVIEW_READY_SHA)
        revisions.extend(
            git("rev-list", "--reverse", CLOSEOUT_REVIEW_READY_SHA + ".." + head, repo=repo)
            .decode()
            .splitlines()
        )
    require(revisions[-1] == head, "lifecycle HEAD mismatch")
    history: list[dict[str, Any]] = []
    for revision in revisions:
        parents = git("rev-list", "--parents", "-n", "1", revision, repo=repo).decode().split()
        require(len(parents) == 2 and parents[0] == revision, "lifecycle merge/root forbidden")
        delta: dict[str, str] = {}
        for row in (
            git("diff", "--name-status", "--no-renames", parents[1], revision, repo=repo)
            .decode()
            .splitlines()
        ):
            status, path = row.split("\t")
            require(path not in delta, "duplicate lifecycle delta path")
            delta[path] = status
        history.append(
            {
                "sha": revision,
                "parents": parents[1:],
                "subject": git("show", "-s", "--format=%s", revision, repo=repo).decode().strip(),
                "delta": delta,
            }
        )
    working = set(git("diff", "--name-only", "HEAD", "--", repo=repo).decode().splitlines())
    working.update(
        git("ls-files", "--others", "--exclude-standard", repo=repo).decode().splitlines()
    )
    return validate_closeout_lifecycle(history, working, changed)


def validate_verifier_sources(review_ready: str, current: str) -> None:
    """Preserve every legacy source span except two exact lifecycle call-site edits."""
    if current == review_ready:
        return
    old_order, old = source_units(review_ready)
    new_order, new = source_units(current)
    additions = {
        "CLOSEOUT_STAGE_A_SHA",
        "CLOSEOUT_REVIEW_READY_SHA",
        "CLOSEOUT_VERIFIER_PATH",
        "CLOSEOUT_PREP_SUBJECT",
        "CLOSEOUT_FINAL_SUBJECT",
        "CLOSEOUT_FINAL_PATHS",
        "validate_closeout_lifecycle",
        "closeout_lifecycle_guard",
        "validate_verifier_sources",
        "verifier_source_guard",
        "check_closeout_lifecycle_controls",
    }
    require(set(new) - set(old) == additions, "unauthorized verifier top-level addition/removal")
    require(
        [name for name in new_order if name not in additions] == old_order,
        "verifier legacy unit identity/order drift",
    )
    for name in old_order:
        expected = old[name][0].encode()
        if name == "verify_collection_and_scope":
            expected = replace_once(
                expected,
                b"    validate_changed_paths(\n"
                b"        changed,\n"
                b'        git("log", "-1", "--pretty=%s").decode().strip(),\n'
                b'        set(git("diff", "--name-only", "HEAD^", "HEAD").decode().splitlines()),\n'
                b"    )\n",
                b"    lifecycle = closeout_lifecycle_guard(changed)\n",
            )
            expected = replace_once(
                expected,
                b'        "shards": 7,\n',
                b'        "shards": 7,\n        "lifecycle": lifecycle,\n',
            )
        elif name == "main":
            expected = replace_once(
                expected,
                b"        workflow_guard()\n",
                b"        verifier_source_guard()\n        workflow_guard()\n",
            )
            expected = replace_once(
                expected,
                b"        controls += 3\n",
                b"        controls += 3\n        controls += check_closeout_lifecycle_controls()\n",
            )
            expected = replace_once(
                expected,
                b'                    "family_subprocess_isolation": "PASS",\n',
                b'                    "family_subprocess_isolation": "PASS",\n'
                b'                    "verifier_self_source_delta_guard": "PASS",\n'
                b'                    "closeout_lifecycle": collection["lifecycle"],\n',
            )
        require(new[name][0].encode() == expected, f"unauthorized verifier source delta: {name}")
    constants = {
        "CLOSEOUT_STAGE_A_SHA": "3cd8023dbe79ca8360a3075dd3b169921e31f7a5",
        "CLOSEOUT_REVIEW_READY_SHA": "f4c528e1daf86aa1a010bce82665e43c55560384",
        "CLOSEOUT_VERIFIER_PATH": "scripts/ci/verify_w04_investigation_gate_contract.py",
        "CLOSEOUT_PREP_SUBJECT": "ci(w04-c09): admit bounded closeout lifecycle",
        "CLOSEOUT_FINAL_SUBJECT": "docs(w04-c09): close investigation regression gate",
        "CLOSEOUT_FINAL_PATHS": (
            "docs/w04/checkpoints/c09/W04_C09_GPT_INDEPENDENT_REVIEW_R1.md",
            "docs/w04/checkpoints/c09/W04_C09_HUMAN_ACCEPTANCE.md",
            "docs/w04/checkpoints/c09/W04_C09_CLOSEOUT_AUTHORIZATION.md",
            "docs/w04/checkpoints/c09/W04_C09_CLOSEOUT_CONTEXT_LOCK.md",
            "docs/w04/checkpoints/c09/W04_C09_FINAL_CLOSEOUT_REPORT.md",
        ),
    }
    for name, value in constants.items():
        node = new[name][1]
        require(isinstance(node, ast.Assign), "lifecycle constant declaration drift")
        require(ast.literal_eval(cast(ast.Assign, node).value) == value, "lifecycle constant drift")


def verifier_source_guard(repo: Path = ROOT) -> None:
    current = (repo / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")
    validate_verifier_sources(
        git("show", CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo).decode(),
        current,
    )
    subject = git("show", "-s", "--format=%s", "HEAD", repo=repo).decode().strip()
    if subject == CLOSEOUT_FINAL_SUBJECT:
        require(
            git("show", "HEAD^:" + CLOSEOUT_VERIFIER_PATH, repo=repo).decode() == current,
            "accepted Prep verifier must remain frozen in Final",
        )


def check_closeout_lifecycle_controls() -> int:
    stage_a: dict[str, Any] = {
        "sha": CLOSEOUT_STAGE_A_SHA,
        "parents": [ENTRY],
        "subject": "ci(w04-c09): add investigation regression gate",
        "delta": dict.fromkeys(STAGE_A, "A"),
    }
    publication: dict[str, Any] = {
        "sha": CLOSEOUT_REVIEW_READY_SHA,
        "parents": [CLOSEOUT_STAGE_A_SHA],
        "subject": "docs(w04-c09): publish regression-hardening proof",
        "delta": {STAGE_B[0]: "A"},
    }
    prep: dict[str, Any] = {
        "sha": "a" * 40,
        "parents": [CLOSEOUT_REVIEW_READY_SHA],
        "subject": CLOSEOUT_PREP_SUBJECT,
        "delta": {CLOSEOUT_VERIFIER_PATH: "M"},
    }
    final: dict[str, Any] = {
        "sha": "b" * 40,
        "parents": [prep["sha"]],
        "subject": CLOSEOUT_FINAL_SUBJECT,
        "delta": dict.fromkeys(CLOSEOUT_FINAL_PATHS, "A"),
    }
    history = [stage_a, publication, prep, final]
    base = set(STAGE_A) | set(STAGE_B)
    complete = base | set(CLOSEOUT_FINAL_PATHS)
    for size, state in enumerate(
        ("STAGE_A", "REVIEW_READY", "CLOSEOUT_PREP_01", "FINAL_CLOSEOUT"), start=1
    ):
        changed = set(STAGE_A) if size == 1 else complete if size == 4 else base
        require(validate_closeout_lifecycle(history[:size], set(), changed) == state, "valid state")
    require(
        validate_closeout_lifecycle(history[:2], {CLOSEOUT_VERIFIER_PATH}, base) == "REVIEW_READY",
        "one-file local Prep candidate",
    )
    mutations: list[tuple[str, list[dict[str, Any]], set[str], set[str]]] = []
    for label, index, field, value in (
        ("wrong Prep parent", 2, "parents", [CLOSEOUT_STAGE_A_SHA]),
        ("wrong Prep subject", 2, "subject", "ci: unauthorized"),
        ("extra Prep path", 2, "delta", {CLOSEOUT_VERIFIER_PATH: "M", STAGE_A[0]: "M"}),
        ("missing final document", 3, "delta", dict.fromkeys(CLOSEOUT_FINAL_PATHS[:-1], "A")),
        (
            "extra final document",
            3,
            "delta",
            {**dict.fromkeys(CLOSEOUT_FINAL_PATHS, "A"), "docs/w04/extra.md": "A"},
        ),
        (
            "mixed final delta",
            3,
            "delta",
            {**dict.fromkeys(CLOSEOUT_FINAL_PATHS, "A"), CLOSEOUT_VERIFIER_PATH: "M"},
        ),
        ("wrong final subject", 3, "subject", "docs: unauthorized"),
        ("final without exact Prep parent", 3, "parents", [CLOSEOUT_REVIEW_READY_SHA]),
        ("merge Prep", 2, "parents", [CLOSEOUT_REVIEW_READY_SHA, CLOSEOUT_STAGE_A_SHA]),
        ("non-new final document", 3, "delta", dict.fromkeys(CLOSEOUT_FINAL_PATHS, "M")),
    ):
        damaged = copy.deepcopy(history)
        damaged[index][field] = value
        mutations.append((label, damaged, set(), complete))
    mutations.extend(
        (
            ("extra post-REVIEW_READY commit", [*history, copy.deepcopy(final)], set(), complete),
            ("missing Prep state", [stage_a, publication, final], set(), complete),
            ("unauthorized working delta", history, {STAGE_A[0]}, complete),
            ("wrong cumulative paths", history, set(), complete | {"src/extra.py"}),
        )
    )
    for label, damaged, working, changed in mutations:
        rejected(
            label,
            lambda damaged=damaged, working=working, changed=changed: validate_closeout_lifecycle(
                damaged, working, changed
            ),
        )
    original = git("show", CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    current = (ROOT / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")
    validate_verifier_sources(original, current)
    order, units = source_units(current)
    mains = [
        n for n in ast.parse(current).body if isinstance(n, ast.FunctionDef) and n.name == "main"
    ]
    require(len(mains) == 1 and "main" in units, "exactly one real top-level main required")
    lines = current.splitlines(keepends=True)

    def damage_unit(name: str, mutate: Any) -> str:
        unit, parsed = units[name]
        node = cast(ast.stmt, parsed)
        changed_node = copy.deepcopy(node)
        mutate(changed_node)
        replacement = ast.unparse(ast.fix_missing_locations(changed_node)) + "\n"
        decorators = getattr(node, "decorator_list", [])
        start = min([node.lineno, *(d.lineno for d in decorators)]) - 1
        require(node.end_lineno is not None, "missing source-unit end span")
        end = node.end_lineno
        require("".join(lines[start:end]) == unit, "source-unit span mismatch")
        candidate = "".join(lines[:start]) + replacement + "".join(lines[end:])
        replacement_order, _ = source_units(replacement)
        require(len(replacement_order) == 1, "adversary must replace exactly one source unit")
        target = replacement_order[0]
        after_order, after = source_units(candidate)
        require(
            [key for key in after_order if key != target] == [key for key in order if key != name],
            "adversary changed unrelated source-unit identities/order",
        )
        require(
            all(after[key][0] == units[key][0] for key in order if key != name),
            "adversary changed an unrelated source span",
        )
        require(after[target][0] != unit, "adversary did not change the target source unit")
        if name == "main":
            require(target == "main", "main adversary must preserve the actual function identity")
        return candidate

    def remove_main_workflow_call(node: ast.FunctionDef) -> None:
        matches: list[tuple[list[ast.stmt], ast.stmt]] = []
        for parent in ast.walk(node):
            body = getattr(parent, "body", None)
            if not isinstance(body, list):
                continue
            for statement in body:
                if (
                    isinstance(statement, ast.Expr)
                    and isinstance(statement.value, ast.Call)
                    and isinstance(statement.value.func, ast.Name)
                    and statement.value.func.id == "workflow_guard"
                ):
                    matches.append((body, statement))
        require(len(matches) == 1, "exactly one real main workflow_guard call required")
        body, statement = matches[0]
        body.remove(statement)

    imports = [
        key
        for key, (_, node) in units.items()
        if isinstance(node, ast.Import) and any(alias.name == "ast" for alias in node.names)
    ]
    require(len(imports) == 1, "exactly one structural ast import required")
    source_mutations = (
        damage_unit("require", lambda node: node.body.append(ast.Raise(exc=None, cause=None))),
        current + "\ndef unauthorized_verifier_unit():\n    pass\n",
        damage_unit(imports[0], lambda node: setattr(node.names[0], "asname", "unauthorized")),
        damage_unit("main", lambda node: node.args.args.append(ast.arg(arg="unauthorized"))),
        damage_unit("main", lambda node: node.decorator_list.append(ast.Name(id="unauthorized"))),
        damage_unit("workflow_guard", lambda node: setattr(node, "name", "renamed_workflow_guard")),
        damage_unit("main", remove_main_workflow_call),
        damage_unit(
            "CLOSEOUT_STAGE_A_SHA", lambda node: setattr(node, "value", ast.Constant("c" * 40))
        ),
    )
    for damaged_source in source_mutations:
        require(damaged_source != current, "verifier source adversary did not mutate")
        rejected(
            "unauthorized verifier top-level mutation",
            lambda damaged_source=damaged_source: validate_verifier_sources(
                original, damaged_source
            ),
        )
    return len(mutations) + len(source_mutations)


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
    lifecycle = closeout_lifecycle_guard(changed)
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
        "lifecycle": lifecycle,
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
        verifier_source_guard()
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
        controls += check_closeout_lifecycle_controls()
        truths = check_workflow_truth((ROOT / ".github/workflows/ci.yml").read_bytes())
        collection = verify_collection_and_scope()
        print(
            json.dumps(
                {
                    "gate_contract": "PASS",
                    "c08_replay_source_delta_guard": "PASS",
                    "c09_meta_ci_delta_guard": "PASS",
                    "family_subprocess_isolation": "PASS",
                    "verifier_self_source_delta_guard": "PASS",
                    "closeout_lifecycle": collection["lifecycle"],
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
