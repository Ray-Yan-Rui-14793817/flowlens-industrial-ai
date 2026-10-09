"""C09 proof contract: real pytest negative cases and frozen workflow enforcement."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/ci"))

import run_w03_ai_loop_gate as gate  # noqa: E402

MANIFEST = ROOT / "docs/w03/checkpoints/c09/specs/c09_gate_manifest.json"
WORKFLOW = ROOT / ".github/workflows/ci.yml"


def manifest_document() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(MANIFEST.read_bytes()))


def write_manifest(tmp_path: Path, document: dict[str, Any]) -> Path:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout


def jobs(content: str) -> dict[str, str]:
    content = content.split("jobs:\n", 1)[1]
    starts = list(re.finditer(r"^  ([a-z][a-z0-9-]+):\n", content, re.MULTILINE))
    return {
        match[1]: content[
            match.start() : starts[index + 1].start() if index + 1 < len(starts) else len(content)
        ]
        for index, match in enumerate(starts)
    }


def workflow_jobs() -> dict[str, str]:
    return jobs(WORKFLOW.read_text(encoding="utf-8"))


def workflow_steps(content: str) -> dict[str, str]:
    starts = list(re.finditer(r"^      - name: ([^\n]+)\n", content, re.MULTILINE))
    return {
        match[1]: content[
            match.start() : starts[index + 1].start() if index + 1 < len(starts) else len(content)
        ]
        for index, match in enumerate(starts)
    }


def fixture_repo(tmp_path: Path, source: str) -> tuple[Path, gate.Family]:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests/test_fixture.py").write_text(textwrap.dedent(source), encoding="utf-8")
    return repo, gate.Family("fixture", 1, (gate.Target("tests/test_fixture.py::test_case", 1),))


def valid_evidence(family: gate.Family) -> dict[str, Any]:
    nodes = [
        target.selector if target.expected_cases == 1 else f"{target.selector}[{index}]"
        for target in family.targets
        for index in range(target.expected_cases)
    ]
    return {
        "schema_version": "w03-c09-pytest-evidence-v1",
        "collected": nodes,
        "collection_errors": 0,
        "exit_code": 0,
        "reports": [
            {"nodeid": node, "when": phase, "outcome": "passed", "wasxfail": False}
            for node in nodes
            for phase in ("setup", "call", "teardown")
        ],
    }


def test_frozen_manifest_schema_families_counts_and_content() -> None:
    manifest = gate.load_manifest(MANIFEST)
    assert tuple(family.id for family in manifest.families) == gate.FAMILY_IDS
    assert tuple(family.expected_cases for family in manifest.families) == (
        3,
        7,
        10,
        5,
        11,
        6,
        11,
        6,
        6,
        20,
    )
    targets = [target for family in manifest.families for target in family.targets]
    assert len(targets) == 38 and sum(target.expected_cases for target in targets) == 85
    assert sum(target.expected_cases > 1 for target in targets) == 10
    assert manifest.sha256 == "bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990"


@pytest.mark.parametrize(
    "key",
    [
        "schema_version",
        "gate_version",
        "checkpoint",
        "contract_entry_sha",
        "selector_semantics",
        "total_selectors",
        "total_cases",
    ],
)
def test_strict_manifest_metadata(tmp_path: Path, key: str) -> None:
    document = manifest_document()
    document[key] = "invalid"
    with pytest.raises(gate.GateError):
        gate.load_manifest(write_manifest(tmp_path, document))


@pytest.mark.parametrize("level", ["root", "family", "target"])
@pytest.mark.parametrize("change", ["extra", "missing"])
def test_unknown_and_missing_keys_rejected(tmp_path: Path, level: str, change: str) -> None:
    document = manifest_document()
    target = document if level == "root" else document["families"][0]
    if level == "target":
        target = target["targets"][0]
    if change == "extra":
        target["command"] = "pytest"
    else:
        target.pop(next(iter(target)))
    with pytest.raises(gate.GateError):
        gate.load_manifest(write_manifest(tmp_path, document))


@pytest.mark.parametrize("change", ["missing", "unknown", "reorder", "duplicate", "empty"])
def test_family_set_and_order_rejected(tmp_path: Path, change: str) -> None:
    document = manifest_document()
    families = document["families"]
    if change == "missing":
        families.pop()
    elif change == "unknown":
        families[0]["id"] = "F00 UNKNOWN"
    elif change == "reorder":
        families[0], families[1] = families[1], families[0]
    elif change == "duplicate":
        families[1] = copy.deepcopy(families[0])
    else:
        families[0]["targets"] = []
    with pytest.raises(gate.GateError):
        gate.load_manifest(write_manifest(tmp_path, document))


def test_duplicate_selector_across_families_rejected(tmp_path: Path) -> None:
    document = manifest_document()
    document["families"][1]["targets"][1] = copy.deepcopy(document["families"][0]["targets"][0])
    with pytest.raises(gate.GateError, match="duplicate selector"):
        gate.load_manifest(write_manifest(tmp_path, document))


@pytest.mark.parametrize(
    "selector",
    [
        "src/test_x.py::test_case",
        "tests/../test_x.py::test_case",
        "/tests/test_x.py::test_case",
        "tests\\test_x.py::test_case",
        "tests//test_x.py::test_case",
        "tests/test_x.py",
        "tests/test_x.py::Class::test_case",
        "tests/test_x.py::test_case[param]",
        "tests/test_*.py::test_case",
        "tests/test_x.py::test_*",
        "-k test_case",
        "tests/test_x.py::test_case --collect-only",
        "tests/test_x.py::test_case;echo bad",
        "tests/test_x.py::test_case|true",
        "tests/test_x.py::test_case\n--ignore=tests",
        "tests/test_x.py::test_case$()",
        "tests/test_x.py::test_case&&true",
    ],
)
def test_invalid_escaping_wildcard_flag_shell_selectors(tmp_path: Path, selector: str) -> None:
    document = manifest_document()
    document["families"][0]["targets"][0]["selector"] = selector
    with pytest.raises(gate.GateError, match="exact test-function selector"):
        gate.load_manifest(write_manifest(tmp_path, document))


@pytest.mark.parametrize("count", [0, -1, True, 1.0, "1", None])
def test_nonpositive_or_noninteger_counts_rejected(tmp_path: Path, count: object) -> None:
    document = manifest_document()
    document["families"][0]["targets"][0]["expected_cases"] = count
    with pytest.raises(gate.GateError, match="positive integer"):
        gate.load_manifest(write_manifest(tmp_path, document))


def test_frozen_selector_and_count_cannot_be_substituted(tmp_path: Path) -> None:
    document = manifest_document()
    document["families"][0]["targets"][0]["selector"] = "tests/test_fixture.py::test_weaker"
    with pytest.raises(gate.GateError, match="frozen selector/count content"):
        gate.load_manifest(write_manifest(tmp_path, document))
    document = manifest_document()
    document["families"][1]["targets"][0]["expected_cases"] = 4
    document["families"][1]["targets"][1]["expected_cases"] = 2
    with pytest.raises(gate.GateError, match="frozen selector/count content"):
        gate.load_manifest(write_manifest(tmp_path, document))


def test_family_and_global_sum_drift_rejected(tmp_path: Path) -> None:
    document = manifest_document()
    document["families"][0]["expected_cases"] += 1
    with pytest.raises(gate.GateError, match="target sum"):
        gate.load_manifest(write_manifest(tmp_path, document))
    document = manifest_document()
    document["families"][0]["targets"].pop()
    document["families"][0]["expected_cases"] -= 1
    with pytest.raises(gate.GateError, match="totals"):
        gate.load_manifest(write_manifest(tmp_path, document))


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b"[]", b"{broken"])
def test_duplicate_json_keys_and_malformed_json_rejected(tmp_path: Path, raw: bytes) -> None:
    path = tmp_path / "manifest.json"
    path.write_bytes(raw)
    with pytest.raises(ValueError):
        gate.load_manifest(path)


@pytest.mark.parametrize("head", ["A" * 40, "a" * 39, "a" * 41, "g" * 40, "main", "0" * 40])
def test_exact_head_malformed_or_mismatched_rejected(head: str) -> None:
    with pytest.raises(gate.GateError):
        gate.verify_head(head, ROOT)


def test_exact_head_cli_mismatch_invalidates_stale_pass(tmp_path: Path) -> None:
    output = tmp_path / "summary.json"
    output.write_text('{"overall":"PASS"}', encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/ci/run_w03_ai_loop_gate.py"),
            "--manifest",
            str(MANIFEST),
            "--expected-head",
            "0" * 40,
            "--output-json",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0 and "HEAD mismatch" in result.stderr
    assert json.loads(output.read_bytes())["overall"] == "FAIL"


@pytest.mark.parametrize(
    "source",
    [
        "def test_renamed(): pass",
        "def test_case(: pass",
    ],
)
def test_missing_renamed_and_collection_failure(tmp_path: Path, source: str) -> None:
    repo, family = fixture_repo(tmp_path, source)
    with pytest.raises(gate.GateError):
        gate.execute_family(family, repo)


@pytest.mark.parametrize(
    "source",
    [
        "def test_case(): assert False",
        "import pytest\n@pytest.fixture\ndef bad(): raise RuntimeError('setup')\n"
        "def test_case(bad): pass",
        "import pytest\n@pytest.fixture\ndef bad():\n    yield\n"
        "    raise RuntimeError('teardown')\n"
        "def test_case(bad): pass",
        "import pytest\ndef test_case(): pytest.skip('critical')",
        "import pytest\n@pytest.mark.xfail(reason='critical')\ndef test_case(): assert False",
        "import pytest\n@pytest.mark.xfail(reason='', strict=False)\ndef test_case(): pass",
        "import pytest\n@pytest.mark.xfail(reason='critical', strict=True)\ndef test_case(): pass",
    ],
)
def test_real_pytest_failure_error_skip_xfail_xpass(tmp_path: Path, source: str) -> None:
    repo, family = fixture_repo(tmp_path, source)
    with pytest.raises(gate.GateError):
        gate.execute_family(family, repo)


def test_real_parameter_expansion_count_and_partial_execution(tmp_path: Path) -> None:
    repo, _ = fixture_repo(
        tmp_path,
        """
        import pytest
        @pytest.mark.parametrize('value', [0, 1, 2], ids=['keep', 'second', 'third'])
        def test_case(value):
            assert value >= 0
    """,
    )
    family = gate.Family("fixture", 3, (gate.Target("tests/test_fixture.py::test_case", 3),))
    result = gate.execute_family(family, repo)
    assert result["selectors"] == 1 and result["tests"] == 3
    with pytest.raises(gate.GateError, match="count drift"):
        gate.execute_family(
            gate.Family("fixture", 2, (gate.Target(family.targets[0].selector, 2),)), repo
        )
    (repo / "pytest.ini").write_text("[pytest]\naddopts = -k keep\n", encoding="utf-8")
    with pytest.raises(gate.GateError, match="count drift"):
        gate.execute_family(family, repo)


@pytest.mark.parametrize(
    "defect",
    [
        "zero",
        "missing_call",
        "duplicate_phase",
        "foreign_node",
        "foreign_collected",
        "duplicate_leaf",
        "count_swap",
    ],
)
def test_leaf_mapping_and_complete_phase_enforcement(defect: str) -> None:
    family = gate.Family(
        "fixture",
        3,
        (gate.Target("tests/test_a.py::test_one", 1), gate.Target("tests/test_b.py::test_two", 2)),
    )
    evidence = valid_evidence(family)
    if defect == "zero":
        evidence["collected"] = []
    elif defect == "missing_call":
        evidence["reports"].pop(1)
    elif defect == "duplicate_phase":
        evidence["reports"].append(evidence["reports"][0])
    elif defect == "foreign_node":
        evidence["reports"][0]["nodeid"] = "tests/test_x.py::test_foreign"
    elif defect == "foreign_collected":
        evidence["collected"][0] = "tests/test_x.py::test_foreign"
    elif defect == "duplicate_leaf":
        evidence["collected"][1] = evidence["collected"][0]
    else:
        # Same family total, wrong per-selector distribution must still fail.
        evidence["collected"][1] = "tests/test_a.py::test_one[extra]"
    with pytest.raises(gate.GateError):
        gate.validate_evidence(family, evidence, 0)


def test_summary_is_deterministic_ordered_and_byte_hash_bound(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_execute(family: gate.Family, repo: Path) -> dict[str, object]:
        return {
            "id": family.id,
            "status": "PASS",
            "selectors": len(family.targets),
            "tests": family.expected_cases,
            "targets": gate.validate_evidence(family, valid_evidence(family), 0),
        }

    monkeypatch.setattr(gate, "execute_family", fake_execute)
    head = git("rev-parse", "HEAD").strip()
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    summary = gate.run_gate(MANIFEST, head, first, ROOT)
    gate.run_gate(MANIFEST, head, second, ROOT)
    assert first.read_bytes() == second.read_bytes() == gate.canonical(summary) + b"\n"
    assert summary["implementation_sha"] == head and summary["overall"] == "PASS"
    assert summary["manifest_sha256"] == hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    assert [item["id"] for item in cast(list[dict[str, object]], summary["families"])] == list(
        gate.FAMILY_IDS
    )
    reformatted = write_manifest(tmp_path, manifest_document())
    alternate = gate.run_gate(reformatted, head, second, ROOT)
    assert alternate["manifest_sha256"] == hashlib.sha256(reformatted.read_bytes()).hexdigest()
    assert alternate["manifest_sha256"] != summary["manifest_sha256"]
    assert "timestamp" not in summary


def test_incomplete_gate_never_publishes_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(family: gate.Family, repo: Path) -> dict[str, object]:
        raise gate.GateError("critical failure")

    monkeypatch.setattr(gate, "execute_family", fail)
    output = tmp_path / "summary.json"
    with pytest.raises(gate.GateError, match="critical failure"):
        gate.run_gate(MANIFEST, git("rev-parse", "HEAD").strip(), output, ROOT)
    assert json.loads(output.read_bytes())["overall"] == "FAIL"
    with pytest.raises(gate.GateError, match="outside the source repository"):
        gate.run_gate(MANIFEST, "0" * 40, ROOT / "src/forbidden.json", ROOT)
    assert not (ROOT / "src/forbidden.json").exists()


def test_workflow_one_job_exact_schedule_source_manifest_and_environment() -> None:
    current = workflow_jobs()
    assert set(current) == {
        "classify-change",
        "quality",
        "compose-smoke",
        "publication-proof",
        "verification-gate",
        "w03-ai-loop-gate",
        "shadow-static-and-plan",
        "shadow-integration-and-data",
        "shadow-non-integration",
        "shadow-non-integration-aggregate",
        "shadow-equivalence",
    }
    job = current["w03-ai-loop-gate"]
    assert "name: W03 AI loop gate" in job
    schedule = (
        "if: ${{ always() && !cancelled() && (needs['classify-change'].result != "
        "'success' || needs['classify-change'].outputs.change_class != 'P') }}"
    )
    assert schedule in job
    assert "needs: [classify-change, quality, compose-smoke, publication-proof]" in job
    head = (
        "${{ github.event_name == 'pull_request' && github.event.pull_request.head.sha "
        "|| github.sha }}"
    )
    assert f"ref: {head}" in job and job.count(f"EXPECTED_HEAD: {head}") == 2
    assert 'test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD"' in job
    for required in (
        "pgvector/pgvector:0.8.6-pg17-bookworm",
        "POSTGRES_DB: flowlens_test",
        "FLOWLENS_APP_ENVIRONMENT: test",
        "FLOWLENS_DATABASE_URL: postgresql+psycopg://",
        'python-version: "3.12"',
        'version: "0.12.5"',
        "uv sync --frozen",
        "check_database_connectivity",
        "uv run alembic upgrade head",
        "uv run python scripts/ci/run_w03_ai_loop_gate.py",
        "--manifest docs/w03/checkpoints/c09/specs/c09_gate_manifest.json",
        '--expected-head "$EXPECTED_HEAD"',
        '--output-json "$RUNNER_TEMP/w03-ai-loop-gate.json"',
    ):
        assert required in job
    assert (
        job.index("check_database_connectivity")
        < job.index("alembic upgrade head")
        < job.index("run_w03_ai_loop_gate.py")
    )
    assert not re.search(r"openai|secrets\.|api_key|upload-artifact", job, re.IGNORECASE)


def test_existing_workflow_jobs_triggers_pins_and_quality_are_unchanged() -> None:
    baseline = git("show", f"{gate.ENTRY}:.github/workflows/ci.yml")
    current_text = WORKFLOW.read_text(encoding="utf-8")
    original = jobs(baseline)
    current = jobs(current_text)
    for job_id in ("classify-change", "compose-smoke", "publication-proof"):
        assert current[job_id] == original[job_id]
    assert (
        current["quality"].split("    steps:\n")[0] == original["quality"].split("    steps:\n")[0]
    )
    legacy_steps = workflow_steps(original["quality"])
    instrumented = workflow_steps(current["quality"])
    modified = {"Run database integration tests", "Run complete test suite"}
    assert set(instrumented) - set(legacy_steps) == {
        "Freeze legacy exact collection and entry no-loss plan",
        "Upload legacy-integration exact-SHA evidence",
        "Upload legacy-nonint exact-SHA evidence",
    }
    for name, body in legacy_steps.items():
        if name not in modified:
            assert instrumented[name] == body
    for name, marker, role in (
        ("Run database integration tests", "integration", "legacy-integration"),
        ("Run complete test suite", "not integration", "legacy-nonint"),
    ):
        body = instrumented[name]
        assert "uv run python scripts/ci/pytest_outcome_receipt.py" in body
        assert f'--role {role} --marker "{marker}"' in body
        assert '--plan "$RUNNER_TEMP/devctrl02-legacy-plan.json"' in body
        assert '--expected-head "$EXPECTED_HEAD"' in body
    assert current_text.split("jobs:\n")[0] == baseline.split("jobs:\n")[0]
    action_pattern = r"uses: ([^\n]+)"
    assert set(re.findall(action_pattern, current_text)) == set(
        re.findall(action_pattern, baseline)
    ) | {
        "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2",
        "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093 # v4.3.0",
    }
    for required in (
        'uv run pytest -m "not integration"',
        "uv run pytest -m integration",
        "uv run ruff check .",
        "uv run mypy .",
        "uv lock --check",
    ):
        assert required in current["quality"]
    assert "name: Verification gate" in current["verification-gate"]


def test_verification_runs_actual_shell_truth_table() -> None:
    verification = workflow_jobs()["verification-gate"]
    assert (
        "needs: [classify-change, quality, compose-smoke, publication-proof, "
        "w03-ai-loop-gate, shadow-equivalence]" in verification
    )
    assert "if: always()" in verification
    assert "W03_RESULT: ${{ needs['w03-ai-loop-gate'].result }}" in verification
    script = textwrap.dedent(verification.split("        run: |\n", 1)[1])
    bash = shutil.which("bash") if sys.platform != "win32" else "C:/Program Files/Git/bin/bash.exe"
    assert bash and Path(bash).is_file(), "Bash required to execute the actual CI enforcement shell"

    def enforce(change: str, values: dict[str, str]) -> int:
        assignments = f"CHANGE_CLASS={change}\n" + "\n".join(
            f"{key}='{value}'" for key, value in values.items()
        )
        return subprocess.run(
            [bash, "--noprofile", "--norc", "-e", "-c", assignments + "\n" + script],
            capture_output=True,
            check=False,
        ).returncode

    for change in ("P", "C", "I", "F", "UNKNOWN"):
        expected = {
            "CLASS_RESULT": "success",
            "QUALITY_RESULT": "skipped" if change == "P" else "success",
            "COMPOSE_RESULT": "skipped" if change == "P" else "success",
            "W03_RESULT": "skipped" if change == "P" else "success",
            "PUBLICATION_RESULT": "success" if change == "P" else "skipped",
            "SHADOW_RESULT": "skipped" if change == "P" else "success",
        }
        assert enforce(change, expected) == 0
        for key in expected:
            for wrong in ("success", "skipped", "failure", "cancelled", ""):
                if wrong != expected[key]:
                    assert enforce(change, expected | {key: wrong}) != 0, (change, key, wrong)
    assert enforce("INVALID", expected) != 0


def test_classifier_publication_and_runtime_frozen_materials_unchanged() -> None:
    for path in (
        "scripts/ci/verify_publication.py",
        "pyproject.toml",
        "uv.lock",
        "docker-compose.yml",
    ):
        assert (ROOT / path).read_text(encoding="utf-8") == git("show", f"{gate.ENTRY}:{path}")
    # DEVCTRL-01 evolves authorized additions through the versioned manifest
    # while retaining all W03 source and every closed checkpoint's Git blobs.
    from verify_w04_source_evolution import verify_source_evolution

    proof = verify_source_evolution(
        ROOT / "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json",
        git("rev-parse", "HEAD").strip(),
        ROOT,
    )
    assert proof["overall"] == "PASS"
    assert not git("diff", "--name-only", gate.ENTRY, "HEAD", "--", "migrations", "apps")
