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


C10_ENTRY_SHA = "d33ee858fca8caaceba2ce60c045f7e4213c631a"
C10_PREP_SHA = "f391cf25871473d488a8f5c7e7ff77fb933920d8"
C10_BOOTSTRAP_SUBJECT = "ci(w04-c10): admit bounded acceptance lifecycle"
C10_STAGE_A_SUBJECT = "docs(w04-c10): prepare investigation business acceptance"
C10_STAGE_B_SUBJECT = "docs(w04-c10): publish business acceptance readiness proof"
C10_STAGE_A_PATHS = (
    "docs/w04/checkpoints/c10/W04_C10_AUTHORIZATION_CONTRACT.md",
    "docs/w04/checkpoints/c10/W04_C10_HUMAN_AUTHORIZATION.md",
    "docs/w04/checkpoints/c10/W04_C10_CONTEXT_LOCK.md",
    "docs/w04/checkpoints/c10/W04_C10_BUSINESS_ACCEPTANCE_SPEC.md",
    "docs/w04/checkpoints/c10/W04_C10_EVIDENCE_MATRIX.md",
    "docs/w04/checkpoints/c10/W04_C10_HUMAN_ACCEPTANCE_FORM.md",
    "docs/w04/checkpoints/c10/W04_C10_HARNESS_SPEC.md",
    "docs/w04/checkpoints/c10/W04_C10_GPT_REVIEW_CHECKLIST.md",
    "docs/w04/checkpoints/c10/W04_C10_BUSINESS_ACCEPTANCE_DOSSIER.md",
    "docs/w04/checkpoints/c10/specs/c10_acceptance_manifest.json",
    "docs/w04/checkpoints/c10/specs/authorized_paths.json",
)
C10_STAGE_B_PATH = "docs/w04/checkpoints/c10/W04_C10_R_DEVELOPMENT_ROUND_REPORT.md"
C10_SOURCE_ADDITIONS = (
    "C10_ENTRY_SHA",
    "C10_PREP_SHA",
    "C10_BOOTSTRAP_SUBJECT",
    "C10_STAGE_A_SUBJECT",
    "C10_STAGE_B_SUBJECT",
    "C10_STAGE_A_PATHS",
    "C10_STAGE_B_PATH",
    "C10_SOURCE_ADDITIONS",
    "validate_c10_lifecycle",
    "c10_bootstrap_revision",
    "validate_c10_verifier_sources",
    "c10_verifier_blob_guard",
    "check_c10_lifecycle_controls",
)


C10_CLOSEOUT_REVIEW_READY_SHA = "250ea1b7476db61aba20b5d2fb11148ce8243678"
C10_CLOSEOUT_BOOTSTRAP_SHA = "a34a84b97681f24bf6df1fed1a80825ae32decfa"
C10_CLOSEOUT_STAGE_A_SHA = "59ec925122c1fdc5b76a3c22fc0ab60a785efb38"
C10_CLOSEOUT_PREP_SUBJECT = "ci(w04-c10): admit bounded closeout lifecycle"
C10_FINAL_CLOSEOUT_SUBJECT = "docs(w04-c10): close business acceptance checkpoint"
C10_FINAL_CLOSEOUT_PATHS = (
    "docs/w04/checkpoints/c10/W04_C10_GPT_INDEPENDENT_REVIEW_R1.md",
    "docs/w04/checkpoints/c10/W04_C10_HUMAN_ACCEPTANCE.md",
    "docs/w04/checkpoints/c10/W04_C10_CLOSEOUT_AUTHORIZATION.md",
    "docs/w04/checkpoints/c10/W04_C10_CLOSEOUT_CONTEXT_LOCK.md",
    "docs/w04/checkpoints/c10/W04_C10_FINAL_CLOSEOUT_REPORT.md",
)
C10_CLOSEOUT_SOURCE_ADDITIONS = (
    "C10_CLOSEOUT_REVIEW_READY_SHA",
    "C10_CLOSEOUT_BOOTSTRAP_SHA",
    "C10_CLOSEOUT_STAGE_A_SHA",
    "C10_CLOSEOUT_PREP_SUBJECT",
    "C10_FINAL_CLOSEOUT_SUBJECT",
    "C10_FINAL_CLOSEOUT_PATHS",
    "C10_CLOSEOUT_SOURCE_ADDITIONS",
    "validate_c10_closeout_lifecycle",
    "c10_closeout_prep_revision",
    "validate_c10_closeout_verifier_sources",
    "c10_closeout_verifier_blob_guard",
    "check_c10_closeout_lifecycle_controls",
)


W04_SPRINT_ENTRY_SHA = "232bfb390babce30417b8cdb9a6660663eb3c3f1"
W04_SPRINT_CLOSEOUT_PREP_SUBJECT = "ci(w04): admit sprint closeout lifecycle"
W04_SPRINT_FINAL_CLOSEOUT_SUBJECT = "docs(w04): close sprint and prepare PR #7 review"
W04_SPRINT_FINAL_MODIFIED_PATHS = ("README.md", "AGENTS.md", "docs/CURRENT_STATE.md")
W04_SPRINT_FINAL_ADDED_PATHS = (
    "docs/w04/W04_GPT_INDEPENDENT_DEEP_REVIEW_R1.md",
    "docs/w04/W04_SPRINT_HUMAN_ACCEPTANCE_AND_AUTHORIZATION.md",
    "docs/w04/W04_SPRINT_CLOSEOUT_CONTEXT_LOCK.md",
    "docs/w04/W04_SPRINT_FINAL_CLOSEOUT_REPORT.md",
    "docs/w04/W04_PR7_READINESS_REPORT.md",
)
W04_SPRINT_SOURCE_ADDITIONS = (
    "W04_SPRINT_ENTRY_SHA",
    "W04_SPRINT_CLOSEOUT_PREP_SUBJECT",
    "W04_SPRINT_FINAL_CLOSEOUT_SUBJECT",
    "W04_SPRINT_FINAL_MODIFIED_PATHS",
    "W04_SPRINT_FINAL_ADDED_PATHS",
    "W04_SPRINT_SOURCE_ADDITIONS",
    "validate_w04_sprint_lifecycle",
    "w04_sprint_prep_revision",
    "validate_w04_sprint_verifier_sources",
    "w04_sprint_verifier_blob_guard",
    "check_w04_sprint_controls",
)


W04_PR7_FINAL_SHA = "985f666e5ecfa5acd35565516e200c9b0e36c76b"
W04_PR7_MAIN_SHA = "af61bdfd5f7cf7961811c4c2dc8e554dd7eed509"
W04_PR7_MERGE_REPAIR_SUBJECT = "ci(w04): admit PR #7 merge commit lifecycle"
W04_PR7_MERGE_SOURCE_ADDITIONS = (
    "W04_PR7_FINAL_SHA",
    "W04_PR7_MAIN_SHA",
    "W04_PR7_MERGE_REPAIR_SUBJECT",
    "W04_PR7_MERGE_SOURCE_ADDITIONS",
    "validate_w04_pr7_merge_repair_lifecycle",
    "validate_w04_pr7_merge_topology",
    "w04_pr7_merged_main_guard",
    "w04_pr7_repair_history",
    "w04_pr7_pre_integration_guard",
    "w04_pr7_integration_anchor",
    "w04_pr7_historical_tip",
    "w04_pr7_merge_repair_revision",
    "validate_w04_pr7_merge_verifier_sources",
    "w04_pr7_merge_verifier_blob_guard",
    "check_w04_pr7_merge_controls",
    "check_w04_pr7_post_integration_controls",
)



W04_POST_MERGE_BASE_SHA = "b2b582541d38180c3bf8360699e6df271979829a"

W04_P2_03_HARDENING_SUBJECT = "ci(post-w04): harden publication deletion governance"

W04_P2_03_HARDENING_PATHS = (
    "scripts/ci/classify_change.py",
    "scripts/ci/verify_publication.py",
    "scripts/ci/verify_w04_investigation_gate_contract.py",
    "tests/test_ci_change_classifier.py",
    "tests/test_ci_publication_gate.py",
)

W04_P2_03_TEST_FUNCTIONS = {
    "tests/test_ci_change_classifier.py": (
        "test_w04_current_git_delta_routes_each_class",
        "test_shadow_workflow_requires_equivalence_and_preserves_classification",
    ),
    "tests/test_ci_publication_gate.py": (
        "test_report_and_state_pass_exact_publication_proof",
        "test_w04_narrow_report_grammars_pass_exact_publication",
    ),
}

W04_P2_03_CI_EDITS = {
    "scripts/ci/classify_change.py": (
        (
            "\ndef changed_paths(",
            "\n"
            "def changed_entries(repo: Path, base: str, head: str) "
            "-> list[tuple[str, str]]:\n"
            '    """Read exact status/path pairs; malformed Git '
            'output cannot grant light proof."""\n'
            "    raw = subprocess.run(\n"
            '        ["git", "diff", "--name-status", '
            '"--no-renames", "-z", base, head, "--"],\n'
            "        cwd=repo,\n"
            "        check=True,\n"
            "        capture_output=True,\n"
            "    ).stdout\n"
            "    if not raw:\n"
            "        return []\n"
            '    if not raw.endswith(b"\\x00"):\n'
            '        raise ValueError("unterminated Git status/path '
            'delta")\n'
            '    fields = raw[:-1].split(b"\\x00")\n'
            "    if len(fields) % 2:\n"
            '        raise ValueError("malformed Git status/path '
            'delta")\n'
            "    entries = []\n"
            "    for status_raw, path_raw in zip(fields[::2], "
            "fields[1::2], strict=True):\n"
            '        status = status_raw.decode("ascii", '
            'errors="strict")\n'
            '        path = path_raw.decode("utf-8", '
            'errors="strict")\n'
            '        if re.fullmatch(r"[ACDMRTUXB]", status) is None '
            "or not path:\n"
            '            raise ValueError("invalid Git status/path '
            'entry")\n'
            "        entries.append((status, path))\n"
            "    if len({path for _, path in entries}) != "
            "len(entries):\n"
            '        raise ValueError("duplicate Git delta path")\n'
            "    return sorted(entries, key=lambda entry: entry[1])\n"
            "\n"
            "\n"
            "def changed_paths(",
        ),
        (
            "        paths = changed_paths(repo, base, head)\n"
            "        change_class = classify_paths(paths)\n",
            "        entries = changed_entries(repo, base, head)\n"
            "        paths = [path for _, path in entries]\n"
            "        change_class = classify_paths(paths)\n"
            '        if change_class == "P" and any(status not in '
            '{"A", "M"} for status, _ in entries):\n'
            '            return result("UNKNOWN", base, head, paths, '
            '"publication_non_add_modify_delta")\n',
        ),
    ),
    "scripts/ci/verify_publication.py": (
        (
            "        if not tree_entry:\n"
            "            continue  # A deleted publication "
            "document has no head content to scan.\n",
            "        if not tree_entry:\n"
            '            raise ValueError(f"missing publication '
            'file at verified head: {path}")\n',
        ),
    ),
}

W04_P2_03_CONNECTORS = {
    "validate_w04_pr7_merge_verifier_sources": (
        (
            '    accepted = git("show", W04_PR7_FINAL_SHA '
            '+ ":" + CLOSEOUT_VERIFIER_PATH).decode()\n',
            '    if "W04_POST_MERGE_BASE_SHA = " in '
            "current:\n"
            "        "
            "validate_w04_p2_03_verifier_sources(review_ready, "
            "current)\n"
            "        return\n"
            '    accepted = git("show", W04_PR7_FINAL_SHA '
            '+ ":" + CLOSEOUT_VERIFIER_PATH).decode()\n',
        ),
    ),
    "w04_pr7_merge_verifier_blob_guard": (
        (
            '    require(repair is not None, "missing validated PR7 merge repair")\n',
            '    require(repair is not None, "missing validated '
            'PR7 merge repair")\n'
            "    frozen = w04_p2_03_hardening_revision(repo) or "
            "repair\n",
        ),
        (
            '        == git("show", str(repair) + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo)\n',
            '        == git("show", str(frozen) + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo)\n',
        ),
        (
            '        == git("rev-parse", str(repair) + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo),\n',
            '        == git("rev-parse", str(frozen) + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo),\n',
        ),
        (
            "    print(\n"
            "        json.dumps(\n"
            "            {\n"
            '                "w04_pr7_merge_repair_sha": '
            "repair,\n"
            "                "
            '"w04_pr7_merge_adversarial_controls": controls,\n'
            '                "w04_post_integration_controls": '
            "post_controls,\n"
            '                "w04_pr7_merge_source_guard": '
            '"PASS",\n'
            "            },\n"
            "            sort_keys=True,\n"
            "        )\n"
            "    )\n",
            "    print(\n"
            "        json.dumps(\n"
            "            {\n"
            '                "w04_pr7_merge_repair_sha": '
            "repair,\n"
            "                "
            '"w04_pr7_merge_adversarial_controls": controls,\n'
            '                "w04_post_integration_controls": '
            "post_controls,\n"
            '                "w04_pr7_merge_source_guard": '
            '"PASS",\n'
            "            },\n"
            "            sort_keys=True,\n"
            "        )\n"
            "    )\n"
            "    if frozen != repair:\n"
            "        hardening_controls = "
            "check_w04_p2_03_controls()\n"
            "        print(\n"
            "            json.dumps(\n"
            "                {\n"
            "                    "
            '"w04_post_merge_p2_03_hardening": "PASS",\n'
            '                    "w04_p2_03_hardening_sha": '
            "frozen,\n"
            '                    "w04_p2_03_controls": '
            "hardening_controls,\n"
            "                },\n"
            "                sort_keys=True,\n"
            "            )\n"
            "        )\n",
        ),
    ),
    "meta_ci_source_guard": (
        ("        validate_meta_ci_sources(\n", "        validate_w04_p2_03_meta_ci_sources(\n"),
        (
            '            (repo / path).read_text(encoding="utf-8"),\n',
            '            (repo / path).read_text(encoding="utf-8"),\n            repo=repo,\n',
        ),
    ),
    "check_meta_ci_source_controls": (
        (
            "        validate_meta_ci_sources(path, entry, current)\n",
            "        validate_w04_p2_03_meta_ci_sources(path, entry, current)\n",
        ),
        (
            "                lambda damaged=damaged, path=path, "
            "entry=entry: validate_meta_ci_sources(\n",
            "                lambda damaged=damaged, path=path, "
            "entry=entry: validate_w04_p2_03_meta_ci_sources(\n",
        ),
    ),
    "verify_collection_and_scope": (
        (
            '        "scripts/ci/classify_change.py",\n'
            '        "scripts/ci/verify_publication.py",\n',
            "",
        ),
        (
            '    require(not git("diff", ENTRY, "--", *protected), '
            '"W04_C09_PROTECTED_OBJECT_DRIFT")\n',
            "    w04_p2_03_protected_source_guard()\n"
            '    require(not git("diff", ENTRY, "--", *protected), '
            '"W04_C09_PROTECTED_OBJECT_DRIFT")\n',
        ),
    ),
}

W04_P2_03_CONTROL_LABELS = (
    "w04-add",
    "w04-modify",
    "state-add",
    "state-modify",
    "w04-delete",
    "w04-delete-defense",
    "state-delete",
    "state-delete-defense",
    "push-delete",
    "publication-rename",
    "mixed-add-delete",
    "routing-C",
    "routing-I",
    "routing-F",
    "routing-UNKNOWN",
    "parser-no-nul",
    "parser-odd",
    "parser-status",
    "parser-empty-status",
    "parser-empty-path",
    "parser-utf8",
    "parser-status-utf8",
    "parser-duplicate",
    "parser-type-change",
    "publication-type-change",
    "history-hardening",
    "history-before",
    "history-docs",
    "history-parent",
    "history-merge-parent",
    "history-root-parent",
    "history-subject",
    "history-sha",
    "history-extra-path",
    "history-missing:scripts/ci/classify_change.py",
    "history-A:scripts/ci/classify_change.py",
    "history-D:scripts/ci/classify_change.py",
    "history-R100:scripts/ci/classify_change.py",
    "history-missing:scripts/ci/verify_publication.py",
    "history-A:scripts/ci/verify_publication.py",
    "history-D:scripts/ci/verify_publication.py",
    "history-R100:scripts/ci/verify_publication.py",
    "history-missing:scripts/ci/verify_w04_investigation_gate_contract.py",
    "history-A:scripts/ci/verify_w04_investigation_gate_contract.py",
    "history-D:scripts/ci/verify_w04_investigation_gate_contract.py",
    "history-R100:scripts/ci/verify_w04_investigation_gate_contract.py",
    "history-missing:tests/test_ci_change_classifier.py",
    "history-A:tests/test_ci_change_classifier.py",
    "history-D:tests/test_ci_change_classifier.py",
    "history-R100:tests/test_ci_change_classifier.py",
    "history-missing:tests/test_ci_publication_gate.py",
    "history-A:tests/test_ci_publication_gate.py",
    "history-D:tests/test_ci_publication_gate.py",
    "history-R100:tests/test_ci_publication_gate.py",
    "history-multiple",
    "history-duplicate",
    "ci-drift:scripts/ci/classify_change.py",
    "ci-drift:scripts/ci/verify_publication.py",
    "test-unrelated:tests/test_ci_change_classifier.py",
    "test-extra:tests/test_ci_change_classifier.py",
    "test-body:test_w04_current_git_delta_routes_each_class",
    "test-signature:test_w04_current_git_delta_routes_each_class",
    "test-decorator:test_w04_current_git_delta_routes_each_class",
    "test-body:test_shadow_workflow_requires_equivalence_and_preserves_classification",
    "test-signature:test_shadow_workflow_requires_equivalence_and_preserves_classification",
    "test-decorator:test_shadow_workflow_requires_equivalence_and_preserves_classification",
    "test-parametrization:tests/test_ci_change_classifier.py",
    "test-unrelated:tests/test_ci_publication_gate.py",
    "test-extra:tests/test_ci_publication_gate.py",
    "test-body:test_report_and_state_pass_exact_publication_proof",
    "test-signature:test_report_and_state_pass_exact_publication_proof",
    "test-decorator:test_report_and_state_pass_exact_publication_proof",
    "test-body:test_w04_narrow_report_grammars_pass_exact_publication",
    "test-signature:test_w04_narrow_report_grammars_pass_exact_publication",
    "test-decorator:test_w04_narrow_report_grammars_pass_exact_publication",
    "test-parametrization:tests/test_ci_publication_gate.py",
    "verifier-constant",
    "verifier-legacy",
    "verifier-extra",
    "verifier-admitted",
    "verifier-order",
    "git-hardening-freeze",
    "git-protected:scripts/ci/classify_change.py",
    "git-protected:scripts/ci/verify_publication.py",
    "git-protected:scripts/ci/verify_w04_investigation_gate_contract.py",
    "git-protected:tests/test_ci_change_classifier.py",
    "git-protected:tests/test_ci_publication_gate.py",
    "git-frozen:.github/workflows/ci.yml",
    "git-frozen:docs/w04/checkpoints/c09/specs/c09_gate_manifest.json",
    "git-frozen:src/flowlens/investigation/__init__.py",
    "git-multiple-anchors",
    "git-wrong-subject",
    "git-wrong-parent",
)

W04_P2_03_SOURCE_ADDITIONS = (
    "W04_POST_MERGE_BASE_SHA",
    "W04_P2_03_HARDENING_SUBJECT",
    "W04_P2_03_HARDENING_PATHS",
    "W04_P2_03_TEST_FUNCTIONS",
    "W04_P2_03_CI_EDITS",
    "W04_P2_03_CONNECTORS",
    "W04_P2_03_CONTROL_LABELS",
    "W04_P2_03_SOURCE_ADDITIONS",
    "validate_w04_p2_03_history",
    "w04_p2_03_commit_record",
    "w04_p2_03_hardening_revision",
    "validate_w04_p2_03_ci_sources",
    "validate_w04_p2_03_test_sources",
    "validate_w04_p2_03_meta_ci_sources",
    "w04_p2_03_protected_source_guard",
    "validate_w04_p2_03_verifier_sources",
    "check_w04_p2_03_controls",
)


W04_P2_03_HARDENING_SHA = "e2606585829153a2f69c9628c916cf42dcc1b926"

W04_P2_03_DOC_SYNC_SHA = "ca2506115b282d9569c3f7c35da266927a39520f"

W04_P2_03_DOC_SYNC_SUBJECT = "docs: synchronize W04 merged state"

W04_P2_03_DOC_SYNC_PATHS = ("README.md", "AGENTS.md", "docs/CURRENT_STATE.md")

W04_P2_03_R2_REPAIR_SUBJECT = "ci(post-w04): repair stabilization proof closure"

W04_P2_03_R2_REPAIR_PATHS = (
    "scripts/ci/verify_w04_investigation_gate_contract.py",
    "tests/test_c09_ci_gate.py",
    "AGENTS.md",
    "docs/CURRENT_STATE.md",
)

W04_P2_03_R2_C09_TARGET = "test_classifier_publication_and_runtime_frozen_materials_unchanged"

W04_P2_03_R2_CONNECTORS = {
    "validate_w04_p2_03_history": (
        (
            "def validate_w04_p2_03_history(history: list[dict[str, "
            "Any]]) -> str | None:\n"
            '    """Discover one exact direct child; suspicious '
            'near-matches never disappear."""\n'
            "    anchors: list[str] = []\n"
            "    seen: set[str] = set()\n"
            "    for row in history:\n"
            '        require(set(row) == {"sha", "parents", '
            '"subject", "delta"}, "P2_03 record shape")\n'
            '        revision = row["sha"]\n',
            "def validate_w04_p2_03_history(history: list[dict[str, "
            "Any]]) -> str | None:\n"
            '    """Validate every ordered post-base row; no '
            'descendant may disappear."""\n'
            "    # The unchanged merge baseline precedes the "
            "separately authorized hardening.\n"
            "    if not history:\n"
            "        return None\n"
            '    require(1 <= len(history) <= 3, "P2_03 '
            'unauthorized post-base history length")\n'
            "    seen: set[str] = set()\n"
            "    expected = (\n"
            "        (\n"
            "            W04_P2_03_HARDENING_SHA,\n"
            "            W04_POST_MERGE_BASE_SHA,\n"
            "            W04_P2_03_HARDENING_SUBJECT,\n"
            "            W04_P2_03_HARDENING_PATHS,\n"
            "        ),\n"
            "        (\n"
            "            W04_P2_03_DOC_SYNC_SHA,\n"
            "            W04_P2_03_HARDENING_SHA,\n"
            "            W04_P2_03_DOC_SYNC_SUBJECT,\n"
            "            W04_P2_03_DOC_SYNC_PATHS,\n"
            "        ),\n"
            "        (\n"
            "            None,\n"
            "            W04_P2_03_DOC_SYNC_SHA,\n"
            "            W04_P2_03_R2_REPAIR_SUBJECT,\n"
            "            W04_P2_03_R2_REPAIR_PATHS,\n"
            "        ),\n"
            "    )\n"
            "    for row, (frozen, parent, subject, paths) in zip(\n"
            "        history, expected[: len(history)], "
            "strict=True\n"
            "    ):\n"
            "        require(\n"
            "            isinstance(row, dict) and set(row) == "
            '{"sha", "parents", "subject", "delta"},\n'
            '            "P2_03 record shape",\n'
            "        )\n"
            '        revision = row["sha"]\n',
        ),
        (
            "        seen.add(revision)\n"
            '        parents, subject, delta = row["parents"], '
            'row["subject"], row["delta"]\n'
            "        require(\n"
            "            isinstance(parents, list)\n"
            "            and all(isinstance(parent, str) for parent "
            "in parents)\n"
            "            and isinstance(subject, str)\n"
            "            and isinstance(delta, dict),\n"
            '            "P2_03 invalid revision metadata",\n'
            "        )\n"
            "        if subject == W04_P2_03_HARDENING_SUBJECT or "
            "(\n"
            "            parents == [W04_POST_MERGE_BASE_SHA]\n"
            "            and "
            "set(delta).intersection(W04_P2_03_HARDENING_PATHS)\n"
            "        ):\n"
            "            require(\n"
            "                parents == [W04_POST_MERGE_BASE_SHA]\n"
            "                and subject == "
            "W04_P2_03_HARDENING_SUBJECT\n"
            '                and delta == {path: "M" for path in '
            "W04_P2_03_HARDENING_PATHS},\n"
            '                "P2_03 hardening '
            'parent/subject/exact-five-M delta",\n'
            "            )\n"
            "            anchors.append(revision)\n"
            '    require(len(anchors) <= 1, "P2_03 multiple '
            'hardening anchors")\n'
            "    return anchors[0] if anchors else None",
            "        seen.add(revision)\n"
            "        require(\n"
            "            (frozen is None or revision == frozen)\n"
            '            and row["parents"] == [parent]\n'
            '            and row["subject"] == subject\n'
            '            and row["delta"] == {path: "M" for path in '
            "paths},\n"
            '            "P2_03 exact ordered '
            'SHA/parent/subject/M-delta",\n'
            "        )\n"
            "    return W04_P2_03_HARDENING_SHA",
        ),
    ),
    "w04_p2_03_protected_source_guard": (
        (
            '            not git("diff", '
            'W04_POST_MERGE_BASE_SHA, "--", '
            "*W04_P2_03_CI_EDITS, repo=repo),\n"
            '            "P2_03 CI source changed before '
            'validated hardening",\n'
            "        )\n"
            "        return\n"
            "    for path in W04_P2_03_HARDENING_PATHS:\n"
            "        require(\n"
            "            (repo / path).read_bytes() == "
            'git("show", anchor + ":" + path, repo=repo)\n'
            '            and git("ls-tree", "HEAD", "--", '
            "path, repo=repo)\n"
            '            == git("ls-tree", anchor, "--", '
            "path, repo=repo),\n"
            '            "P2_03 protected source drift: " + '
            "path,\n"
            "        )\n"
            "    require(\n"
            '        not git("diff", anchor, "--", '
            "*W04_P2_03_HARDENING_PATHS, repo=repo),\n"
            '        "P2_03 protected working-tree/mode '
            'drift",\n'
            "    )\n"
            "    for path in W04_P2_03_CI_EDITS:\n"
            "        validate_w04_p2_03_ci_sources(\n"
            "            path,\n"
            '            git("show", W04_POST_MERGE_BASE_SHA '
            '+ ":" + path, repo=repo).decode("utf-8"),\n',
            '            not git("diff", '
            'W04_POST_MERGE_BASE_SHA, "--", '
            "*W04_P2_03_CI_EDITS, repo=repo),\n"
            '            "P2_03 CI source changed before '
            'validated hardening",\n'
            "        )\n"
            "        return\n"
            "    repair = w04_p2_03_r2_repair_revision(repo)\n"
            "    frozen_paths = {path: anchor for path in "
            "W04_P2_03_HARDENING_PATHS}\n"
            "    if repair is not None:\n"
            "        frozen_paths.update({path: repair for "
            "path in W04_P2_03_R2_REPAIR_PATHS})\n"
            "    for path, frozen in frozen_paths.items():\n"
            "        require(\n"
            "            (repo / path).read_bytes() == "
            'git("show", frozen + ":" + path, repo=repo)\n'
            '            and git("ls-tree", "HEAD", "--", '
            "path, repo=repo)\n"
            '            == git("ls-tree", frozen, "--", '
            "path, repo=repo)\n"
            '            and not git("diff", frozen, "--", '
            "path, repo=repo),\n"
            '            "P2_03 protected source drift: " + '
            "path,\n"
            "        )\n"
            "    for path in W04_P2_03_CI_EDITS:\n"
            "        validate_w04_p2_03_ci_sources(\n"
            "            path,\n"
            '            git("show", W04_POST_MERGE_BASE_SHA '
            '+ ":" + path, repo=repo).decode("utf-8"),\n',
        ),
        (
            "        validate_w04_p2_03_test_sources(\n"
            "            path,\n"
            '            git("show", W04_POST_MERGE_BASE_SHA '
            '+ ":" + path, repo=repo).decode("utf-8"),\n'
            "            (repo / "
            'path).read_text(encoding="utf-8"),\n'
            "        )",
            "        validate_w04_p2_03_test_sources(\n"
            "            path,\n"
            '            git("show", W04_POST_MERGE_BASE_SHA '
            '+ ":" + path, repo=repo).decode("utf-8"),\n'
            "            (repo / "
            'path).read_text(encoding="utf-8"),\n'
            "        )\n"
            "    if repair is not None:\n"
            "        validate_w04_p2_03_r2_test_sources(\n"
            '            git("show", W04_P2_03_DOC_SYNC_SHA + '
            '":tests/test_c09_ci_gate.py", '
            "repo=repo).decode(\n"
            '                "utf-8"\n'
            "            ),\n"
            "            (repo / "
            '"tests/test_c09_ci_gate.py").read_text(encoding="utf-8"),\n'
            "            repo=repo,\n"
            "        )",
        ),
    ),
    "validate_w04_pr7_merge_verifier_sources": (
        (
            '    """Validate every accepted layer '
            "first, then only the exact seven repair "
            'connectors."""\n'
            '    if "W04_POST_MERGE_BASE_SHA = " in '
            "current:\n",
            '    """Validate every accepted layer '
            "first, then only the exact seven repair "
            'connectors."""\n'
            '    if "W04_P2_03_HARDENING_SHA = " in '
            "current:\n"
            "        "
            "validate_w04_p2_03_r2_verifier_sources(review_ready, "
            "current)\n"
            "        return\n"
            '    if "W04_POST_MERGE_BASE_SHA = " in '
            "current:\n",
        ),
    ),
    "validate_w04_p2_03_meta_ci_sources": (
        (
            "        validate_w04_p2_03_test_sources(path, accepted, current)\n    else:\n",
            "        validate_w04_p2_03_test_sources(path, "
            "accepted, current)\n"
            '    elif path == "tests/test_c09_ci_gate.py" '
            "and w04_p2_03_r2_repair_revision(repo):\n"
            "        validate_w04_p2_03_r2_test_sources(\n"
            '            git("show", W04_P2_03_DOC_SYNC_SHA '
            '+ ":" + path, repo=repo).decode("utf-8"),\n'
            "            current,\n"
            "            repo=repo,\n"
            "        )\n"
            "    else:\n",
        ),
    ),
    "w04_pr7_merge_verifier_blob_guard": (
        (
            '    require(repair is not None, "missing '
            'validated PR7 merge repair")\n'
            "    frozen = w04_p2_03_hardening_revision(repo) "
            "or repair\n"
            "    validate_w04_pr7_merge_verifier_sources(\n",
            '    require(repair is not None, "missing '
            'validated PR7 merge repair")\n'
            "    hardening = "
            "w04_p2_03_hardening_revision(repo)\n"
            "    r2_repair = "
            "w04_p2_03_r2_repair_revision(repo)\n"
            "    frozen = r2_repair or hardening or repair\n"
            "    validate_w04_pr7_merge_verifier_sources(\n",
        ),
        (
            "                    "
            '"w04_post_merge_p2_03_hardening": "PASS",\n'
            '                    "w04_p2_03_hardening_sha": '
            "frozen,\n"
            '                    "w04_p2_03_controls": '
            "hardening_controls,\n",
            "                    "
            '"w04_post_merge_p2_03_hardening": "PASS",\n'
            '                    "w04_p2_03_hardening_sha": '
            "hardening,\n"
            '                    "w04_p2_03_controls": '
            "hardening_controls,\n",
        ),
        (
            "            )\n        )",
            "            )\n"
            "        )\n"
            "    if r2_repair is not None:\n"
            "        r2_controls = "
            "check_w04_p2_03_r2_controls()\n"
            "        print(\n"
            "            json.dumps(\n"
            "                {\n"
            '                    "w04_p2_03_r2_repair": '
            '"PASS",\n'
            '                    "w04_p2_03_r2_repair_sha": '
            "r2_repair,\n"
            '                    "w04_p2_03_r2_controls": '
            "r2_controls,\n"
            "                },\n"
            "                sort_keys=True,\n"
            "            )\n"
            "        )",
        ),
    ),
    "check_w04_p2_03_controls": (
        (
            '        yes("history-before", '
            "validate_w04_p2_03_history([]) is None)\n"
            "        doc = {\n"
            '            "sha": "d" * 40,\n'
            '            "parents": [hardening],\n'
            '            "subject": "docs: fixture",\n'
            '            "delta": {"README.md": "M"},\n'
            "        }\n"
            '        yes("history-docs", '
            "validate_w04_p2_03_history([valid, doc]) == hardening)\n",
            '        yes("history-before", '
            "validate_w04_p2_03_history([]) is None)\n"
            "        doc = "
            "w04_p2_03_commit_record(W04_P2_03_DOC_SYNC_SHA)\n"
            '        yes("history-docs", '
            "validate_w04_p2_03_history([valid, doc]) == "
            "hardening)\n",
        ),
        (
            '                "verifier-" + label,\n'
            "                lambda damaged=damaged: "
            "validate_w04_p2_03_verifier_sources(review, damaged),\n"
            '                "P2_03",\n',
            '                "verifier-" + label,\n'
            "                lambda damaged=damaged: "
            "validate_w04_pr7_merge_verifier_sources(review, "
            "damaged),\n"
            '                "P2_03",\n',
        ),
        (
            "                lambda: "
            "w04_p2_03_protected_source_guard(fixture),\n"
            '                "P2_03 protected source drift",\n'
            "            )\n",
            "                lambda: "
            "w04_p2_03_protected_source_guard(fixture),\n"
            '                "P2_03",\n'
            "            )\n",
        ),
        (
            "            else:\n"
            '                with patch.dict(globals(), {"ROOT": '
            'fixture, "git": fixture_git}):\n'
            "                    no(\n",
            "            else:\n"
            "                with patch.dict(\n"
            "                    globals(),\n"
            "                    {\n"
            '                        "ROOT": fixture,\n'
            '                        "git": fixture_git,\n'
            "                        "
            '"w04_p2_03_protected_source_guard": lambda: None,\n'
            "                    },\n"
            "                ):\n"
            "                    no(\n",
        ),
        (
            "            lambda: "
            "w04_p2_03_hardening_revision(fixture),\n"
            '            "P2_03 multiple hardening anchors",\n'
            "        )\n",
            "            lambda: "
            "w04_p2_03_hardening_revision(fixture),\n"
            '            "P2_03",\n'
            "        )\n",
        ),
    ),
}

W04_P2_03_R2_CONTROL_LABELS = (
    "state-1",
    "state-2",
    "state-3",
    "arbitrary-third",
    "arbitrary-fourth",
    "0-sha",
    "0-invalid-sha",
    "0-parent",
    "0-root",
    "0-merge",
    "0-subject",
    "0-missing-path",
    "0-extra-path",
    "1-sha",
    "1-invalid-sha",
    "1-parent",
    "1-root",
    "1-merge",
    "1-subject",
    "1-missing-path",
    "1-extra-path",
    "2-sha",
    "2-invalid-sha",
    "2-parent",
    "2-root",
    "2-merge",
    "2-subject",
    "2-missing-path",
    "2-extra-path",
    "0-unpinned-sha",
    "1-unpinned-sha",
    "reordered",
    "duplicate",
    "record-shape",
    "repair-missing:scripts/ci/verify_w04_investigation_gate_contract.py",
    "repair-A:scripts/ci/verify_w04_investigation_gate_contract.py",
    "repair-D:scripts/ci/verify_w04_investigation_gate_contract.py",
    "repair-R:scripts/ci/verify_w04_investigation_gate_contract.py",
    "repair-T:scripts/ci/verify_w04_investigation_gate_contract.py",
    "repair-missing:tests/test_c09_ci_gate.py",
    "repair-A:tests/test_c09_ci_gate.py",
    "repair-D:tests/test_c09_ci_gate.py",
    "repair-R:tests/test_c09_ci_gate.py",
    "repair-T:tests/test_c09_ci_gate.py",
    "repair-missing:AGENTS.md",
    "repair-A:AGENTS.md",
    "repair-D:AGENTS.md",
    "repair-R:AGENTS.md",
    "repair-T:AGENTS.md",
    "repair-missing:docs/CURRENT_STATE.md",
    "repair-A:docs/CURRENT_STATE.md",
    "repair-D:docs/CURRENT_STATE.md",
    "repair-R:docs/CURRENT_STATE.md",
    "repair-T:docs/CURRENT_STATE.md",
    "c09-stale-publication-freeze-removed",
    "c09-historical:pyproject.toml",
    "c09-historical:uv.lock",
    "c09-historical:docker-compose.yml",
    "c09-publication-e260",
    "c09-unrelated",
    "c09-extra",
    "c09-rename",
    "c09-signature",
    "c09-decorator",
    "c09-import",
    "c09-body",
    "verifier:require",
    "verifier:validate_w04_p2_03_history",
    "verifier:w04_p2_03_r2_repair_revision",
    "verifier-extra",
    "e260-freeze:scripts/ci/classify_change.py",
    "e260-freeze:scripts/ci/verify_publication.py",
    "e260-freeze:tests/test_ci_change_classifier.py",
    "e260-freeze:tests/test_ci_publication_gate.py",
    "git-doc-discovery",
    "git-doc-no-repair",
    "git-old-finding-reproduced",
    "git-old-protected-escape-reproduced",
    "git-third-rejected",
    "git-third-protected-rejected",
    "git-r2-discovery",
    "git-r2-protected",
    "git-working-drift:scripts/ci/classify_change.py",
    "git-working-drift:scripts/ci/verify_publication.py",
    "git-working-drift:scripts/ci/verify_w04_investigation_gate_contract.py",
    "git-working-drift:tests/test_ci_change_classifier.py",
    "git-working-drift:tests/test_ci_publication_gate.py",
    "git-working-drift:tests/test_c09_ci_gate.py",
    "git-working-drift:AGENTS.md",
    "git-working-drift:docs/CURRENT_STATE.md",
    "git-fourth-rejected",
    "git-fourth-repair-rejected",
    "git-frozen:.github/workflows/ci.yml",
    "git-frozen:docs/w04/checkpoints/c09/specs/c09_gate_manifest.json",
    "git-frozen:src/flowlens/investigation/__init__.py",
)

W04_P2_03_R2_SOURCE_ADDITIONS = (
    "W04_P2_03_HARDENING_SHA",
    "W04_P2_03_DOC_SYNC_SHA",
    "W04_P2_03_DOC_SYNC_SUBJECT",
    "W04_P2_03_DOC_SYNC_PATHS",
    "W04_P2_03_R2_REPAIR_SUBJECT",
    "W04_P2_03_R2_REPAIR_PATHS",
    "W04_P2_03_R2_C09_TARGET",
    "W04_P2_03_R2_CONNECTORS",
    "W04_P2_03_R2_CONTROL_LABELS",
    "W04_P2_03_R2_SOURCE_ADDITIONS",
    "w04_p2_03_r2_repair_revision",
    "validate_w04_p2_03_r2_test_sources",
    "validate_w04_p2_03_r2_verifier_sources",
    "check_w04_p2_03_r2_controls",
)


W04_P2_03_R2_SHA = "e706e1f8ed920af0e840fbb9e97725d47d79a2c6"

W04_P2_03_PR8_MERGE_REPAIR_SUBJECT = "ci(post-w04): admit PR #8 merge lifecycle"

W04_P2_03_PR8_MERGE_REPAIR_PATHS = (
    "scripts/ci/verify_w04_investigation_gate_contract.py",
    "AGENTS.md",
    "docs/CURRENT_STATE.md",
)

W04_P2_03_PR8_MERGE_CONNECTORS = {
    "validate_w04_p2_03_history": (
        (
            'require(1 <= len(history) <= 3, "P2_03 unauthorized post-base history length")',
            'require(1 <= len(history) <= 4, "P2_03 unauthorized post-base history length")',
        ),
        (
            "            None,\n"
            "            W04_P2_03_DOC_SYNC_SHA,\n"
            "            W04_P2_03_R2_REPAIR_SUBJECT,\n"
            "            W04_P2_03_R2_REPAIR_PATHS,\n"
            "        ),",
            "            W04_P2_03_R2_SHA,\n"
            "            W04_P2_03_DOC_SYNC_SHA,\n"
            "            W04_P2_03_R2_REPAIR_SUBJECT,\n"
            "            W04_P2_03_R2_REPAIR_PATHS,\n"
            "        ),\n"
            "        (\n"
            "            None,\n"
            "            W04_P2_03_R2_SHA,\n"
            "            W04_P2_03_PR8_MERGE_REPAIR_SUBJECT,\n"
            "            W04_P2_03_PR8_MERGE_REPAIR_PATHS,\n"
            "        ),",
        ),
    ),
    "w04_p2_03_hardening_revision": (
        (
            "    revisions = (\n"
            '        git("rev-list", "--reverse", "--topo-order", '
            'W04_POST_MERGE_BASE_SHA + "..HEAD", repo=repo)\n'
            '        .decode("ascii")\n'
            "        .splitlines()\n"
            "    )\n"
            "    return validate_w04_p2_03_history(\n"
            "        [w04_p2_03_commit_record(revision, repo) for "
            "revision in revisions]\n"
            "    )",
            "    history = "
            "w04_p2_03_source_history(w04_p2_03_source_tip(repo), "
            "repo)\n"
            "    return validate_w04_p2_03_history(history)",
        ),
    ),
    "w04_p2_03_r2_repair_revision": (
        (
            "    revisions = (\n"
            '        git("rev-list", "--reverse", "--topo-order", '
            'W04_POST_MERGE_BASE_SHA + "..HEAD", repo=repo)\n'
            '        .decode("ascii")\n'
            "        .splitlines()\n"
            "    )\n"
            "    return revisions[2] if len(revisions) == 3 else None",
            "    history = "
            "w04_p2_03_source_history(w04_p2_03_source_tip(repo), "
            "repo)\n"
            '    return cast(str, history[2]["sha"]) if len(history) >= '
            "3 else None",
        ),
    ),
    "w04_p2_03_protected_source_guard": (
        (
            "        frozen_paths.update({path: repair for path in "
            "W04_P2_03_R2_REPAIR_PATHS})\n"
            "    for path, frozen in frozen_paths.items():",
            "        frozen_paths.update({path: repair for path in "
            "W04_P2_03_R2_REPAIR_PATHS})\n"
            "    pr8_repair = "
            "w04_p2_03_pr8_merge_repair_revision(repo)\n"
            "    if pr8_repair is not None:\n"
            "        frozen_paths.update({path: pr8_repair for path "
            "in W04_P2_03_PR8_MERGE_REPAIR_PATHS})\n"
            "        if w04_p2_03_pr8_integration_anchor(repo) is "
            "not None:\n"
            '            frozen_paths.pop("AGENTS.md")\n'
            '            frozen_paths.pop("docs/CURRENT_STATE.md")\n'
            "    for path, frozen in frozen_paths.items():",
        ),
    ),
    "validate_w04_p2_03_r2_verifier_sources": (
        (
            '    """Execute the accepted R1 chain, then admit '
            'only literal R2 connectors/additions."""\n',
            '    """Execute the accepted R1 chain, then admit '
            'only literal R2 connectors/additions."""\n'
            '    if "W04_P2_03_R2_SHA = " in current:\n'
            "        "
            "validate_w04_p2_03_pr8_verifier_sources(review_ready, "
            "current)\n"
            "        return\n",
        ),
    ),
    "w04_pr7_merge_verifier_blob_guard": (
        (
            "    frozen = r2_repair or hardening or repair\n",
            "    pr8_repair = "
            "w04_p2_03_pr8_merge_repair_revision(repo)\n"
            "    frozen = pr8_repair or r2_repair or hardening or "
            "repair\n",
        ),
        (
            '                  "w04_p2_03_r2_repair": "PASS",\n'
            '                    "w04_p2_03_r2_repair_sha": '
            "r2_repair,\n"
            '                    "w04_p2_03_r2_controls": '
            "r2_controls,\n"
            "                },\n"
            "                sort_keys=True,\n"
            "            )\n"
            "        )\n",
            '                  "w04_p2_03_r2_repair": "PASS",\n'
            '                    "w04_p2_03_r2_repair_sha": '
            "r2_repair,\n"
            '                    "w04_p2_03_r2_controls": '
            "r2_controls,\n"
            "                },\n"
            "                sort_keys=True,\n"
            "            )\n"
            "        )\n"
            "    if pr8_repair is not None:\n"
            "        pr8_controls = "
            "check_w04_p2_03_pr8_merge_controls()\n"
            "        print(\n"
            "            json.dumps(\n"
            "                {\n"
            '                    "w04_p2_03_pr8_merge_repair": '
            '"PASS",\n'
            '                    "w04_p2_03_pr8_merge_repair_sha": '
            "pr8_repair,\n"
            '                    "w04_p2_03_pr8_merge_controls": '
            "pr8_controls,\n"
            '                    "w04_p2_03_pr8_lifecycle": '
            "w04_p2_03_pr8_lifecycle(repo),\n"
            '                    "w04_p2_03_source_tip": '
            "w04_p2_03_source_tip(repo),\n"
            "                    "
            '"w04_p2_03_pr8_integration_anchor": '
            "w04_p2_03_pr8_integration_anchor(repo),\n"
            "                },\n"
            "                sort_keys=True,\n"
            "            )\n"
            "        )\n",
        ),
    ),
}

W04_P2_03_PR8_MERGE_CONTROL_LABELS = (
    "state-0",
    "state-1",
    "state-2",
    "state-3",
    "state-4",
    "arbitrary-fourth",
    "arbitrary-fifth",
    "unpinned-e706",
    "r4-sha-zero",
    "r4-sha-malformed",
    "r4-sha-duplicate",
    "r4-parent",
    "r4-root",
    "r4-merge",
    "r4-subject",
    "r4-extra-path",
    "r4-missing:scripts/ci/verify_w04_investigation_gate_contract.py",
    "r4-A:scripts/ci/verify_w04_investigation_gate_contract.py",
    "r4-D:scripts/ci/verify_w04_investigation_gate_contract.py",
    "r4-R:scripts/ci/verify_w04_investigation_gate_contract.py",
    "r4-T:scripts/ci/verify_w04_investigation_gate_contract.py",
    "r4-missing:AGENTS.md",
    "r4-A:AGENTS.md",
    "r4-D:AGENTS.md",
    "r4-R:AGENTS.md",
    "r4-T:AGENTS.md",
    "r4-missing:docs/CURRENT_STATE.md",
    "r4-A:docs/CURRENT_STATE.md",
    "r4-D:docs/CURRENT_STATE.md",
    "r4-R:docs/CURRENT_STATE.md",
    "r4-T:docs/CURRENT_STATE.md",
    "reordered",
    "record-shape",
    "nonrecursive:w04_p2_03_source_history",
    "nonrecursive:w04_p2_03_pr8_integration_anchor",
    "source-chain",
    "source:require",
    "source:validate_w04_p2_03_history",
    "source:w04_p2_03_source_history",
    "source:w04_p2_03_pr8_integration_anchor",
    "source:w04_p2_03_source_tip",
    "source:w04_p2_03_protected_source_guard",
    "source:validate_w04_p2_03_pr8_verifier_sources",
    "source-extra",
    "current-protected",
    "git-state-0",
    "git-state-1",
    "git-state-2",
    "git-state-3",
    "git-state-4",
    "git-fourth-rejected",
    "git-fifth-rejected",
    "pre-protected:scripts/ci/classify_change.py",
    "pre-protected:scripts/ci/verify_publication.py",
    "pre-protected:tests/test_ci_change_classifier.py",
    "pre-protected:tests/test_ci_publication_gate.py",
    "pre-protected:tests/test_c09_ci_gate.py",
    "pre-protected:scripts/ci/verify_w04_investigation_gate_contract.py",
    "pre-protected:AGENTS.md",
    "pre-protected:docs/CURRENT_STATE.md",
    "topology-positive",
    "topology-wrong-main",
    "topology-wrong-feature",
    "topology-direct-e706",
    "topology-reversed",
    "topology-octopus",
    "topology-root",
    "topology-single",
    "topology-tree",
    "topology-delta",
    "topology-unreachable",
    "git-wrong-main",
    "git-wrong-feature",
    "git-direct-e706",
    "git-reversed",
    "git-octopus",
    "git-anchor",
    "git-merge-tip",
    "git-merge-lifecycle",
    "post-protected:scripts/ci/classify_change.py",
    "post-protected:scripts/ci/verify_publication.py",
    "post-protected:tests/test_ci_change_classifier.py",
    "post-protected:tests/test_ci_publication_gate.py",
    "post-protected:tests/test_c09_ci_gate.py",
    "post-protected:scripts/ci/verify_w04_investigation_gate_contract.py",
    "git-real-nonempty-delta",
    "git-tree-drift",
    "git-docs-protected",
    "git-docs-tip",
    "git-docs-lifecycle",
    "git-later-merge-tip",
    "git-later-merge-anchor",
    "git-later-merge-lifecycle",
    "git-nonprotected-tip",
    "git-nonprotected-anchor",
    "git-nonprotected-lifecycle",
    "git-post-runtime-drift",
    "git-multiple-anchors",
)

W04_P2_03_PR8_MERGE_SOURCE_ADDITIONS = (
    "W04_P2_03_R2_SHA",
    "W04_P2_03_PR8_MERGE_REPAIR_SUBJECT",
    "W04_P2_03_PR8_MERGE_REPAIR_PATHS",
    "W04_P2_03_PR8_MERGE_CONNECTORS",
    "W04_P2_03_PR8_MERGE_CONTROL_LABELS",
    "W04_P2_03_PR8_MERGE_SOURCE_ADDITIONS",
    "w04_p2_03_source_history",
    "validate_w04_p2_03_pr8_merge_topology",
    "w04_p2_03_pr8_integration_anchor",
    "w04_p2_03_source_tip",
    "w04_p2_03_pr8_merge_repair_revision",
    "w04_p2_03_pr8_lifecycle",
    "validate_w04_p2_03_pr8_verifier_sources",
    "check_w04_p2_03_pr8_merge_controls",
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
        validate_w04_p2_03_meta_ci_sources(
            path,
            git("show", ENTRY + ":" + path, repo=repo).decode(),
            (repo / path).read_text(encoding="utf-8"),
            repo=repo,
        )


def check_meta_ci_source_controls() -> int:
    for path, allowed in AUTHORIZED_META_CI_FUNCTIONS.items():
        entry = git("show", ENTRY + ":" + path).decode()
        current = (ROOT / path).read_text(encoding="utf-8")
        validate_w04_p2_03_meta_ci_sources(path, entry, current)
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
                lambda damaged=damaged, path=path, entry=entry: validate_w04_p2_03_meta_ci_sources(
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


def validate_c10_lifecycle(
    history: list[dict[str, Any]], working: set[str], changed: set[str]
) -> str:
    """Extend only the exact accepted C09 Final by three single-parent C10 children."""
    if len(history) > 7:
        return validate_c10_closeout_lifecycle(history, working, changed)
    require(5 <= len(history) <= 7, "extra post-C10_REVIEW_READY commit")
    base = set(STAGE_A) | set(STAGE_B) | set(CLOSEOUT_FINAL_PATHS)
    require(
        validate_closeout_lifecycle(history[:4], set(), base) == "FINAL_CLOSEOUT",
        "C10 requires the complete accepted C09 lifecycle",
    )
    require(
        history[2]["sha"] == C10_PREP_SHA and history[3]["sha"] == C10_ENTRY_SHA,
        "C10 exact accepted C09 Prep/Final anchors drift",
    )
    for record in history[4:]:
        require(set(record) == {"sha", "parents", "subject", "delta"}, "C10 record shape")
        require(
            re.fullmatch(r"[0-9a-f]{40}", record["sha"]) is not None and record["sha"] != "0" * 40,
            "invalid C10 lifecycle SHA",
        )
    require(len({r["sha"] for r in history}) == len(history), "duplicate C10 lifecycle SHA")
    bootstrap = history[4]
    require(
        bootstrap["parents"] == [C10_ENTRY_SHA]
        and bootstrap["subject"] == C10_BOOTSTRAP_SUBJECT
        and bootstrap["delta"] == {CLOSEOUT_VERIFIER_PATH: "M"},
        "invalid exact C10 Bootstrap parent/subject/delta",
    )
    state, expected = "C10_BOOTSTRAP_01", base.copy()
    if len(history) >= 6:
        stage_a = history[5]
        require(
            stage_a["parents"] == [bootstrap["sha"]]
            and stage_a["subject"] == C10_STAGE_A_SUBJECT
            and stage_a["delta"] == dict.fromkeys(C10_STAGE_A_PATHS, "A"),
            "invalid exact C10 Stage-A parent/subject/delta",
        )
        state = "C10_STAGE_A"
        expected.update(C10_STAGE_A_PATHS)
    if len(history) == 7:
        stage_b = history[6]
        require(
            stage_b["parents"] == [history[5]["sha"]]
            and stage_b["subject"] == C10_STAGE_B_SUBJECT
            and stage_b["delta"] == {C10_STAGE_B_PATH: "A"},
            "invalid exact C10 Stage-B parent/subject/delta",
        )
        state = "C10_REVIEW_READY"
        expected.add(C10_STAGE_B_PATH)
    require(changed == expected, "C10 cumulative path-set drift")
    require(not working, "uncommitted C10 lifecycle delta")
    return state


def c10_bootstrap_revision(repo: Path = ROOT) -> str:
    """Derive the Bootstrap only after validating the full committed lifecycle."""
    changed = set(git("diff", "--name-only", ENTRY, "--", repo=repo).decode().splitlines())
    changed.update(
        git("ls-files", "--others", "--exclude-standard", repo=repo).decode().splitlines()
    )
    state = closeout_lifecycle_guard(changed, repo=repo)
    require(
        state
        in {
            "C10_BOOTSTRAP_01",
            "C10_STAGE_A",
            "C10_REVIEW_READY",
            "C10_CLOSEOUT_PREP_01",
            "C10_FINAL_CLOSEOUT",
            "W04_SPRINT_CLOSEOUT_PREP_01",
            "W04_SPRINT_FINAL_CLOSEOUT",
            "W04_PR7_MERGE_REPAIR_01",
            "W04_PR7_MERGED_MAIN",
            "W04_POST_MERGE_INTEGRATED",
        },
        "no validated C10 Bootstrap",
    )
    revisions = (
        git("rev-list", "--reverse", C10_ENTRY_SHA + ".." + w04_pr7_historical_tip(repo), repo=repo)
        .decode()
        .splitlines()
    )
    require(1 <= len(revisions) <= 7, "invalid C10 Bootstrap derivation")
    return revisions[0]


def validate_c10_verifier_sources(review_ready: str, current: str) -> None:
    """Bind legacy spans to C09 Final and all added spans to the validated Bootstrap."""
    if "C10_CLOSEOUT_REVIEW_READY_SHA = " in current:
        validate_c10_closeout_verifier_sources(review_ready, current)
        return
    final = git("show", C10_ENTRY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    validate_verifier_sources(review_ready, final)
    old_order, old = source_units(final)
    new_order, new = source_units(current)
    additions = set(C10_SOURCE_ADDITIONS)
    require(set(new) - set(old) == additions, "unauthorized C10 verifier unit addition/removal")
    require(
        [name for name in new_order if name not in additions] == old_order
        and [name for name in new_order if name in additions] == list(C10_SOURCE_ADDITIONS),
        "C10 verifier source-unit order drift",
    )
    for name in old_order:
        require(name in new, "removed C09 verifier unit")
        expected = old[name][0].encode()
        if name == "validate_closeout_lifecycle":
            expected = replace_once(
                expected,
                b'    require(1 <= len(history) <= 4, "extra post-REVIEW_READY commit")\n',
                b"    if len(history) > 4:\n"
                b"        return validate_c10_lifecycle(history, working, changed)\n"
                b'    require(1 <= len(history) <= 4, "extra post-REVIEW_READY commit")\n',
            )
        elif name == "validate_verifier_sources":
            expected = replace_once(
                expected,
                b"    if current == review_ready:\n",
                b'    if "C10_ENTRY_SHA = " in current:\n'
                b"        validate_c10_verifier_sources(review_ready, current)\n"
                b"        return\n"
                b"    if current == review_ready:\n",
            )
        elif name == "verifier_source_guard":
            expected = replace_once(
                expected,
                b'    current = (repo / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")\n',
                b'    current = (repo / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")\n'
                b"    c10_verifier_blob_guard(repo)\n",
            )
        require(new[name][0].encode() == expected, f"unauthorized C10 verifier span: {name}")
    bootstrap = git("show", c10_bootstrap_revision() + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    committed_order, committed = source_units(bootstrap)
    require(new_order == committed_order, "Bootstrap source-unit placement drift")
    for name in C10_SOURCE_ADDITIONS:
        require(new[name][0] == committed[name][0], f"C10 Bootstrap source-span drift: {name}")
    constants: dict[str, object] = {
        "C10_ENTRY_SHA": "d33ee858fca8caaceba2ce60c045f7e4213c631a",
        "C10_PREP_SHA": "f391cf25871473d488a8f5c7e7ff77fb933920d8",
        "C10_BOOTSTRAP_SUBJECT": "ci(w04-c10): admit bounded acceptance lifecycle",
        "C10_STAGE_A_SUBJECT": "docs(w04-c10): prepare investigation business acceptance",
        "C10_STAGE_B_SUBJECT": "docs(w04-c10): publish business acceptance readiness proof",
        "C10_STAGE_A_PATHS": (
            "docs/w04/checkpoints/c10/W04_C10_AUTHORIZATION_CONTRACT.md",
            "docs/w04/checkpoints/c10/W04_C10_HUMAN_AUTHORIZATION.md",
            "docs/w04/checkpoints/c10/W04_C10_CONTEXT_LOCK.md",
            "docs/w04/checkpoints/c10/W04_C10_BUSINESS_ACCEPTANCE_SPEC.md",
            "docs/w04/checkpoints/c10/W04_C10_EVIDENCE_MATRIX.md",
            "docs/w04/checkpoints/c10/W04_C10_HUMAN_ACCEPTANCE_FORM.md",
            "docs/w04/checkpoints/c10/W04_C10_HARNESS_SPEC.md",
            "docs/w04/checkpoints/c10/W04_C10_GPT_REVIEW_CHECKLIST.md",
            "docs/w04/checkpoints/c10/W04_C10_BUSINESS_ACCEPTANCE_DOSSIER.md",
            "docs/w04/checkpoints/c10/specs/c10_acceptance_manifest.json",
            "docs/w04/checkpoints/c10/specs/authorized_paths.json",
        ),
        "C10_STAGE_B_PATH": "docs/w04/checkpoints/c10/W04_C10_R_DEVELOPMENT_ROUND_REPORT.md",
    }
    for name, value in constants.items():
        node = new[name][1]
        require(isinstance(node, ast.Assign), "C10 constant declaration drift")
        require(ast.literal_eval(cast(ast.Assign, node).value) == value, "C10 constant value drift")


def c10_verifier_blob_guard(repo: Path = ROOT) -> None:
    if c10_closeout_prep_revision(repo) is not None:
        c10_closeout_verifier_blob_guard(repo)
        return
    bootstrap = c10_bootstrap_revision(repo)
    require(
        (repo / CLOSEOUT_VERIFIER_PATH).read_bytes()
        == git("show", bootstrap + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo),
        "C10 verifier must remain byte-identical to Bootstrap",
    )
    controls = check_c10_lifecycle_controls()
    print(
        json.dumps(
            {"c10_bootstrap_sha": bootstrap, "c10_adversarial_controls": controls}, sort_keys=True
        )
    )


def check_c10_lifecycle_controls() -> int:
    """C10 positive states and exact lifecycle/source adversaries; no pytest node changes."""
    history: list[dict[str, Any]] = [
        {
            "sha": CLOSEOUT_STAGE_A_SHA,
            "parents": [ENTRY],
            "subject": "ci(w04-c09): add investigation regression gate",
            "delta": dict.fromkeys(STAGE_A, "A"),
        },
        {
            "sha": CLOSEOUT_REVIEW_READY_SHA,
            "parents": [CLOSEOUT_STAGE_A_SHA],
            "subject": "docs(w04-c09): publish regression-hardening proof",
            "delta": dict.fromkeys(STAGE_B, "A"),
        },
        {
            "sha": C10_PREP_SHA,
            "parents": [CLOSEOUT_REVIEW_READY_SHA],
            "subject": CLOSEOUT_PREP_SUBJECT,
            "delta": {CLOSEOUT_VERIFIER_PATH: "M"},
        },
        {
            "sha": C10_ENTRY_SHA,
            "parents": [C10_PREP_SHA],
            "subject": CLOSEOUT_FINAL_SUBJECT,
            "delta": dict.fromkeys(CLOSEOUT_FINAL_PATHS, "A"),
        },
        {
            "sha": "c" * 40,
            "parents": [C10_ENTRY_SHA],
            "subject": C10_BOOTSTRAP_SUBJECT,
            "delta": {CLOSEOUT_VERIFIER_PATH: "M"},
        },
        {
            "sha": "d" * 40,
            "parents": ["c" * 40],
            "subject": C10_STAGE_A_SUBJECT,
            "delta": dict.fromkeys(C10_STAGE_A_PATHS, "A"),
        },
        {
            "sha": "e" * 40,
            "parents": ["d" * 40],
            "subject": C10_STAGE_B_SUBJECT,
            "delta": {C10_STAGE_B_PATH: "A"},
        },
    ]
    base = set(STAGE_A) | set(STAGE_B) | set(CLOSEOUT_FINAL_PATHS)
    sets = (base, base | set(C10_STAGE_A_PATHS), base | set(C10_STAGE_A_PATHS) | {C10_STAGE_B_PATH})
    for size, state in enumerate(("C10_BOOTSTRAP_01", "C10_STAGE_A", "C10_REVIEW_READY"), 5):
        require(validate_closeout_lifecycle(history[:size], set(), sets[size - 5]) == state, state)
    mutations: list[tuple[str, int, int, str, Any]] = [
        ("wrong Bootstrap parent", 5, 4, "parents", [C10_PREP_SHA]),
        ("wrong Bootstrap subject", 5, 4, "subject", "ci: unapproved"),
        ("extra Bootstrap path", 5, 4, "delta", {CLOSEOUT_VERIFIER_PATH: "M", "extra": "A"}),
        ("missing verifier modification", 5, 4, "delta", {}),
        ("merge Bootstrap", 5, 4, "parents", [C10_ENTRY_SHA, C10_PREP_SHA]),
        ("wrong Stage-A parent", 6, 5, "parents", [C10_ENTRY_SHA]),
        ("wrong Stage-A subject", 6, 5, "subject", "docs: unapproved"),
        ("missing Stage-A document", 6, 5, "delta", dict.fromkeys(C10_STAGE_A_PATHS[:-1], "A")),
        ("extra Stage-A document", 6, 5, "delta", {**history[5]["delta"], "extra": "A"}),
        ("modified Stage-A document", 6, 5, "delta", dict.fromkeys(C10_STAGE_A_PATHS, "M")),
        (
            "mixed C09/C10 mutation",
            6,
            5,
            "delta",
            {**history[5]["delta"], CLOSEOUT_FINAL_PATHS[0]: "M"},
        ),
        (
            "verifier changed in Stage A",
            6,
            5,
            "delta",
            {**history[5]["delta"], CLOSEOUT_VERIFIER_PATH: "M"},
        ),
        ("wrong Stage-B parent", 7, 6, "parents", ["c" * 40]),
        ("wrong Stage-B subject", 7, 6, "subject", "docs: unapproved"),
        ("wrong Stage-B report path", 7, 6, "delta", {"docs/w04/other-report.md": "A"}),
        ("extra Stage-B path", 7, 6, "delta", {C10_STAGE_B_PATH: "A", "extra": "A"}),
        ("modified Stage-B report", 7, 6, "delta", {C10_STAGE_B_PATH: "M"}),
        (
            "verifier changed in Stage B",
            7,
            6,
            "delta",
            {C10_STAGE_B_PATH: "A", CLOSEOUT_VERIFIER_PATH: "M"},
        ),
        (
            "C09 final document mutation",
            5,
            4,
            "delta",
            {CLOSEOUT_VERIFIER_PATH: "M", CLOSEOUT_FINAL_PATHS[0]: "M"},
        ),
        (
            "C01-C08 protected object mutation",
            5,
            4,
            "delta",
            {CLOSEOUT_VERIFIER_PATH: "M", "src/flowlens/investigation/contracts.py": "M"},
        ),
        (
            "source-manifest mutation",
            5,
            4,
            "delta",
            {CLOSEOUT_VERIFIER_PATH: "M", "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json": "M"},
        ),
        ("second Bootstrap", 6, 5, "subject", C10_BOOTSTRAP_SUBJECT),
        ("merge Stage A", 6, 5, "parents", ["c" * 40, C10_ENTRY_SHA]),
        ("merge Stage B", 7, 6, "parents", ["d" * 40, "c" * 40]),
        ("renamed Stage-A document", 6, 5, "delta", dict.fromkeys(C10_STAGE_A_PATHS, "R100")),
    ]
    for label, size, index, field, value in mutations:
        damaged = copy.deepcopy(history[:size])
        damaged[index][field] = value
        rejected(
            label,
            lambda damaged=damaged, size=size: validate_closeout_lifecycle(
                damaged, set(), sets[size - 5]
            ),
        )
    for label, damaged, working, changed in (
        ("extra commit after C10_REVIEW_READY", [*history, history[6]], set(), sets[2]),
        ("working verifier mutation", history[:5], {CLOSEOUT_VERIFIER_PATH}, sets[0]),
        ("C10 cumulative path drift", history[:6], set(), sets[1] | {"extra"}),
    ):
        rejected(
            label,
            lambda damaged=damaged, working=working, changed=changed: validate_closeout_lifecycle(
                damaged, working, changed
            ),
        )
    original = git("show", CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    current = (ROOT / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")
    order, units = source_units(current)
    lines = current.splitlines(keepends=True)
    source_mutations = [current + "\ndef unauthorized_c10_unit():\n    pass\n"]
    for name in ("require", "validate_c10_lifecycle", "validate_c10_verifier_sources"):
        unit, parsed = units[name]
        node = cast(ast.stmt, parsed)
        require(node.end_lineno is not None, "C10 adversary end span")
        start, end = node.lineno - 1, node.end_lineno
        require("".join(lines[start:end]) == unit, "C10 adversary exact source span")
        damaged_source = "".join(lines[:start]) + unit + "    pass\n" + "".join(lines[end:])
        after_order, after = source_units(damaged_source)
        require(after_order == order, "C10 adversary changed unit identities/order")
        require(all(after[k][0] == units[k][0] for k in order if k != name), "unrelated span drift")
        require(after[name][0] != unit, "C10 source adversary was a no-op")
        source_mutations.append(damaged_source)
    for damaged_source in source_mutations:
        rejected(
            "unauthorized C10 source unit/span",
            lambda damaged_source=damaged_source: validate_verifier_sources(
                original, damaged_source
            ),
        )
    return len(mutations) + 3 + len(source_mutations)
def validate_c10_closeout_lifecycle(
    history: list[dict[str, Any]], working: set[str], changed: set[str]
) -> str:
    """Admit only one Prep and its five-document Final after accepted C10 review."""
    if len(history) > 9:
        return validate_w04_sprint_lifecycle(history, working, changed)
    require(8 <= len(history) <= 9, "extra post-C10_FINAL_CLOSEOUT commit")
    base = set(STAGE_A) | set(STAGE_B) | set(CLOSEOUT_FINAL_PATHS)
    base.update(C10_STAGE_A_PATHS)
    base.add(C10_STAGE_B_PATH)
    require(
        validate_c10_lifecycle(history[:7], set(), base) == "C10_REVIEW_READY",
        "C10 closeout requires the complete development lifecycle",
    )
    require(
        [row["sha"] for row in history[4:7]]
        == [C10_CLOSEOUT_BOOTSTRAP_SHA, C10_CLOSEOUT_STAGE_A_SHA, C10_CLOSEOUT_REVIEW_READY_SHA],
        "C10 closeout immutable development anchors drift",
    )
    for record in history[7:]:
        require(set(record) == {"sha", "parents", "subject", "delta"}, "C10 closeout record shape")
        require(
            isinstance(record["sha"], str)
            and re.fullmatch(r"[0-9a-f]{40}", record["sha"]) is not None
            and record["sha"] != "0" * 40,
            "invalid C10 closeout SHA",
        )
    require(len({row["sha"] for row in history}) == len(history), "duplicate C10 closeout SHA")
    prep = history[7]
    require(
        prep["parents"] == [C10_CLOSEOUT_REVIEW_READY_SHA]
        and prep["subject"] == C10_CLOSEOUT_PREP_SUBJECT
        and prep["delta"] == {CLOSEOUT_VERIFIER_PATH: "M"},
        "invalid exact C10 closeout Prep parent/subject/delta",
    )
    state, expected = "C10_CLOSEOUT_PREP_01", base.copy()
    if len(history) == 9:
        final = history[8]
        require(
            final["parents"] == [prep["sha"]]
            and final["subject"] == C10_FINAL_CLOSEOUT_SUBJECT
            and final["delta"] == dict.fromkeys(C10_FINAL_CLOSEOUT_PATHS, "A"),
            "invalid exact C10 final-closeout parent/subject/delta",
        )
        state = "C10_FINAL_CLOSEOUT"
        expected.update(C10_FINAL_CLOSEOUT_PATHS)
    require(changed == expected, "C10 closeout cumulative path-set drift")
    require(not working, "uncommitted C10 closeout lifecycle delta")
    return state


def c10_closeout_prep_revision(repo: Path = ROOT) -> str | None:
    """Derive a Prep only from the validated exact accepted development chain."""
    revisions = (
        git("rev-list", "--reverse", C10_ENTRY_SHA + ".." + w04_pr7_historical_tip(repo), repo=repo)
        .decode()
        .splitlines()
    )
    if len(revisions) <= 3:
        return None
    changed = set(git("diff", "--name-only", ENTRY, "--", repo=repo).decode().splitlines())
    changed.update(
        git("ls-files", "--others", "--exclude-standard", repo=repo).decode().splitlines()
    )
    state = closeout_lifecycle_guard(changed, repo=repo)
    require(
        state
        in {
            "C10_CLOSEOUT_PREP_01",
            "C10_FINAL_CLOSEOUT",
            "W04_SPRINT_CLOSEOUT_PREP_01",
            "W04_SPRINT_FINAL_CLOSEOUT",
            "W04_PR7_MERGE_REPAIR_01",
            "W04_PR7_MERGED_MAIN",
            "W04_POST_MERGE_INTEGRATED",
        }
        and 4 <= len(revisions) <= 7
        and revisions[2] == C10_CLOSEOUT_REVIEW_READY_SHA,
        "no validated C10 closeout Prep",
    )
    return revisions[3]


def validate_c10_closeout_verifier_sources(review_ready: str, current: str) -> None:
    """Preserve all accepted spans except four exact C10 closeout connectors."""
    if "W04_SPRINT_ENTRY_SHA = " in current:
        validate_w04_sprint_verifier_sources(review_ready, current)
        return
    accepted = git("show", C10_CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    validate_c10_verifier_sources(review_ready, accepted)
    old_order, old = source_units(accepted)
    new_order, new = source_units(current)
    additions = set(C10_CLOSEOUT_SOURCE_ADDITIONS)
    require(set(new) - set(old) == additions, "unauthorized C10 closeout unit addition/removal")
    require(
        [name for name in new_order if name not in additions] == old_order
        and [name for name in new_order if name in additions]
        == list(C10_CLOSEOUT_SOURCE_ADDITIONS),
        "C10 closeout source-unit order drift",
    )
    replacements = {
        "validate_c10_lifecycle": [
            (
                b'    require(5 <= len(history) <= 7, "extra post-C10_REVIEW_READY commit")\n',
                b"    if len(history) > 7:\n"
                b"        return validate_c10_closeout_lifecycle(history, working, changed)\n"
                b'    require(5 <= len(history) <= 7, "extra post-C10_REVIEW_READY commit")\n',
            )
        ],
        "c10_bootstrap_revision": [
            (
                b'        state in {"C10_BOOTSTRAP_01", "C10_STAGE_A", "C10_REVIEW_READY"},\n',
                b"        state\n"
                b"        in {\n"
                b'            "C10_BOOTSTRAP_01",\n'
                b'            "C10_STAGE_A",\n'
                b'            "C10_REVIEW_READY",\n'
                b'            "C10_CLOSEOUT_PREP_01",\n'
                b'            "C10_FINAL_CLOSEOUT",\n'
                b"        },\n",
            ),
            (
                b'    require(1 <= len(revisions) <= 3, "invalid C10 Bootstrap derivation")\n',
                b'    require(1 <= len(revisions) <= 5, "invalid C10 Bootstrap derivation")\n',
            ),
        ],
        "validate_c10_verifier_sources": [
            (
                b'    final = git("show", C10_ENTRY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()\n',
                b'    if "C10_CLOSEOUT_REVIEW_READY_SHA = " in current:\n'
                b"        validate_c10_closeout_verifier_sources(review_ready, current)\n"
                b"        return\n"
                b'    final = git("show", C10_ENTRY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()\n',
            )
        ],
        "c10_verifier_blob_guard": [
            (
                b"    bootstrap = c10_bootstrap_revision(repo)\n",
                b"    if c10_closeout_prep_revision(repo) is not None:\n"
                b"        c10_closeout_verifier_blob_guard(repo)\n"
                b"        return\n"
                b"    bootstrap = c10_bootstrap_revision(repo)\n",
            )
        ],
    }
    for name in old_order:
        expected = old[name][0].encode()
        for before, after in replacements.get(name, []):
            expected = replace_once(expected, before, after)
        require(new[name][0].encode() == expected, f"unauthorized C10 closeout span: {name}")
    prep = c10_closeout_prep_revision()
    require(prep is not None, "C10 closeout source requires committed Prep")
    committed_order, committed = source_units(
        git("show", str(prep) + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    )
    require(new_order == committed_order, "C10 Prep source-unit placement drift")
    for name in C10_CLOSEOUT_SOURCE_ADDITIONS:
        require(new[name][0] == committed[name][0], f"C10 Prep source-span drift: {name}")
    constants: dict[str, object] = {
        "C10_CLOSEOUT_REVIEW_READY_SHA": "250ea1b7476db61aba20b5d2fb11148ce8243678",
        "C10_CLOSEOUT_BOOTSTRAP_SHA": "a34a84b97681f24bf6df1fed1a80825ae32decfa",
        "C10_CLOSEOUT_STAGE_A_SHA": "59ec925122c1fdc5b76a3c22fc0ab60a785efb38",
        "C10_CLOSEOUT_PREP_SUBJECT": "ci(w04-c10): admit bounded closeout lifecycle",
        "C10_FINAL_CLOSEOUT_SUBJECT": "docs(w04-c10): close business acceptance checkpoint",
        "C10_FINAL_CLOSEOUT_PATHS": (
            "docs/w04/checkpoints/c10/W04_C10_GPT_INDEPENDENT_REVIEW_R1.md",
            "docs/w04/checkpoints/c10/W04_C10_HUMAN_ACCEPTANCE.md",
            "docs/w04/checkpoints/c10/W04_C10_CLOSEOUT_AUTHORIZATION.md",
            "docs/w04/checkpoints/c10/W04_C10_CLOSEOUT_CONTEXT_LOCK.md",
            "docs/w04/checkpoints/c10/W04_C10_FINAL_CLOSEOUT_REPORT.md",
        ),
        "C10_CLOSEOUT_SOURCE_ADDITIONS": (
            "C10_CLOSEOUT_REVIEW_READY_SHA",
            "C10_CLOSEOUT_BOOTSTRAP_SHA",
            "C10_CLOSEOUT_STAGE_A_SHA",
            "C10_CLOSEOUT_PREP_SUBJECT",
            "C10_FINAL_CLOSEOUT_SUBJECT",
            "C10_FINAL_CLOSEOUT_PATHS",
            "C10_CLOSEOUT_SOURCE_ADDITIONS",
            "validate_c10_closeout_lifecycle",
            "c10_closeout_prep_revision",
            "validate_c10_closeout_verifier_sources",
            "c10_closeout_verifier_blob_guard",
            "check_c10_closeout_lifecycle_controls",
        ),
    }
    for name, value in constants.items():
        node = new[name][1]
        require(isinstance(node, ast.Assign), "C10 closeout constant declaration drift")
        require(
            ast.literal_eval(cast(ast.Assign, node).value) == value, "C10 closeout constant drift"
        )


def c10_closeout_verifier_blob_guard(repo: Path = ROOT) -> None:
    if w04_sprint_prep_revision(repo) is not None:
        w04_sprint_verifier_blob_guard(repo)
        return
    prep = c10_closeout_prep_revision(repo)
    require(prep is not None, "missing validated C10 closeout Prep")
    require(
        (repo / CLOSEOUT_VERIFIER_PATH).read_bytes()
        == git("show", str(prep) + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo),
        "C10 closeout verifier must remain byte-identical to Prep",
    )
    development_controls = check_c10_lifecycle_controls()
    require(development_controls == 32, "C10 development adversarial control drift")
    print(
        json.dumps(
            {
                "c10_bootstrap_sha": C10_CLOSEOUT_BOOTSTRAP_SHA,
                "c10_adversarial_controls": development_controls,
            },
            sort_keys=True,
        )
    )
    controls = check_c10_closeout_lifecycle_controls()
    print(
        json.dumps(
            {"c10_closeout_prep_sha": prep, "c10_closeout_adversarial_controls": controls},
            sort_keys=True,
        )
    )


def check_c10_closeout_lifecycle_controls() -> int:
    revisions = (
        CLOSEOUT_STAGE_A_SHA,
        CLOSEOUT_REVIEW_READY_SHA,
        C10_PREP_SHA,
        C10_ENTRY_SHA,
        C10_CLOSEOUT_BOOTSTRAP_SHA,
        C10_CLOSEOUT_STAGE_A_SHA,
        C10_CLOSEOUT_REVIEW_READY_SHA,
    )
    history: list[dict[str, Any]] = []
    for revision in revisions:
        parent = git("show", "-s", "--format=%P", revision).decode().split()
        delta = {}
        for row in (
            git("diff", "--name-status", "--no-renames", parent[0], revision).decode().splitlines()
        ):
            status, path = row.split("\t")
            delta[path] = status
        history.append(
            {
                "sha": revision,
                "parents": parent,
                "subject": git("show", "-s", "--format=%s", revision).decode().strip(),
                "delta": delta,
            }
        )
    history.extend(
        [
            {
                "sha": "f" * 40,
                "parents": [C10_CLOSEOUT_REVIEW_READY_SHA],
                "subject": C10_CLOSEOUT_PREP_SUBJECT,
                "delta": {CLOSEOUT_VERIFIER_PATH: "M"},
            },
            {
                "sha": "b" * 40,
                "parents": ["f" * 40],
                "subject": C10_FINAL_CLOSEOUT_SUBJECT,
                "delta": dict.fromkeys(C10_FINAL_CLOSEOUT_PATHS, "A"),
            },
        ]
    )
    base = set(STAGE_A) | set(STAGE_B) | set(CLOSEOUT_FINAL_PATHS) | set(C10_STAGE_A_PATHS)
    base.add(C10_STAGE_B_PATH)
    changed_sets = {8: base, 9: base | set(C10_FINAL_CLOSEOUT_PATHS)}
    for size, state in ((8, "C10_CLOSEOUT_PREP_01"), (9, "C10_FINAL_CLOSEOUT")):
        require(
            validate_closeout_lifecycle(history[:size], set(), changed_sets[size]) == state, state
        )
    mutations: list[tuple[str, int, int, str, Any]] = [
        ("wrong C10 Prep parent", 8, 7, "parents", [C10_ENTRY_SHA]),
        ("wrong C10 Prep subject", 8, 7, "subject", "ci: unapproved"),
        ("extra C10 Prep path", 8, 7, "delta", {CLOSEOUT_VERIFIER_PATH: "M", "extra": "A"}),
        ("missing C10 Prep verifier", 8, 7, "delta", {}),
        ("added C10 Prep verifier", 8, 7, "delta", {CLOSEOUT_VERIFIER_PATH: "A"}),
        ("merge C10 Prep", 8, 7, "parents", [C10_CLOSEOUT_REVIEW_READY_SHA, C10_ENTRY_SHA]),
        ("wrong C10 Final parent", 9, 8, "parents", [C10_CLOSEOUT_REVIEW_READY_SHA]),
        ("wrong C10 Final subject", 9, 8, "subject", "docs: unapproved"),
        (
            "missing C10 Final file",
            9,
            8,
            "delta",
            dict.fromkeys(C10_FINAL_CLOSEOUT_PATHS[:-1], "A"),
        ),
        ("extra C10 Final file", 9, 8, "delta", {**history[8]["delta"], "extra": "A"}),
        ("modified C10 Final file", 9, 8, "delta", dict.fromkeys(C10_FINAL_CLOSEOUT_PATHS, "M")),
        ("renamed C10 Final file", 9, 8, "delta", dict.fromkeys(C10_FINAL_CLOSEOUT_PATHS, "R100")),
        ("deleted C10 Final file", 9, 8, "delta", dict.fromkeys(C10_FINAL_CLOSEOUT_PATHS, "D")),
        ("merge C10 Final", 9, 8, "parents", ["f" * 40, C10_CLOSEOUT_REVIEW_READY_SHA]),
        (
            "C10 Final verifier mutation",
            9,
            8,
            "delta",
            {**history[8]["delta"], CLOSEOUT_VERIFIER_PATH: "M"},
        ),
        (
            "mixed C10 Final/runtime",
            9,
            8,
            "delta",
            {**history[8]["delta"], "src/flowlens/investigation/contracts.py": "M"},
        ),
        (
            "mixed C10 Final/tests",
            9,
            8,
            "delta",
            {**history[8]["delta"], "tests/test_investigation_replay.py": "M"},
        ),
        (
            "mixed C10 Final/workflow",
            9,
            8,
            "delta",
            {**history[8]["delta"], ".github/workflows/ci.yml": "M"},
        ),
        (
            "mixed C10 Final/source manifest",
            9,
            8,
            "delta",
            {**history[8]["delta"], "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json": "M"},
        ),
        ("C09 protected file drift", 8, 3, "delta", {**history[3]["delta"], "extra": "M"}),
        ("C10 Stage-A historical drift", 8, 5, "delta", dict.fromkeys(C10_STAGE_A_PATHS, "M")),
        ("C10 Stage-B historical drift", 8, 6, "delta", {C10_STAGE_B_PATH: "M"}),
        ("C10 Bootstrap SHA drift", 8, 4, "sha", "a" * 40),
        ("C10 Stage-A SHA drift", 8, 5, "sha", "a" * 40),
        ("C10 Review-Ready SHA drift", 8, 6, "sha", "a" * 40),
        ("invalid C10 Prep SHA", 8, 7, "sha", "wrong"),
        ("duplicate C10 Prep SHA", 8, 7, "sha", C10_ENTRY_SHA),
        ("invalid C10 Final SHA", 9, 8, "sha", "0" * 40),
        ("duplicate C10 Final SHA", 9, 8, "sha", "f" * 40),
        ("C10 Prep record shape", 8, 7, "extra", True),
        ("C10 Final record shape", 9, 8, "extra", True),
    ]
    for label, size, index, field, value in mutations:
        damaged = copy.deepcopy(history[:size])
        damaged[index][field] = value
        rejected(
            label,
            lambda damaged=damaged, size=size: validate_closeout_lifecycle(
                damaged, set(), changed_sets[size]
            ),
        )
    cases = [
        ("Final without C10 Prep", history[:7] + [history[8]], set(), changed_sets[9]),
        ("extra post-C10 Final commit", history + [history[8]], set(), changed_sets[9]),
        ("working C10 Prep verifier", history[:8], {CLOSEOUT_VERIFIER_PATH}, base),
        ("working C10 Final governance", history, {C10_FINAL_CLOSEOUT_PATHS[0]}, changed_sets[9]),
        ("extra cumulative C10 path", history, set(), changed_sets[9] | {"extra"}),
    ]
    for label, damaged, working, changed in cases:
        rejected(
            label,
            lambda damaged=damaged, working=working, changed=changed: validate_closeout_lifecycle(
                damaged, working, changed
            ),
        )
    original = git("show", CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    source = (ROOT / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")
    _, units = source_units(source)
    for name in C10_CLOSEOUT_SOURCE_ADDITIONS:
        text, node = units[name]
        located = cast(ast.FunctionDef | ast.Assign, node)
        lines = source.splitlines(keepends=True)
        start, end = located.lineno - 1, cast(int, located.end_lineno)
        damaged_source = "".join(lines[:start] + lines[end:])
        rejected(
            "removed closeout source " + name,
            lambda damaged_source=damaged_source: validate_verifier_sources(
                original, damaged_source
            ),
        )
        damaged_source = "".join(lines[:start] + lines[end:]) + "\n" + text
        rejected(
            "reordered closeout source " + name,
            lambda damaged_source=damaged_source: validate_verifier_sources(
                original, damaged_source
            ),
        )
    return len(mutations) + len(cases) + 2 * len(C10_CLOSEOUT_SOURCE_ADDITIONS)


def validate_w04_sprint_lifecycle(
    history: list[dict[str, Any]], working: set[str], changed: set[str]
) -> str:
    """Admit one verifier Prep and one exact eight-path sprint Final, then stop."""
    if len(history) > 11:
        return validate_w04_pr7_merge_repair_lifecycle(history, working, changed)
    require(10 <= len(history) <= 11, "extra post-W04_SPRINT_FINAL_CLOSEOUT commit")
    base = set(STAGE_A) | set(STAGE_B) | set(CLOSEOUT_FINAL_PATHS)
    base.update(C10_STAGE_A_PATHS)
    base.add(C10_STAGE_B_PATH)
    base.update(C10_FINAL_CLOSEOUT_PATHS)
    require(
        validate_c10_closeout_lifecycle(history[:9], set(), base) == "C10_FINAL_CLOSEOUT"
        and history[8]["sha"] == W04_SPRINT_ENTRY_SHA,
        "sprint closeout requires the exact accepted C10 Final",
    )
    for record in history[9:]:
        require(set(record) == {"sha", "parents", "subject", "delta"}, "sprint record shape")
        require(
            isinstance(record["sha"], str)
            and re.fullmatch(r"[0-9a-f]{40}", record["sha"]) is not None
            and record["sha"] != "0" * 40,
            "invalid sprint closeout SHA",
        )
    require(len({row["sha"] for row in history}) == len(history), "duplicate sprint SHA")
    prep = history[9]
    require(
        prep["parents"] == [W04_SPRINT_ENTRY_SHA]
        and prep["subject"] == W04_SPRINT_CLOSEOUT_PREP_SUBJECT
        and prep["delta"] == {CLOSEOUT_VERIFIER_PATH: "M"},
        "invalid exact sprint Prep parent/subject/delta",
    )
    state, expected = "W04_SPRINT_CLOSEOUT_PREP_01", base.copy()
    if len(history) == 11:
        final = history[10]
        delta = dict.fromkeys(W04_SPRINT_FINAL_MODIFIED_PATHS, "M")
        delta.update(dict.fromkeys(W04_SPRINT_FINAL_ADDED_PATHS, "A"))
        require(
            final["parents"] == [prep["sha"]]
            and final["subject"] == W04_SPRINT_FINAL_CLOSEOUT_SUBJECT
            and final["delta"] == delta,
            "invalid exact sprint Final parent/subject/delta",
        )
        state = "W04_SPRINT_FINAL_CLOSEOUT"
        expected.update(delta)
    require(changed == expected, "sprint cumulative path-set drift")
    require(not working, "uncommitted sprint lifecycle delta")
    return state


def w04_sprint_prep_revision(repo: Path = ROOT) -> str | None:
    """Derive Sprint Prep only from the validated single-parent accepted chain."""
    revisions = git(
        "rev-list", "--reverse", W04_SPRINT_ENTRY_SHA + ".." + w04_pr7_historical_tip(repo),
        repo=repo,
    )
    rows = revisions.decode().splitlines()
    if not rows:
        return None
    changed = set(git("diff", "--name-only", ENTRY, "--", repo=repo).decode().splitlines())
    changed.update(
        git("ls-files", "--others", "--exclude-standard", repo=repo).decode().splitlines()
    )
    state = closeout_lifecycle_guard(changed, repo=repo)
    require(
        state
        in {
            "W04_SPRINT_CLOSEOUT_PREP_01",
            "W04_SPRINT_FINAL_CLOSEOUT",
            "W04_PR7_MERGE_REPAIR_01",
            "W04_PR7_MERGED_MAIN",
            "W04_POST_MERGE_INTEGRATED",
        }
        and 1 <= len(rows) <= 2,
        "no validated sprint Prep",
    )
    return rows[0]


def validate_w04_sprint_verifier_sources(review_ready: str, current: str) -> None:
    """Preserve every accepted source unit except five exact lifecycle connectors."""
    if "W04_PR7_FINAL_SHA = " in current:
        validate_w04_pr7_merge_verifier_sources(review_ready, current)
        return
    accepted = git("show", W04_SPRINT_ENTRY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    validate_c10_closeout_verifier_sources(review_ready, accepted)
    old_order, old = source_units(accepted)
    new_order, new = source_units(current)
    additions = set(W04_SPRINT_SOURCE_ADDITIONS)
    require(set(new) == set(old) | additions, "unauthorized sprint source unit addition/removal")
    require(
        [name for name in new_order if name not in additions] == old_order
        and [name for name in new_order if name in additions] == list(W04_SPRINT_SOURCE_ADDITIONS),
        "sprint source-unit order drift",
    )
    replacements = {
        "validate_c10_closeout_lifecycle": [
            (
                b'    require(8 <= len(history) <= 9, "extra post-C10_FINAL_CLOSEOUT commit")\n',
                b"    if len(history) > 9:\n"
                b"        return validate_w04_sprint_lifecycle(history, workin"
                b"g, changed)\n"
                b'    require(8 <= len(history) <= 9, "extra post-C10_FINAL_CL'
                b'OSEOUT commit")\n',
            ),
        ],
        "c10_bootstrap_revision": [
            (
                b'            "C10_FINAL_CLOSEOUT",\n',
                b'            "C10_FINAL_CLOSEOUT",\n'
                b'            "W04_SPRINT_CLOSEOUT_PREP_01",\n'
                b'            "W04_SPRINT_FINAL_CLOSEOUT",\n',
            ),
            (
                b'    require(1 <= len(revisions) <= 5, "invalid C10 Bootstrap derivation")\n',
                b'    require(1 <= len(revisions) <= 7, "invalid C10 Bootstrap derivation")\n',
            ),
        ],
        "c10_closeout_prep_revision": [
            (
                b'        state in {"C10_CLOSEOUT_PREP_01", "C10_FINAL_CLOSEOU'
                b'T"}\n'
                b"        and 4 <= len(revisions) <= 5\n",
                b"        state\n"
                b"        in {\n"
                b'            "C10_CLOSEOUT_PREP_01",\n'
                b'            "C10_FINAL_CLOSEOUT",\n'
                b'            "W04_SPRINT_CLOSEOUT_PREP_01",\n'
                b'            "W04_SPRINT_FINAL_CLOSEOUT",\n'
                b"        }\n"
                b"        and 4 <= len(revisions) <= 7\n",
            ),
        ],
        "validate_c10_closeout_verifier_sources": [
            (
                b'    accepted = git("show", C10_CLOSEOUT_REVIEW_READY_SHA + "'
                b':" + CLOSEOUT_VERIFIER_PATH).decode()\n',
                b'    if "W04_SPRINT_ENTRY_SHA = " in current:\n'
                b"        validate_w04_sprint_verifier_sources(review_ready, c"
                b"urrent)\n"
                b"        return\n"
                b'    accepted = git("show", C10_CLOSEOUT_REVIEW_READY_SHA + "'
                b':" + CLOSEOUT_VERIFIER_PATH).decode()\n',
            ),
        ],
        "c10_closeout_verifier_blob_guard": [
            (
                b"    prep = c10_closeout_prep_revision(repo)\n",
                b"    if w04_sprint_prep_revision(repo) is not None:\n"
                b"        w04_sprint_verifier_blob_guard(repo)\n"
                b"        return\n"
                b"    prep = c10_closeout_prep_revision(repo)\n",
            ),
        ],
    }
    for name in old_order:
        expected = old[name][0].encode()
        for before, after in replacements.get(name, []):
            expected = replace_once(expected, before, after)
        require(new[name][0].encode() == expected, f"unauthorized sprint source span: {name}")
    prep = w04_sprint_prep_revision()
    require(prep is not None, "sprint source requires committed Prep")
    committed_order, committed = source_units(
        git("show", str(prep) + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    )
    require(new_order == committed_order, "sprint Prep source-unit placement drift")
    for name in W04_SPRINT_SOURCE_ADDITIONS:
        require(new[name][0] == committed[name][0], f"sprint Prep source-span drift: {name}")
    constants: dict[str, object] = {
        "W04_SPRINT_ENTRY_SHA": "232bfb390babce30417b8cdb9a6660663eb3c3f1",
        "W04_SPRINT_CLOSEOUT_PREP_SUBJECT": "ci(w04): admit sprint closeout lifecycle",
        "W04_SPRINT_FINAL_CLOSEOUT_SUBJECT": "docs(w04): close sprint and prepare PR #7 review",
        "W04_SPRINT_FINAL_MODIFIED_PATHS": ("README.md", "AGENTS.md", "docs/CURRENT_STATE.md"),
        "W04_SPRINT_FINAL_ADDED_PATHS": (
            "docs/w04/W04_GPT_INDEPENDENT_DEEP_REVIEW_R1.md",
            "docs/w04/W04_SPRINT_HUMAN_ACCEPTANCE_AND_AUTHORIZATION.md",
            "docs/w04/W04_SPRINT_CLOSEOUT_CONTEXT_LOCK.md",
            "docs/w04/W04_SPRINT_FINAL_CLOSEOUT_REPORT.md",
            "docs/w04/W04_PR7_READINESS_REPORT.md",
        ),
        "W04_SPRINT_SOURCE_ADDITIONS": (
            "W04_SPRINT_ENTRY_SHA",
            "W04_SPRINT_CLOSEOUT_PREP_SUBJECT",
            "W04_SPRINT_FINAL_CLOSEOUT_SUBJECT",
            "W04_SPRINT_FINAL_MODIFIED_PATHS",
            "W04_SPRINT_FINAL_ADDED_PATHS",
            "W04_SPRINT_SOURCE_ADDITIONS",
            "validate_w04_sprint_lifecycle",
            "w04_sprint_prep_revision",
            "validate_w04_sprint_verifier_sources",
            "w04_sprint_verifier_blob_guard",
            "check_w04_sprint_controls",
        ),
    }
    for name, value in constants.items():
        node = new[name][1]
        require(isinstance(node, ast.Assign), "sprint constant declaration drift")
        require(ast.literal_eval(cast(ast.Assign, node).value) == value, "sprint constant drift")


def w04_sprint_verifier_blob_guard(repo: Path = ROOT) -> None:
    if w04_pr7_merge_repair_revision(repo) is not None:
        w04_pr7_merge_verifier_blob_guard(repo)
        return
    prep = w04_sprint_prep_revision(repo)
    require(prep is not None, "missing validated sprint Prep")
    require(
        (repo / CLOSEOUT_VERIFIER_PATH).read_bytes()
        == git("show", str(prep) + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo),
        "sprint verifier must remain byte-identical to Prep",
    )
    development = check_c10_lifecycle_controls()
    require(development == 32, "C10 development adversarial control drift")
    print(
        json.dumps(
            {
                "c10_bootstrap_sha": C10_CLOSEOUT_BOOTSTRAP_SHA,
                "c10_adversarial_controls": development,
            },
            sort_keys=True,
        )
    )
    closeout = check_c10_closeout_lifecycle_controls()
    require(closeout == 60, "C10 closeout adversarial control drift")
    c10_prep = c10_closeout_prep_revision(repo)
    print(
        json.dumps(
            {"c10_closeout_prep_sha": c10_prep, "c10_closeout_adversarial_controls": closeout},
            sort_keys=True,
        )
    )
    controls = check_w04_sprint_controls()
    print(
        json.dumps(
            {"w04_sprint_prep_sha": prep, "w04_sprint_adversarial_controls": controls},
            sort_keys=True,
        )
    )


def check_w04_sprint_controls() -> int:
    """Exercise the two new states, exact deltas, preserved anchors and self-source denial."""
    revisions = (
        CLOSEOUT_STAGE_A_SHA,
        CLOSEOUT_REVIEW_READY_SHA,
        C10_PREP_SHA,
        C10_ENTRY_SHA,
        C10_CLOSEOUT_BOOTSTRAP_SHA,
        C10_CLOSEOUT_STAGE_A_SHA,
        C10_CLOSEOUT_REVIEW_READY_SHA,
        "3d9c13f06e32b2cb75d258ed838ad0958d2f5803",
        W04_SPRINT_ENTRY_SHA,
    )
    history: list[dict[str, Any]] = []
    for revision in revisions:
        parents = git("show", "-s", "--format=%P", revision).decode().split()
        delta = {}
        for row in (
            git("diff", "--name-status", "--no-renames", parents[0], revision).decode().splitlines()
        ):
            status, path = row.split("\t")
            delta[path] = status
        history.append(
            {
                "sha": revision,
                "parents": parents,
                "subject": git("show", "-s", "--format=%s", revision).decode().strip(),
                "delta": delta,
            }
        )
    final_delta = dict.fromkeys(W04_SPRINT_FINAL_MODIFIED_PATHS, "M")
    final_delta.update(dict.fromkeys(W04_SPRINT_FINAL_ADDED_PATHS, "A"))
    history.extend(
        [
            {
                "sha": "1" * 40,
                "parents": [W04_SPRINT_ENTRY_SHA],
                "subject": W04_SPRINT_CLOSEOUT_PREP_SUBJECT,
                "delta": {CLOSEOUT_VERIFIER_PATH: "M"},
            },
            {
                "sha": "2" * 40,
                "parents": ["1" * 40],
                "subject": W04_SPRINT_FINAL_CLOSEOUT_SUBJECT,
                "delta": final_delta,
            },
        ]
    )
    base = (
        set(STAGE_A)
        | set(STAGE_B)
        | set(CLOSEOUT_FINAL_PATHS)
        | set(C10_STAGE_A_PATHS)
        | set(C10_FINAL_CLOSEOUT_PATHS)
    )
    base.add(C10_STAGE_B_PATH)
    sets = {10: base, 11: base | set(final_delta)}
    for size, state in ((10, "W04_SPRINT_CLOSEOUT_PREP_01"), (11, "W04_SPRINT_FINAL_CLOSEOUT")):
        require(validate_closeout_lifecycle(history[:size], set(), sets[size]) == state, state)
    mutations: list[tuple[str, int, int, str, Any]] = [
        ("wrong sprint Prep parent", 10, 9, "parents", [C10_CLOSEOUT_REVIEW_READY_SHA]),
        ("merge sprint Prep", 10, 9, "parents", [W04_SPRINT_ENTRY_SHA, C10_ENTRY_SHA]),
        ("wrong sprint Prep subject", 10, 9, "subject", "ci: unauthorized"),
        ("extra sprint Prep path", 10, 9, "delta", {CLOSEOUT_VERIFIER_PATH: "M", "extra": "A"}),
        ("missing sprint Prep verifier", 10, 9, "delta", {}),
        ("added sprint Prep verifier", 10, 9, "delta", {CLOSEOUT_VERIFIER_PATH: "A"}),
        ("wrong sprint Final parent", 11, 10, "parents", [W04_SPRINT_ENTRY_SHA]),
        ("merge sprint Final", 11, 10, "parents", ["1" * 40, W04_SPRINT_ENTRY_SHA]),
        ("wrong sprint Final subject", 11, 10, "subject", "docs: unauthorized"),
        (
            "missing sprint Final file",
            11,
            10,
            "delta",
            {k: v for k, v in final_delta.items() if k != "README.md"},
        ),
        ("extra sprint Final file", 11, 10, "delta", {**final_delta, "extra": "A"}),
        ("renamed sprint Final file", 11, 10, "delta", {**final_delta, "README.md": "R100"}),
        ("deleted sprint Final file", 11, 10, "delta", {**final_delta, "README.md": "D"}),
        ("added existing sprint file", 11, 10, "delta", {**final_delta, "README.md": "A"}),
        (
            "modified new sprint file",
            11,
            10,
            "delta",
            {**final_delta, W04_SPRINT_FINAL_ADDED_PATHS[0]: "M"},
        ),
        (
            "sprint Final verifier mutation",
            11,
            10,
            "delta",
            {**final_delta, CLOSEOUT_VERIFIER_PATH: "M"},
        ),
        ("wrong accepted C10 Final", 10, 8, "sha", "a" * 40),
        ("historical C10 drift", 10, 7, "subject", "ci: unauthorized"),
        ("invalid sprint SHA", 10, 9, "sha", "invalid"),
        ("zero sprint SHA", 10, 9, "sha", "0" * 40),
        ("duplicate sprint SHA", 10, 9, "sha", W04_SPRINT_ENTRY_SHA),
    ]
    for path in (
        "src/unauthorized.py",
        "tests/unauthorized.py",
        ".github/workflows/ci.yml",
        "pyproject.toml",
        "uv.lock",
        "migrations/unauthorized.py",
        "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json",
        "docs/w04/checkpoints/c10/W04_C10_FINAL_CLOSEOUT_REPORT.md",
        ".gitattributes",
    ):
        mutations.append(
            ("sprint Final protected delta " + path, 11, 10, "delta", {**final_delta, path: "M"})
        )
    for label, size, index, field, value in mutations:
        damaged = copy.deepcopy(history[:size])
        damaged[index][field] = value
        rejected(
            label,
            lambda damaged=damaged, size=size: validate_closeout_lifecycle(
                damaged, set(), sets[size]
            ),
        )
    extra = {"sha": "3" * 40, "parents": ["2" * 40], "subject": "docs: extra", "delta": {}}
    cases = [
        ("extra post-sprint Final commit", [*history, extra], set(), sets[11]),
        ("sprint Final without Prep", [*history[:9], history[10]], set(), sets[11]),
        ("dirty sprint Prep", history[:10], {CLOSEOUT_VERIFIER_PATH}, sets[10]),
        ("dirty sprint Final", history, {"README.md"}, sets[11]),
        ("sprint cumulative missing path", history, set(), base),
        ("sprint cumulative extra path", history, set(), sets[11] | {"extra"}),
    ]
    for label, rows, working, changed in cases:
        rejected(
            label,
            lambda rows=rows, working=working, changed=changed: validate_closeout_lifecycle(
                rows, working, changed
            ),
        )
    current = (ROOT / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")
    original = git("show", CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    _, units = source_units(current)
    for name in (*W04_SPRINT_SOURCE_ADDITIONS, "require"):
        text, node = units[name]
        located = cast(ast.FunctionDef | ast.Assign, node)
        lines = current.splitlines(keepends=True)
        start, end = located.lineno - 1, cast(int, located.end_lineno)
        require("".join(lines[start:end]) == text, "sprint adversary exact source span")
        for replacement in (
            [],
            [lines[start].rstrip("\n") + " # unauthorized\n", *lines[start + 1 : end]],
        ):
            damaged_source = "".join([*lines[:start], *replacement, *lines[end:]])
            rejected(
                "sprint unauthorized source span " + name,
                lambda damaged_source=damaged_source: validate_verifier_sources(
                    original, damaged_source
                ),
            )
    return len(mutations) + len(cases) + 2 * (len(W04_SPRINT_SOURCE_ADDITIONS) + 1)


def validate_w04_pr7_merge_repair_lifecycle(
    history: list[dict[str, Any]], working: set[str], changed: set[str]
) -> str:
    """Admit one verifier-only child of the exact accepted Sprint Final."""
    require(len(history) == 12, "extra or missing PR7 merge-repair lifecycle commit")
    expected = set(STAGE_A) | set(STAGE_B) | set(CLOSEOUT_FINAL_PATHS)
    expected.update(C10_STAGE_A_PATHS)
    expected.add(C10_STAGE_B_PATH)
    expected.update(C10_FINAL_CLOSEOUT_PATHS)
    expected.update(W04_SPRINT_FINAL_MODIFIED_PATHS)
    expected.update(W04_SPRINT_FINAL_ADDED_PATHS)
    require(
        validate_w04_sprint_lifecycle(history[:11], set(), expected)
        == "W04_SPRINT_FINAL_CLOSEOUT"
        and history[10]["sha"] == W04_PR7_FINAL_SHA,
        "PR7 repair requires the exact accepted Sprint Final and historical anchors",
    )
    repair = history[11]
    require(set(repair) == {"sha", "parents", "subject", "delta"}, "PR7 repair record shape")
    require(
        isinstance(repair["sha"], str)
        and re.fullmatch(r"[0-9a-f]{40}", repair["sha"]) is not None
        and repair["sha"] != "0" * 40
        and repair["sha"] not in {row["sha"] for row in history[:11]},
        "invalid PR7 repair SHA",
    )
    require(
        repair["parents"] == [W04_PR7_FINAL_SHA]
        and repair["subject"] == W04_PR7_MERGE_REPAIR_SUBJECT
        and repair["delta"] == {CLOSEOUT_VERIFIER_PATH: "M"},
        "invalid exact PR7 merge-repair parent/subject/delta",
    )
    require(changed == expected, "PR7 repair cumulative path-set drift")
    require(not working, "uncommitted PR7 merge-repair lifecycle delta")
    return "W04_PR7_MERGE_REPAIR_01"


def validate_w04_pr7_merge_topology(
    head: str,
    parents: list[str],
    repair: str,
    head_tree: bytes,
    repair_tree: bytes,
    second_parent_diff: bytes,
    working: set[str],
) -> str:
    """Authorize only the terminal frozen-main/exact-repair merge, with no new bytes."""
    require(
        re.fullmatch(r"[0-9a-f]{40}", head) is not None
        and re.fullmatch(r"[0-9a-f]{40}", repair) is not None
        and head != "0" * 40
        and repair != "0" * 40
        and head != repair,
        "invalid PR7 merged-main SHA",
    )
    require(
        parents == [head, W04_PR7_MAIN_SHA, repair],
        "PR7 merge requires ordered frozen-main and validated repair parents",
    )
    require(
        re.fullmatch(rb"[0-9a-f]{40}", head_tree) is not None
        and head_tree == repair_tree,
        "PR7 merge tree differs from validated repair",
    )
    require(not second_parent_diff, "PR7 merge has a second-parent resolution delta")
    require(not working, "uncommitted PR7 merged-main lifecycle delta")
    return "W04_PR7_MERGED_MAIN"


def w04_pr7_merged_main_guard(
    history: list[dict[str, Any]],
    changed: set[str],
    head: str,
    parents: list[str],
    repo: Path = ROOT,
) -> str:
    """The historical loop delegates only its terminal two-parent revision here."""
    working = set(git("diff", "--name-only", "HEAD", "--", repo=repo).decode().splitlines())
    working.update(
        git("ls-files", "--others", "--exclude-standard", repo=repo).decode().splitlines()
    )
    require(
        validate_closeout_lifecycle(history, working, changed) == "W04_PR7_MERGE_REPAIR_01",
        "PR7 merge requires one validated repair before the terminal merge",
    )
    git(
        "merge-base", "--is-ancestor", head,
        git("rev-parse", "HEAD", repo=repo).decode().strip(), repo=repo
    )
    repair = cast(str, history[-1]["sha"])
    return validate_w04_pr7_merge_topology(
        head,
        parents,
        repair,
        git("rev-parse", head + "^{tree}", repo=repo).strip(),
        git("rev-parse", repair + "^{tree}", repo=repo).strip(),
        git("diff", repair, head, "--", repo=repo),
        working,
    )


def w04_pr7_repair_history(
    repair: str, repo: Path = ROOT
) -> tuple[list[dict[str, Any]], set[str]]:
    """Read and validate the complete immutable lifecycle through the repair."""
    raw = git(
        "log", "--reverse", "--topo-order", "--format=%x1e%H%x00%P%x00%s",
        "--name-status", "--no-renames", ENTRY + ".." + repair, "--", repo=repo
    ).decode()
    history: list[dict[str, Any]] = []
    for record in raw.split("\x1e")[1:]:
        lines = record.splitlines()
        sha, parent_text, subject = lines[0].split("\x00")
        parents = parent_text.split()
        require(len(parents) == 1, "historical PR7 lifecycle merge/root forbidden")
        delta: dict[str, str] = {}
        for row in lines[1:]:
            if not row:
                continue
            status, path = row.split("\t")
            require(path not in delta, "duplicate PR7 historical delta")
            delta[path] = status
        history.append({"sha": sha, "parents": parents, "subject": subject, "delta": delta})
    changed = set(git("diff", "--name-only", ENTRY, repair, "--", repo=repo).decode().splitlines())
    require(
        validate_w04_pr7_merge_repair_lifecycle(history, set(), changed)
        == "W04_PR7_MERGE_REPAIR_01",
        "invalid historical PR7 repair",
    )
    return history, changed


def w04_pr7_pre_integration_guard(changed: set[str], repo: Path = ROOT) -> str | None:
    """Keep every pre-integration state strict, including the one repair child."""
    head = git("rev-parse", "HEAD", repo=repo).decode().strip()
    rows = git(
        "rev-list", "--reverse", W04_PR7_FINAL_SHA + ".." + head, repo=repo
    ).decode().splitlines()
    if not rows:
        return None
    require(rows == [head], "extra pre-integration PR7 repair history")
    history, _ = w04_pr7_repair_history(head, repo)
    working = set(git("diff", "--name-only", "HEAD", "--", repo=repo).decode().splitlines())
    working.update(
        git("ls-files", "--others", "--exclude-standard", repo=repo).decode().splitlines()
    )
    return validate_w04_pr7_merge_repair_lifecycle(history, working, changed)


def w04_pr7_integration_anchor(repo: Path = ROOT) -> str | None:
    """Find the exact integration in ancestry, without interpreting its descendants."""
    rows = [
        row.split() for row in git(
            "rev-list", "--parents", "--reverse", "--topo-order",
            W04_PR7_FINAL_SHA + "..HEAD", repo=repo
        ).decode().splitlines()
    ]
    records = {row[0]: row for row in rows}
    anchors = []
    for parents in rows:
        if (
            len(parents) != 3 or parents[1] != W04_PR7_MAIN_SHA
            or records.get(parents[2]) != [parents[2], W04_PR7_FINAL_SHA]
        ):
            continue
        merge, repair = parents[0], parents[2]
        span = git(
            "rev-list", "--reverse", "--topo-order",
            W04_PR7_FINAL_SHA + ".." + merge, repo=repo
        ).decode().splitlines()
        require(span == [repair, merge], "extra pre-integration PR7 history")
        history, changed = w04_pr7_repair_history(repair, repo)
        require(
            w04_pr7_merged_main_guard(history, changed, merge, parents, repo)
            == "W04_PR7_MERGED_MAIN",
            "invalid historical PR7 integration",
        )
        anchors.append(merge)
    require(len(anchors) <= 1, "multiple PR7 integration anchors")
    return anchors[0] if anchors else None


def w04_pr7_historical_tip(repo: Path = ROOT) -> str:
    """Keep historical source-layer derivations bounded to the accepted W04 Final."""
    return W04_PR7_FINAL_SHA if w04_pr7_merge_repair_revision(repo) is not None else "HEAD"


def w04_pr7_merge_repair_revision(repo: Path = ROOT) -> str | None:
    """Derive an exact repair either before or after its validated integration."""
    anchor = w04_pr7_integration_anchor(repo)
    if anchor is not None:
        return git("show", "-s", "--format=%P", anchor, repo=repo).decode().split()[1]
    rows = (
        git("rev-list", "--reverse", W04_PR7_FINAL_SHA + "..HEAD", repo=repo)
        .decode().splitlines()
    )
    if not rows:
        return None
    require(len(rows) == 1, "extra pre-integration PR7 repair commit")
    changed = set(git("diff", "--name-only", ENTRY, "--", repo=repo).decode().splitlines())
    changed.update(
        git("ls-files", "--others", "--exclude-standard", repo=repo).decode().splitlines()
    )
    require(
        closeout_lifecycle_guard(changed, repo=repo) == "W04_PR7_MERGE_REPAIR_01",
        "no validated PR7 merge repair",
    )
    return rows[0]


def validate_w04_pr7_merge_verifier_sources(review_ready: str, current: str) -> None:
    """Validate every accepted layer first, then only the exact seven repair connectors."""
    if "W04_P2_03_HARDENING_SHA = " in current:
        validate_w04_p2_03_r2_verifier_sources(review_ready, current)
        return
    if "W04_POST_MERGE_BASE_SHA = " in current:
        validate_w04_p2_03_verifier_sources(review_ready, current)
        return
    accepted = git("show", W04_PR7_FINAL_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    validate_w04_sprint_verifier_sources(review_ready, accepted)
    old_order, old = source_units(accepted)
    new_order, new = source_units(current)
    additions = set(W04_PR7_MERGE_SOURCE_ADDITIONS)
    require(set(new) == set(old) | additions, "unauthorized PR7 source unit addition/removal")
    require(
        [name for name in new_order if name not in additions] == old_order
        and [name for name in new_order if name in additions]
        == list(W04_PR7_MERGE_SOURCE_ADDITIONS),
        "PR7 source-unit identity/order drift",
    )
    replacements = {
        'validate_w04_sprint_lifecycle': [
            (
                '    require(10 <= len(history) <= 11, "extra post-W04_SPRINT_FINAL_CLOSEOUT '
                'commit")\n',
                '    if len(history) > 11:\n        return validate_w04_pr7_merge_repair_life'
                'cycle(history, working, changed)\n    require(10 <= len(history) <= 11, "ext'
                'ra post-W04_SPRINT_FINAL_CLOSEOUT commit")\n',
            ),
        ],
        'c10_bootstrap_revision': [
            (
                '            "W04_SPRINT_FINAL_CLOSEOUT",\n',
                '            "W04_SPRINT_FINAL_CLOSEOUT",\n            "W04_PR7_MERGE_REPAIR_'
                '01",\n            "W04_PR7_MERGED_MAIN",\n            "W04_POST_MERGE_INTEGR'
                'ATED",\n',
            ),
            (
                '        git("rev-list", "--reverse", C10_ENTRY_SHA + "..HEAD", repo=repo).de'
                'code().splitlines()\n',
                '        git("rev-list", "--reverse", C10_ENTRY_SHA + ".." + w04_pr7_historic'
                'al_tip(repo), repo=repo)\n        .decode()\n        .splitlines()\n',
            ),
        ],
        'c10_closeout_prep_revision': [
            (
                '            "W04_SPRINT_FINAL_CLOSEOUT",\n',
                '            "W04_SPRINT_FINAL_CLOSEOUT",\n            "W04_PR7_MERGE_REPAIR_'
                '01",\n            "W04_PR7_MERGED_MAIN",\n            "W04_POST_MERGE_INTEGR'
                'ATED",\n',
            ),
            (
                '        git("rev-list", "--reverse", C10_ENTRY_SHA + "..HEAD", repo=repo).de'
                'code().splitlines()\n',
                '        git("rev-list", "--reverse", C10_ENTRY_SHA + ".." + w04_pr7_historic'
                'al_tip(repo), repo=repo)\n        .decode()\n        .splitlines()\n',
            ),
        ],
        'w04_sprint_prep_revision': [
            (
                '    revisions = git("rev-list", "--reverse", W04_SPRINT_ENTRY_SHA + "..HEAD"'
                ', repo=repo)\n',
                '    revisions = git(\n        "rev-list", "--reverse", W04_SPRINT_ENTRY_SHA '
                '+ ".." + w04_pr7_historical_tip(repo),\n        repo=repo,\n    )\n',
            ),
            (
                '        state in {"W04_SPRINT_CLOSEOUT_PREP_01", "W04_SPRINT_FINAL_CLOSEOUT"'
                '}\n',
                '        state\n        in {\n            "W04_SPRINT_CLOSEOUT_PREP_01",\n   '
                '         "W04_SPRINT_FINAL_CLOSEOUT",\n            "W04_PR7_MERGE_REPAIR_01"'
                ',\n            "W04_PR7_MERGED_MAIN",\n            "W04_POST_MERGE_INTEGRATE'
                'D",\n        }\n',
            ),
        ],
        'validate_w04_sprint_verifier_sources': [
            (
                '    accepted = git("show", W04_SPRINT_ENTRY_SHA + ":" + CLOSEOUT_VERIFIER_PA'
                'TH).decode()\n',
                '    if "W04_PR7_FINAL_SHA = " in current:\n        validate_w04_pr7_merge_ve'
                'rifier_sources(review_ready, current)\n        return\n    accepted = git("s'
                'how", W04_SPRINT_ENTRY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()\n',
            ),
        ],
        'w04_sprint_verifier_blob_guard': [
            (
                '    prep = w04_sprint_prep_revision(repo)\n',
                '    if w04_pr7_merge_repair_revision(repo) is not None:\n        w04_pr7_mer'
                'ge_verifier_blob_guard(repo)\n        return\n    prep = w04_sprint_prep_rev'
                'ision(repo)\n',
            ),
        ],
        'closeout_lifecycle_guard': [
            (
                '    head = git("rev-parse", "HEAD", repo=repo).decode().strip()\n',
                '    head = git("rev-parse", "HEAD", repo=repo).decode().strip()\n    integra'
                'tion = w04_pr7_integration_anchor(repo)\n    if integration is not None:\n  '
                '      working = set(git("diff", "--name-only", "HEAD", "--", repo=repo).deco'
                'de().splitlines())\n        working.update(\n            git("ls-files", "--'
                'others", "--exclude-standard", repo=repo).decode().splitlines()\n        )\n'
                '        require(not working, "uncommitted post-integration lifecycle delta")'
                '\n        return "W04_PR7_MERGED_MAIN" if head == integration else "W04_POST'
                '_MERGE_INTEGRATED"\n    repaired = w04_pr7_pre_integration_guard(changed, re'
                'po)\n    if repaired is not None:\n        return repaired\n',
            ),
        ],
    }
    for name in old_order:
        expected = old[name][0].encode()
        for before, after in replacements.get(name, []):
            expected = replace_once(expected, before.encode(), after.encode())
        require(new[name][0].encode() == expected, f"unauthorized PR7 accepted source span: {name}")
    repair = w04_pr7_merge_repair_revision()
    require(repair is not None, "PR7 source requires committed validated repair")
    committed_order, committed = source_units(
        git("show", str(repair) + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    )
    require(new_order == committed_order, "PR7 repair source-unit placement drift")
    for name in W04_PR7_MERGE_SOURCE_ADDITIONS:
        require(new[name][0] == committed[name][0], f"PR7 repair source-span drift: {name}")
    constants: dict[str, object] = {
        'W04_PR7_FINAL_SHA': '985f666e5ecfa5acd35565516e200c9b0e36c76b',
        'W04_PR7_MAIN_SHA': 'af61bdfd5f7cf7961811c4c2dc8e554dd7eed509',
        'W04_PR7_MERGE_REPAIR_SUBJECT': 'ci(w04): admit PR #7 merge commit lifecycle',
        'W04_PR7_MERGE_SOURCE_ADDITIONS': (
            'W04_PR7_FINAL_SHA',
            'W04_PR7_MAIN_SHA',
            'W04_PR7_MERGE_REPAIR_SUBJECT',
            'W04_PR7_MERGE_SOURCE_ADDITIONS',
            'validate_w04_pr7_merge_repair_lifecycle',
            'validate_w04_pr7_merge_topology',
            'w04_pr7_merged_main_guard',
            'w04_pr7_repair_history',
            'w04_pr7_pre_integration_guard',
            'w04_pr7_integration_anchor',
            'w04_pr7_historical_tip',
            'w04_pr7_merge_repair_revision',
            'validate_w04_pr7_merge_verifier_sources',
            'w04_pr7_merge_verifier_blob_guard',
            'check_w04_pr7_merge_controls',
            'check_w04_pr7_post_integration_controls',
        ),
    }
    for name, value in constants.items():
        node = new[name][1]
        require(isinstance(node, ast.Assign), "PR7 constant declaration drift")
        require(ast.literal_eval(cast(ast.Assign, node).value) == value, "PR7 constant drift")


def w04_pr7_merge_verifier_blob_guard(repo: Path = ROOT) -> None:
    repair = w04_pr7_merge_repair_revision(repo)
    require(repair is not None, "missing validated PR7 merge repair")
    hardening = w04_p2_03_hardening_revision(repo)
    r2_repair = w04_p2_03_r2_repair_revision(repo)
    pr8_repair = w04_p2_03_pr8_merge_repair_revision(repo)
    frozen = pr8_repair or r2_repair or hardening or repair
    validate_w04_pr7_merge_verifier_sources(
        git("show", CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo).decode(),
        (repo / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8"),
    )
    require(
        (repo / CLOSEOUT_VERIFIER_PATH).read_bytes()
        == git("show", str(frozen) + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo)
        and git("rev-parse", "HEAD:" + CLOSEOUT_VERIFIER_PATH, repo=repo)
        == git("rev-parse", str(frozen) + ":" + CLOSEOUT_VERIFIER_PATH, repo=repo),
        "PR7 verifier must remain byte-identical to validated repair",
    )
    prep = w04_sprint_prep_revision(repo)
    require(prep is not None, "missing accepted Sprint Prep")
    development = check_c10_lifecycle_controls()
    require(development == 32, "C10 development adversarial control drift")
    print(
        json.dumps(
            {
                "c10_bootstrap_sha": C10_CLOSEOUT_BOOTSTRAP_SHA,
                "c10_adversarial_controls": development,
            },
            sort_keys=True,
        )
    )
    closeout = check_c10_closeout_lifecycle_controls()
    require(closeout == 60, "C10 closeout adversarial control drift")
    c10_prep = c10_closeout_prep_revision(repo)
    print(
        json.dumps(
            {"c10_closeout_prep_sha": c10_prep, "c10_closeout_adversarial_controls": closeout},
            sort_keys=True,
        )
    )
    controls = check_w04_sprint_controls()
    print(
        json.dumps(
            {"w04_sprint_prep_sha": prep, "w04_sprint_adversarial_controls": controls},
            sort_keys=True,
        )
    )
    controls = check_w04_pr7_merge_controls()
    post_controls = check_w04_pr7_post_integration_controls()
    print(
        json.dumps(
            {
                "w04_pr7_merge_repair_sha": repair,
                "w04_pr7_merge_adversarial_controls": controls,
                "w04_post_integration_controls": post_controls,
                "w04_pr7_merge_source_guard": "PASS",
            },
            sort_keys=True,
        )
    )
    if frozen != repair:
        hardening_controls = check_w04_p2_03_controls()
        print(
            json.dumps(
                {
                    "w04_post_merge_p2_03_hardening": "PASS",
                    "w04_p2_03_hardening_sha": hardening,
                    "w04_p2_03_controls": hardening_controls,
                },
                sort_keys=True,
            )
        )
    if r2_repair is not None:
        r2_controls = check_w04_p2_03_r2_controls()
        print(
            json.dumps(
                {
                    "w04_p2_03_r2_repair": "PASS",
                    "w04_p2_03_r2_repair_sha": r2_repair,
                    "w04_p2_03_r2_controls": r2_controls,
                },
                sort_keys=True,
            )
        )
    if pr8_repair is not None:
        pr8_controls = check_w04_p2_03_pr8_merge_controls()
        print(
            json.dumps(
                {
                    "w04_p2_03_pr8_merge_repair": "PASS",
                    "w04_p2_03_pr8_merge_repair_sha": pr8_repair,
                    "w04_p2_03_pr8_merge_controls": pr8_controls,
                    "w04_p2_03_pr8_lifecycle": w04_p2_03_pr8_lifecycle(repo),
                    "w04_p2_03_source_tip": w04_p2_03_source_tip(repo),
                    "w04_p2_03_pr8_integration_anchor": w04_p2_03_pr8_integration_anchor(repo),
                },
                sort_keys=True,
            )
        )


def check_w04_pr7_merge_controls() -> int:
    """Execute accepted-Final, exact repair/merge positives and hostile lifecycle/source cases."""
    revisions = [CLOSEOUT_STAGE_A_SHA, CLOSEOUT_REVIEW_READY_SHA]
    revisions.extend(
        git("rev-list", "--reverse", CLOSEOUT_REVIEW_READY_SHA + ".." + W04_PR7_FINAL_SHA)
        .decode()
        .splitlines()
    )
    history: list[dict[str, Any]] = []
    for revision in revisions:
        parents = git("show", "-s", "--format=%P", revision).decode().split()
        require(len(parents) == 1, "accepted historical lifecycle merge/root")
        delta = {}
        for row in (
            git("diff", "--name-status", "--no-renames", parents[0], revision).decode().splitlines()
        ):
            status, path = row.split("\t")
            require(path not in delta, "duplicate accepted lifecycle path")
            delta[path] = status
        history.append(
            {
                "sha": revision,
                "parents": parents,
                "subject": git("show", "-s", "--format=%s", revision).decode().strip(),
                "delta": delta,
            }
        )
    changed = set(git("diff", "--name-only", ENTRY, W04_PR7_FINAL_SHA, "--").decode().splitlines())
    require(
        validate_closeout_lifecycle(history, set(), changed) == "W04_SPRINT_FINAL_CLOSEOUT",
        "accepted W04 Sprint Final no longer valid",
    )
    repair, merge, tree = "a" * 40, "b" * 40, b"c" * 40
    history.append(
        {
            "sha": repair,
            "parents": [W04_PR7_FINAL_SHA],
            "subject": W04_PR7_MERGE_REPAIR_SUBJECT,
            "delta": {CLOSEOUT_VERIFIER_PATH: "M"},
        }
    )
    require(
        validate_closeout_lifecycle(history, set(), changed) == "W04_PR7_MERGE_REPAIR_01",
        "valid PR7 merge-repair state rejected",
    )
    parents = [merge, W04_PR7_MAIN_SHA, repair]
    require(
        validate_w04_pr7_merge_topology(merge, parents, repair, tree, tree, b"", set())
        == "W04_PR7_MERGED_MAIN",
        "valid synthetic PR7 merge rejected",
    )
    lifecycle_mutations: list[tuple[str, int, str, Any]] = [
        ("wrong repair parent", 11, "parents", ["d" * 40]),
        ("merge repair", 11, "parents", [W04_PR7_FINAL_SHA, W04_PR7_MAIN_SHA]),
        ("root repair", 11, "parents", []),
        ("wrong repair subject", 11, "subject", "ci: unauthorized"),
        ("extra repair path", 11, "delta", {CLOSEOUT_VERIFIER_PATH: "M", "README.md": "M"}),
        ("added repair verifier", 11, "delta", {CLOSEOUT_VERIFIER_PATH: "A"}),
        ("deleted repair verifier", 11, "delta", {CLOSEOUT_VERIFIER_PATH: "D"}),
        ("renamed repair verifier", 11, "delta", {CLOSEOUT_VERIFIER_PATH: "R100"}),
        ("invalid repair SHA", 11, "sha", "0" * 40),
        ("historical lifecycle merge", 9, "parents", [W04_SPRINT_ENTRY_SHA, W04_PR7_MAIN_SHA]),
        ("historical anchor mutation", 8, "sha", "d" * 40),
        ("accepted Final mutation", 10, "sha", "e" * 40),
    ]
    for label, index, field, value in lifecycle_mutations:
        damaged = copy.deepcopy(history)
        damaged[index][field] = value
        rejected(
            label,
            lambda damaged=damaged: validate_closeout_lifecycle(damaged, set(), changed),
        )
    for label, damaged, working, cumulative in (
        ("extra Final-to-repair commit", history[:11] + [history[-1], history[-1]], set(), changed),
        ("extra repair-to-merge commit", history + [history[-1]], set(), changed),
        ("uncommitted repair", history, {CLOSEOUT_VERIFIER_PATH}, changed),
        ("repair cumulative extra path", history, set(), changed | {"src/extra.py"}),
    ):
        rejected(
            label,
            lambda damaged=damaged, working=working, cumulative=cumulative:
                validate_closeout_lifecycle(damaged, working, cumulative),
        )
    topology_mutations: list[tuple[str, str, list[str], bytes, bytes, bytes, set[str]]] = [
        ("wrong main parent", merge, [merge, "d" * 40, repair], tree, tree, b"", set()),
        (
            "wrong feature parent", merge, [merge, W04_PR7_MAIN_SHA, "d" * 40],
            tree, tree, b"", set(),
        ),
        ("reversed parents", merge, [merge, repair, W04_PR7_MAIN_SHA], tree, tree, b"", set()),
        ("octopus merge", merge, parents + ["d" * 40], tree, tree, b"", set()),
        ("root merge", merge, [merge], tree, tree, b"", set()),
        ("arbitrary one-parent merge", merge, [merge, repair], tree, tree, b"", set()),
        ("merge tree drift", merge, parents, b"d" * 40, tree, b"", set()),
        ("second-parent resolution delta", merge, parents, tree, tree, b"changed", set()),
        ("invalid merge tree", merge, parents, b"", b"", b"", set()),
        ("uncommitted merge", merge, parents, tree, tree, b"", {"README.md"}),
        ("nonterminal merge identity", "d" * 40, parents, tree, tree, b"", set()),
    ]
    for label, damaged_head, damaged_parents, head_tree, repair_tree, diff, working in (
        topology_mutations
    ):
        rejected(
            label,
            lambda damaged_head=damaged_head, damaged_parents=damaged_parents,
                head_tree=head_tree, repair_tree=repair_tree, diff=diff, working=working:
                validate_w04_pr7_merge_topology(
                    damaged_head, damaged_parents, repair, head_tree, repair_tree, diff, working
                ),
        )

    def fake_git(*arguments: str, repo: Path = ROOT) -> bytes:
        responses = {
            ("diff", "--name-only", "HEAD", "--"): b"",
            ("ls-files", "--others", "--exclude-standard"): b"",
            ("rev-parse", "HEAD"): merge.encode(),
            ("merge-base", "--is-ancestor", merge, merge): b"",
            ("rev-parse", merge + "^{tree}"): tree,
            ("rev-parse", repair + "^{tree}"): tree,
            ("diff", repair, merge, "--"): b"",
        }
        require(arguments in responses, "unexpected merge-control Git command")
        return responses[arguments]

    with patch.dict(globals(), {"git": fake_git}):
        require(
            w04_pr7_merged_main_guard(history, changed, merge, parents) == "W04_PR7_MERGED_MAIN",
            "terminal merge dispatch rejected valid topology",
        )
        rejected(
            "direct Final-to-merge without repair",
            lambda: w04_pr7_merged_main_guard(
                history[:11], changed, merge, [merge, W04_PR7_MAIN_SHA, W04_PR7_FINAL_SHA]
            ),
        )
    original = git("show", CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()
    current = (ROOT / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")
    validate_w04_pr7_merge_verifier_sources(original, current)
    _, units = source_units(current)
    lines = current.splitlines(keepends=True)

    def splice(name: str, replacement: str) -> str:
        text, parsed = units[name]
        node = cast(ast.stmt, parsed)
        start, end = node.lineno - 1, cast(int, node.end_lineno)
        require("".join(lines[start:end]) == text, "PR7 source adversary span mismatch")
        return "".join(lines[:start]) + replacement + "".join(lines[end:])

    name = "validate_w04_pr7_merge_topology"
    unit = units[name][0]
    source_mutations = [
        splice(name, ""),
        splice(name, unit.replace("def " + name + "(", "def renamed_pr7_topology(", 1)),
        splice(name, "") + "\n" + unit,
        splice(name, unit + "    pass\n"),
        splice("require", units["require"][0] + "    pass\n"),
        current + "\ndef unauthorized_pr7_unit():\n    pass\n",
        splice(
            "W04_PR7_MAIN_SHA",
            'W04_PR7_MAIN_SHA = "' + "d" * 40 + '"\n',
        ),
        splice(
            "closeout_lifecycle_guard",
            units["closeout_lifecycle_guard"][0].replace(
                "if integration is not None:", "if True:", 1
            ),
        ),
    ]
    for damaged_source in source_mutations:
        require(damaged_source != current, "PR7 source adversary no-op")
        rejected(
            "unauthorized PR7 source deletion/rename/reorder/span/merge exception",
            lambda damaged_source=damaged_source:
                validate_w04_pr7_merge_verifier_sources(original, damaged_source),
        )
    return 4 + len(lifecycle_mutations) + 4 + len(topology_mutations) + 1 + len(source_mutations)


def check_w04_pr7_post_integration_controls() -> int:
    """Execute integration/descendant continuations and fail-closed anchor controls."""
    repair = "a" * 40
    merge = "b" * 40
    doc = "c" * 40
    later = "d" * 40
    branch = "e" * 40
    tree = b"f" * 40
    actual = w04_pr7_merge_repair_revision()
    require(actual is not None, "post-integration controls need a validated repair")
    history, changed = w04_pr7_repair_history(cast(str, actual))
    history[-1]["sha"] = repair
    records = {
        repair: [repair, W04_PR7_FINAL_SHA],
        merge: [merge, W04_PR7_MAIN_SHA, repair],
        doc: [doc, merge],
        branch: [branch, doc],
        later: [later, doc, branch],
    }
    state: dict[str, Any] = {
        "head": merge, "working": set(), "tree": tree,
        "diff": b"", "span": [repair, merge], "history": history,
    }

    def fake_history(revision: str, repo: Path = ROOT) -> tuple[list[dict[str, Any]], set[str]]:
        require(revision == repair, "unexpected historical control revision")
        validate_w04_pr7_merge_repair_lifecycle(state["history"], set(), changed)
        return state["history"], changed

    def fake_git(*arguments: str, repo: Path = ROOT) -> bytes:
        if arguments == ("rev-parse", "HEAD"):
            return cast(str, state["head"]).encode()
        if arguments == (
            "rev-list", "--parents", "--reverse", "--topo-order", W04_PR7_FINAL_SHA + "..HEAD"
        ):
            active = {merge: [repair, merge], doc: [repair, merge, doc],
                      later: [repair, merge, doc, branch, later]}[state["head"]]
            return "\n".join(" ".join(records[n]) for n in active).encode()
        if arguments == (
            "rev-list", "--reverse", "--topo-order", W04_PR7_FINAL_SHA + ".." + merge
        ):
            return "\n".join(state["span"]).encode()
        if arguments == ("diff", "--name-only", "HEAD", "--"):
            return "\n".join(sorted(state["working"])).encode()
        if arguments == ("ls-files", "--others", "--exclude-standard"):
            return b""
        if arguments == ("merge-base", "--is-ancestor", merge, state["head"]):
            return b""
        if arguments == ("rev-parse", merge + "^{tree}"):
            return cast(bytes, state["tree"])
        if arguments == ("rev-parse", repair + "^{tree}"):
            return tree
        if arguments == ("diff", repair, merge, "--"):
            return cast(bytes, state["diff"])
        raise AssertionError("unexpected post-integration control Git command: " + repr(arguments))

    with patch.dict(globals(), {"git": fake_git, "w04_pr7_repair_history": fake_history}):
        for head, expected in (
            (merge, "W04_PR7_MERGED_MAIN"),
            (doc, "W04_POST_MERGE_INTEGRATED"),
            (later, "W04_POST_MERGE_INTEGRATED"),
        ):
            state["head"] = head
            require(closeout_lifecycle_guard(changed) == expected, "post-integration continuation")
        for path in (CLOSEOUT_VERIFIER_PATH, "README.md", "src/extra.py", "extra-untracked"):
            state["working"] = {path}
            rejected("dirty historical mode", lambda: closeout_lifecycle_guard(changed))
        state["working"] = set()
        for key, value in (
            ("tree", b"0" * 40), ("diff", b"changed"),
            ("span", [repair, "0" * 40, merge]),
            ("history", history[:11]),
        ):
            original = state[key]
            state[key] = value
            rejected(
                "invalid historical integration proof", lambda: closeout_lifecycle_guard(changed)
            )
            state[key] = original
        original = records[merge]
        for parents in (
            [merge, repair, W04_PR7_MAIN_SHA],
            [merge, W04_PR7_MAIN_SHA, W04_PR7_FINAL_SHA],
            [merge, W04_PR7_MAIN_SHA, repair, "0" * 40],
        ):
            records[merge] = parents
            require(w04_pr7_integration_anchor() is None, "hostile topology became an anchor")
        records[merge] = original
    return 3 + 4 + 4 + 3



def validate_w04_p2_03_history(history: list[dict[str, Any]]) -> str | None:
    """Validate every ordered post-base row; no descendant may disappear."""
    # The unchanged merge baseline precedes the separately authorized hardening.
    if not history:
        return None
    require(1 <= len(history) <= 4, "P2_03 unauthorized post-base history length")
    seen: set[str] = set()
    expected = (
        (
            W04_P2_03_HARDENING_SHA,
            W04_POST_MERGE_BASE_SHA,
            W04_P2_03_HARDENING_SUBJECT,
            W04_P2_03_HARDENING_PATHS,
        ),
        (
            W04_P2_03_DOC_SYNC_SHA,
            W04_P2_03_HARDENING_SHA,
            W04_P2_03_DOC_SYNC_SUBJECT,
            W04_P2_03_DOC_SYNC_PATHS,
        ),
        (
            W04_P2_03_R2_SHA,
            W04_P2_03_DOC_SYNC_SHA,
            W04_P2_03_R2_REPAIR_SUBJECT,
            W04_P2_03_R2_REPAIR_PATHS,
        ),
        (
            None,
            W04_P2_03_R2_SHA,
            W04_P2_03_PR8_MERGE_REPAIR_SUBJECT,
            W04_P2_03_PR8_MERGE_REPAIR_PATHS,
        ),
    )
    for row, (frozen, parent, subject, paths) in zip(
        history, expected[: len(history)], strict=True
    ):
        require(
            isinstance(row, dict) and set(row) == {"sha", "parents", "subject", "delta"},
            "P2_03 record shape",
        )
        revision = row["sha"]
        require(
            isinstance(revision, str)
            and re.fullmatch(r"[0-9a-f]{40}", revision) is not None
            and revision != "0" * 40
            and revision not in seen,
            "P2_03 invalid/duplicate revision",
        )
        seen.add(revision)
        require(
            (frozen is None or revision == frozen)
            and row["parents"] == [parent]
            and row["subject"] == subject
            and row["delta"] == {path: "M" for path in paths},
            "P2_03 exact ordered SHA/parent/subject/M-delta",
        )
    return W04_P2_03_HARDENING_SHA


def w04_p2_03_commit_record(revision: str, repo: Path = ROOT) -> dict[str, Any]:
    parents = git("show", "-s", "--format=%P", revision, repo=repo).decode("ascii").split()
    require(bool(parents), "P2_03 root revision forbidden")
    raw = git("diff", "--name-status", "--no-renames", "-z", parents[0], revision, "--", repo=repo)
    require(not raw or raw.endswith(b"\x00"), "P2_03 unterminated Git delta")
    fields = raw[:-1].split(b"\x00") if raw else []
    require(len(fields) % 2 == 0, "P2_03 malformed Git delta")
    delta: dict[str, str] = {}
    for status_raw, path_raw in zip(fields[::2], fields[1::2], strict=True):
        status = status_raw.decode("ascii", errors="strict")
        path = path_raw.decode("utf-8", errors="strict")
        require(bool(path) and path not in delta, "P2_03 duplicate/empty Git path")
        require(re.fullmatch(r"[ACDMRTUXB]", status) is not None, "P2_03 invalid Git status")
        delta[path] = status
    return {
        "sha": revision,
        "parents": parents,
        "subject": git("show", "-s", "--format=%s", revision, repo=repo)
        .decode("utf-8")
        .rstrip("\r\n"),
        "delta": delta,
    }


def w04_p2_03_hardening_revision(repo: Path = ROOT) -> str | None:
    integration = w04_pr7_integration_anchor(repo)
    if integration is None:
        return None
    require(integration == W04_POST_MERGE_BASE_SHA, "P2_03 historical integration anchor drift")
    history = w04_p2_03_source_history(w04_p2_03_source_tip(repo), repo)
    return validate_w04_p2_03_history(history)


def validate_w04_p2_03_ci_sources(path: str, entry: str, current: str) -> None:
    require(path in W04_P2_03_CI_EDITS, "P2_03 unauthorized CI source path")
    require(
        entry == git("show", W04_POST_MERGE_BASE_SHA + ":" + path).decode("utf-8"),
        "P2_03 CI baseline identity",
    )
    expected = entry.encode("utf-8")
    for before, after in W04_P2_03_CI_EDITS[path]:
        expected = replace_once(expected, before.encode("utf-8"), after.encode("utf-8"))
    require(current.encode("utf-8") == expected, "P2_03 unauthorized CI source evolution: " + path)


def validate_w04_p2_03_test_sources(path: str, entry: str, current: str) -> None:
    require(path in W04_P2_03_TEST_FUNCTIONS, "P2_03 unauthorized test source path")
    require(
        entry == git("show", W04_POST_MERGE_BASE_SHA + ":" + path).decode("utf-8"),
        "P2_03 test baseline identity",
    )
    anchor = w04_p2_03_hardening_revision()
    require(anchor is not None, "P2_03 test evolution requires committed hardening")
    old_order, old = source_units(entry)
    new_order, new = source_units(current)
    _, frozen = source_units(git("show", str(anchor) + ":" + path).decode("utf-8"))
    require(old_order == new_order, "P2_03 test unit/name/order drift")
    old_lines, new_lines = entry.splitlines(keepends=True), current.splitlines(keepends=True)
    for name in old_order:
        if name not in W04_P2_03_TEST_FUNCTIONS[path]:
            require(old[name][0] == new[name][0], "P2_03 unrelated test source drift: " + name)
            continue
        a, b = old[name][1], new[name][1]
        require(
            isinstance(a, ast.FunctionDef) and isinstance(b, ast.FunctionDef), "P2_03 test kind"
        )
        a, b = cast(ast.FunctionDef, a), cast(ast.FunctionDef, b)
        left, right = copy.deepcopy(a), copy.deepcopy(b)
        left.body, right.body = [], []
        require(
            ast.dump(left, include_attributes=False) == ast.dump(right, include_attributes=False),
            "P2_03 test signature/decorator/parameter drift: " + name,
        )
        a_start = min([a.lineno, *(d.lineno for d in a.decorator_list)]) - 1
        b_start = min([b.lineno, *(d.lineno for d in b.decorator_list)]) - 1
        require(
            old_lines[a_start : a.body[0].lineno - 1] == new_lines[b_start : b.body[0].lineno - 1],
            "P2_03 test declaration source drift: " + name,
        )
        require(new[name][0] == frozen[name][0], "P2_03 committed test body drift: " + name)


def validate_w04_p2_03_meta_ci_sources(
    path: str, entry: str, current: str, repo: Path = ROOT
) -> None:
    anchor = w04_p2_03_hardening_revision(repo)
    if anchor is None:
        validate_meta_ci_sources(path, entry, current)
        return
    accepted = git("show", W04_POST_MERGE_BASE_SHA + ":" + path, repo=repo).decode("utf-8")
    validate_meta_ci_sources(path, entry, accepted)
    if path in W04_P2_03_TEST_FUNCTIONS:
        validate_w04_p2_03_test_sources(path, accepted, current)
    elif path == "tests/test_c09_ci_gate.py" and w04_p2_03_r2_repair_revision(repo):
        validate_w04_p2_03_r2_test_sources(
            git("show", W04_P2_03_DOC_SYNC_SHA + ":" + path, repo=repo).decode("utf-8"),
            current,
            repo=repo,
        )
    else:
        require(current == accepted, "P2_03 unchanged legacy meta-CI source drift")


def w04_p2_03_protected_source_guard(repo: Path = ROOT) -> None:
    anchor = w04_p2_03_hardening_revision(repo)
    if anchor is None:
        require(
            not git("diff", W04_POST_MERGE_BASE_SHA, "--", *W04_P2_03_CI_EDITS, repo=repo),
            "P2_03 CI source changed before validated hardening",
        )
        return
    repair = w04_p2_03_r2_repair_revision(repo)
    frozen_paths = {path: anchor for path in W04_P2_03_HARDENING_PATHS}
    if repair is not None:
        frozen_paths.update({path: repair for path in W04_P2_03_R2_REPAIR_PATHS})
    pr8_repair = w04_p2_03_pr8_merge_repair_revision(repo)
    if pr8_repair is not None:
        frozen_paths.update({path: pr8_repair for path in W04_P2_03_PR8_MERGE_REPAIR_PATHS})
        if w04_p2_03_pr8_integration_anchor(repo) is not None:
            frozen_paths.pop("AGENTS.md")
            frozen_paths.pop("docs/CURRENT_STATE.md")
    for path, frozen in frozen_paths.items():
        require(
            (repo / path).read_bytes() == git("show", frozen + ":" + path, repo=repo)
            and git("ls-tree", "HEAD", "--", path, repo=repo)
            == git("ls-tree", frozen, "--", path, repo=repo)
            and not git("diff", frozen, "--", path, repo=repo),
            "P2_03 protected source drift: " + path,
        )
    for path in W04_P2_03_CI_EDITS:
        validate_w04_p2_03_ci_sources(
            path,
            git("show", W04_POST_MERGE_BASE_SHA + ":" + path, repo=repo).decode("utf-8"),
            (repo / path).read_text(encoding="utf-8"),
        )
    for path in W04_P2_03_TEST_FUNCTIONS:
        validate_w04_p2_03_test_sources(
            path,
            git("show", W04_POST_MERGE_BASE_SHA + ":" + path, repo=repo).decode("utf-8"),
            (repo / path).read_text(encoding="utf-8"),
        )
    if repair is not None:
        validate_w04_p2_03_r2_test_sources(
            git("show", W04_P2_03_DOC_SYNC_SHA + ":tests/test_c09_ci_gate.py", repo=repo).decode(
                "utf-8"
            ),
            (repo / "tests/test_c09_ci_gate.py").read_text(encoding="utf-8"),
            repo=repo,
        )


def validate_w04_p2_03_verifier_sources(review_ready: str, current: str) -> None:
    accepted = git("show", W04_POST_MERGE_BASE_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode("utf-8")
    validate_w04_pr7_merge_verifier_sources(review_ready, accepted)
    old_order, old = source_units(accepted)
    new_order, new = source_units(current)
    additions = set(W04_P2_03_SOURCE_ADDITIONS)
    require(set(new) == set(old) | additions, "P2_03 verifier unit addition/removal")
    require(
        [name for name in new_order if name not in additions] == old_order
        and [name for name in new_order if name in additions] == list(W04_P2_03_SOURCE_ADDITIONS),
        "P2_03 verifier source-unit identity/order drift",
    )
    for name in old_order:
        expected = old[name][0].encode("utf-8")
        for before, after in W04_P2_03_CONNECTORS.get(name, ()):
            expected = replace_once(expected, before.encode("utf-8"), after.encode("utf-8"))
        require(new[name][0].encode("utf-8") == expected, "P2_03 unrelated verifier span: " + name)
    anchor = w04_p2_03_hardening_revision()
    require(anchor is not None, "P2_03 source requires committed exact hardening")
    committed_order, committed = source_units(
        git("show", str(anchor) + ":" + CLOSEOUT_VERIFIER_PATH).decode("utf-8")
    )
    require(new_order == committed_order, "P2_03 verifier committed unit placement")
    for name in W04_P2_03_SOURCE_ADDITIONS:
        require(new[name][0] == committed[name][0], "P2_03 admitted source span drift: " + name)
    constants: dict[str, object] = {
        "W04_POST_MERGE_BASE_SHA": "b2b582541d38180c3bf8360699e6df271979829a",
        "W04_P2_03_HARDENING_SUBJECT": "ci(post-w04): harden publication deletion governance",
        "W04_P2_03_HARDENING_PATHS": W04_P2_03_HARDENING_PATHS,
        "W04_P2_03_TEST_FUNCTIONS": W04_P2_03_TEST_FUNCTIONS,
        "W04_P2_03_CI_EDITS": W04_P2_03_CI_EDITS,
        "W04_P2_03_CONNECTORS": W04_P2_03_CONNECTORS,
        "W04_P2_03_CONTROL_LABELS": W04_P2_03_CONTROL_LABELS,
        "W04_P2_03_SOURCE_ADDITIONS": W04_P2_03_SOURCE_ADDITIONS,
    }
    for name, value in constants.items():
        node = new[name][1]
        require(isinstance(node, ast.Assign), "P2_03 constant declaration drift")
        require(
            ast.literal_eval(cast(ast.Assign, node).value) == value, "P2_03 constant value drift"
        )


def check_w04_p2_03_controls() -> int:
    """Exercise real Git routing, publication defense and exact history/source admission."""
    import classify_change as classifier
    import verify_publication as publication

    completed: list[str] = []

    def done(label: str) -> None:
        require(
            label in W04_P2_03_CONTROL_LABELS and label not in completed, "P2_03 control identity"
        )
        completed.append(label)

    def yes(label: str, condition: bool) -> None:
        require(condition, "P2_03 positive control failed: " + label)
        done(label)

    def no(label: str, action: Any, message: str | None = None) -> None:
        try:
            action()
        except (
            ValueError,
            AssertionError,
            OSError,
            UnicodeError,
            subprocess.CalledProcessError,
        ) as error:
            require(message is None or message in str(error), "P2_03 wrong rejection: " + label)
            done(label)
            return
        raise ValueError("P2_03 negative control admitted: " + label)

    with tempfile.TemporaryDirectory(prefix="w04-p203-") as temporary:
        directory = Path(temporary)
        route = directory / "routing"
        route.mkdir()
        git("init", "-q", "-b", "main", repo=route)
        git("config", "user.email", "ci@example.test", repo=route)
        git("config", "user.name", "CI Test", repo=route)
        git("config", "core.autocrlf", "false", repo=route)
        (route / "README.md").write_text("fixture\n", encoding="utf-8", newline="\n")
        for path in W04_P2_03_CI_EDITS:
            target = route / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / path).read_bytes())

        def commit_route() -> str:
            git("add", "-A", repo=route)
            git("commit", "-q", "-m", "P2-03 behavior fixture", repo=route)
            return git("rev-parse", "HEAD", repo=route).decode("ascii").strip()

        def event(before: str, head: str) -> dict[str, Any]:
            return {
                "action": "synchronize",
                "before": before,
                "after": head,
                "pull_request": {"head": {"sha": head}},
            }

        def changed(before: str, head: str) -> dict[str, Any]:
            return classifier.classify_event(event(before, head), "pull_request", head, route)

        def positive(label: str, before: str, head: str, path: str) -> None:
            actual = changed(before, head)
            proof = publication.verify_publication(event(before, head), "pull_request", head, route)
            yes(
                label,
                actual == proof
                and actual["class"] == "P"
                and actual["gate"] == "PUBLICATION_EXACT_SHA"
                and actual["changed_paths"] == [path],
            )

        def full(label: str, before: str, head: str, paths: list[str]) -> None:
            actual = changed(before, head)
            yes(
                label,
                actual["class"] == "UNKNOWN"
                and actual["gate"] == "FULL_EXACT_SHA"
                and actual["changed_paths"] == sorted(paths)
                and "publication_non_add_modify_delta" in actual["reason_codes"],
            )

        before = commit_route()
        report = "docs/w04/checkpoints/fixture/W04_FIXTURE_FINAL_CLOSEOUT_REPORT.md"
        state = "docs/CURRENT_STATE.md"
        for path, label in ((report, "w04-add"), (state, "state-add")):
            target = route / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Report\n", encoding="utf-8", newline="\n")
            head = commit_route()
            positive(label, before, head, path)
            before = head
            target.write_text("# Modified\n", encoding="utf-8", newline="\n")
            head = commit_route()
            positive(label.replace("add", "modify"), before, head, path)
            before = head
        for path, label in ((report, "w04-delete"), (state, "state-delete")):
            deleted_base = before
            (route / path).unlink()
            head = commit_route()
            full(label, before, head, [path])
            weakened = classifier.result("P", before, head, [path], "regression-control")
            with patch.object(publication, "classify_event", return_value=weakened):
                no(
                    label + "-defense",
                    lambda before=before, head=head: publication.verify_publication(
                        event(before, head), "pull_request", head, route
                    ),
                    "missing publication file at verified head:",
                )
            before = head
        push = classifier.classify_event(event(deleted_base, head), "push", head, route)
        yes(
            "push-delete",
            push["class"] == "UNKNOWN"
            and push["gate"] == "FULL_EXACT_SHA"
            and push["reason_codes"] == ["push_full"],
        )
        (route / report).write_text("# Restored\n", encoding="utf-8", newline="\n")
        before = commit_route()
        renamed = report.replace("FIXTURE_", "RENAMED_")
        git("mv", report, renamed, repo=route)
        head = commit_route()
        full("publication-rename", before, head, [report, renamed])
        (route / renamed).unlink()
        (route / report).write_text("# New report\n", encoding="utf-8", newline="\n")
        before, head = head, commit_route()
        full("mixed-add-delete", before, head, [report, renamed])
        for path, expected in (
            ("docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json", "C"),
            ("src/flowlens/investigation/fixture.py", "I"),
            ("uv.lock", "F"),
            ("unknown/fixture.txt", "UNKNOWN"),
        ):
            target = route / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("fixture\n", encoding="utf-8", newline="\n")
            before, head = head, commit_route()
            actual = changed(before, head)
            yes(
                "routing-" + expected,
                actual["class"] == expected and actual["gate"] == "FULL_EXACT_SHA",
            )
        malformed = {
            "no-nul": b"M\x00docs/CURRENT_STATE.md",
            "odd": b"M\x00path\x00A\x00",
            "status": b"Q\x00path\x00",
            "empty-status": b"\x00path\x00",
            "empty-path": b"M\x00\x00",
            "utf8": b"M\x00\xff\x00",
            "status-utf8": b"\xff\x00path\x00",
            "duplicate": b"A\x00path\x00M\x00path\x00",
        }
        for label, payload in malformed.items():
            with patch.object(
                subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout=payload)
            ):
                no("parser-" + label, lambda: classifier.changed_entries(route, "base", "head"))
        with patch.object(
            subprocess,
            "run",
            return_value=subprocess.CompletedProcess(
                [], 0, stdout=b"T\x00docs/CURRENT_STATE.md\x00"
            ),
        ):
            yes(
                "parser-type-change",
                classifier.changed_entries(route, "base", "head")
                == [("T", "docs/CURRENT_STATE.md")],
            )
        # Use a real committed type transition without creating a host symlink.
        (route / state).write_text("# State\n", encoding="utf-8", newline="\n")
        before = commit_route()
        blob = (
            subprocess.run(
                ["git", "hash-object", "-w", "--stdin"],
                cwd=route,
                check=True,
                input=b"target\n",
                capture_output=True,
            )
            .stdout.decode()
            .strip()
        )
        git("update-index", "--cacheinfo", "120000," + blob + "," + state, repo=route)
        git("commit", "-q", "-m", "P2-03 type fixture", repo=route)
        head = git("rev-parse", "HEAD", repo=route).decode().strip()
        full("publication-type-change", before, head, [state])

        hardening = w04_p2_03_hardening_revision()
        require(hardening is not None, "P2_03 controls require the committed hardening")
        hardening = cast(str, hardening)
        valid = w04_p2_03_commit_record(hardening)
        yes("history-hardening", validate_w04_p2_03_history([valid]) == hardening)
        yes("history-before", validate_w04_p2_03_history([]) is None)
        doc = w04_p2_03_commit_record(W04_P2_03_DOC_SYNC_SHA)
        yes("history-docs", validate_w04_p2_03_history([valid, doc]) == hardening)
        mutations: list[tuple[str, str, Any]] = [
            ("parent", "parents", [W04_PR7_FINAL_SHA]),
            ("merge-parent", "parents", [W04_POST_MERGE_BASE_SHA, hardening]),
            ("root-parent", "parents", []),
            ("subject", "subject", "ci: unauthorized"),
            ("sha", "sha", "0" * 40),
            ("extra-path", "delta", {**valid["delta"], "README.md": "M"}),
        ]
        for path in W04_P2_03_HARDENING_PATHS:
            mutations.append(
                ("missing:" + path, "delta", {p: s for p, s in valid["delta"].items() if p != path})
            )
            for status in ("A", "D", "R100"):
                mutations.append((status + ":" + path, "delta", {**valid["delta"], path: status}))
        for label, key, value in mutations:
            damaged_record = copy.deepcopy(valid)
            damaged_record[key] = value
            no(
                "history-" + label,
                lambda damaged_record=damaged_record: validate_w04_p2_03_history([damaged_record]),
                "P2_03",
            )
        second = {**valid, "sha": "e" * 40}
        no("history-multiple", lambda: validate_w04_p2_03_history([valid, second]), "P2_03")
        no("history-duplicate", lambda: validate_w04_p2_03_history([valid, valid]), "P2_03")

        for path in W04_P2_03_CI_EDITS:
            baseline = git("show", W04_POST_MERGE_BASE_SHA + ":" + path).decode("utf-8")
            current = (ROOT / path).read_text(encoding="utf-8")
            no(
                "ci-drift:" + path,
                lambda path=path, baseline=baseline, current=current: validate_w04_p2_03_ci_sources(
                    path, baseline, current + "\n# drift\n"
                ),
                "P2_03",
            )
        for path, names in W04_P2_03_TEST_FUNCTIONS.items():
            baseline = git("show", W04_POST_MERGE_BASE_SHA + ":" + path).decode("utf-8")
            current = (ROOT / path).read_text(encoding="utf-8")
            _, units = source_units(current)
            unrelated = next(n for n in units if n.startswith("test_") and n not in names)
            damaged = current.replace(units[unrelated][0], units[unrelated][0] + "    pass\n", 1)
            no(
                "test-unrelated:" + path,
                lambda path=path, baseline=baseline, damaged=damaged: (
                    validate_w04_p2_03_test_sources(path, baseline, damaged)
                ),
                "P2_03",
            )
            no(
                "test-extra:" + path,
                lambda path=path, baseline=baseline, current=current: (
                    validate_w04_p2_03_test_sources(
                        path, baseline, current + "\ndef test_unapproved():\n    pass\n"
                    )
                ),
                "P2_03",
            )
            for name in names:
                unit = units[name][0]
                for label, replacement in (
                    ("body", unit + "    pass\n"),
                    ("signature", unit.replace("def " + name + "(", "def renamed(", 1)),
                    ("decorator", '@pytest.mark.usefixtures("unapproved")\n' + unit),
                ):
                    damaged = current.replace(unit, replacement, 1)
                    no(
                        "test-" + label + ":" + name,
                        lambda path=path, baseline=baseline, damaged=damaged: (
                            validate_w04_p2_03_test_sources(path, baseline, damaged)
                        ),
                        "P2_03",
                    )
            parametrized = next(n for n in names if "@pytest.mark.parametrize" in units[n][0])
            damaged = current.replace(
                units[parametrized][0],
                units[parametrized][0].replace('"P"', '"UNKNOWN"', 1)
                if '"P"' in units[parametrized][0].split("def ")[0]
                else units[parametrized][0].replace(
                    "W04_FIXTURE_FINAL_CLOSEOUT_REPORT.md",
                    "W04_CHANGED_FINAL_CLOSEOUT_REPORT.md",
                    1,
                ),
                1,
            )
            require(damaged != current, "P2_03 parameter adversary did not mutate")
            no(
                "test-parametrization:" + path,
                lambda path=path, baseline=baseline, damaged=damaged: (
                    validate_w04_p2_03_test_sources(path, baseline, damaged)
                ),
                "P2_03",
            )

        review = git("show", CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode()
        current = (ROOT / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")
        _, units = source_units(current)
        verifier_mutations = {
            "constant": current.replace(
                units["W04_POST_MERGE_BASE_SHA"][0],
                'W04_POST_MERGE_BASE_SHA = "' + "e" * 40 + '"\n',
                1,
            ),
            "legacy": current.replace(units["require"][0], units["require"][0] + "    pass\n", 1),
            "extra": current + "\ndef unapproved_p2_unit():\n    pass\n",
            "admitted": current.replace(
                units["w04_p2_03_hardening_revision"][0],
                units["w04_p2_03_hardening_revision"][0] + "    pass\n",
                1,
            ),
            "order": current.replace(units["w04_p2_03_commit_record"][0], "", 1)
            + "\n"
            + units["w04_p2_03_commit_record"][0],
        }
        for label, damaged in verifier_mutations.items():
            require(damaged != current, "P2_03 verifier adversary did not mutate")
            no(
                "verifier-" + label,
                lambda damaged=damaged: validate_w04_pr7_merge_verifier_sources(review, damaged),
                "P2_03",
            )

        fixture = directory / "source"
        git(
            "clone",
            "--quiet",
            "--no-hardlinks",
            "--no-checkout",
            str(ROOT),
            str(fixture),
            repo=directory,
        )
        git("config", "user.email", "ci@example.test", repo=fixture)
        git("config", "user.name", "CI Test", repo=fixture)
        git("config", "core.autocrlf", "false", repo=fixture)
        git("checkout", "-q", "--detach", hardening, repo=fixture)
        w04_p2_03_protected_source_guard(fixture)
        done("git-hardening-freeze")
        for path in W04_P2_03_HARDENING_PATHS:
            target = fixture / path
            target.write_bytes(target.read_bytes() + b"\n# unauthorized drift\n")
            git("add", "--", path, repo=fixture)
            git("commit", "-q", "-m", "fixture protected drift", repo=fixture)
            no(
                "git-protected:" + path,
                lambda: w04_p2_03_protected_source_guard(fixture),
                "P2_03",
            )
            git("checkout", "-q", "--detach", hardening, repo=fixture)
        real_git = git

        def fixture_git(*arguments: str, repo: Path = ROOT) -> bytes:
            return real_git(*arguments, repo=fixture)

        for path in (
            ".github/workflows/ci.yml",
            "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json",
            "src/flowlens/investigation/__init__.py",
        ):
            target = fixture / path
            target.write_bytes(target.read_bytes() + b"\n# unauthorized drift\n")
            git("add", "--", path, repo=fixture)
            git("commit", "-q", "-m", "fixture frozen drift", repo=fixture)
            if path == ".github/workflows/ci.yml":
                no("git-frozen:" + path, lambda: workflow_guard(fixture))
            elif path == "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json":
                no("git-frozen:" + path, lambda path=path: runner.load_manifest(fixture / path))
            else:
                with patch.dict(
                    globals(),
                    {
                        "ROOT": fixture,
                        "git": fixture_git,
                        "w04_p2_03_protected_source_guard": lambda: None,
                    },
                ):
                    no(
                        "git-frozen:" + path,
                        verify_collection_and_scope,
                        "W04_C09_PROTECTED_OBJECT_DRIFT",
                    )
            git("checkout", "-q", "--detach", hardening, repo=fixture)
        tree = git("rev-parse", hardening + "^{tree}", repo=fixture).decode().strip()
        duplicate = (
            git(
                "commit-tree",
                tree,
                "-p",
                W04_POST_MERGE_BASE_SHA,
                "-m",
                W04_P2_03_HARDENING_SUBJECT,
                "-m",
                "second control anchor",
                repo=fixture,
            )
            .decode()
            .strip()
        )
        merged = (
            git(
                "commit-tree",
                tree,
                "-p",
                hardening,
                "-p",
                duplicate,
                "-m",
                "control merge",
                repo=fixture,
            )
            .decode()
            .strip()
        )
        git("checkout", "-q", "--detach", merged, repo=fixture)
        no(
            "git-multiple-anchors",
            lambda: w04_p2_03_hardening_revision(fixture),
            "P2_03",
        )
        wrong = (
            git(
                "commit-tree",
                tree,
                "-p",
                W04_POST_MERGE_BASE_SHA,
                "-m",
                "ci: wrong hardening subject",
                repo=fixture,
            )
            .decode()
            .strip()
        )
        git("checkout", "-q", "--detach", wrong, repo=fixture)
        no("git-wrong-subject", lambda: w04_p2_03_hardening_revision(fixture), "P2_03")
        documentation = (
            git(
                "commit-tree",
                W04_POST_MERGE_BASE_SHA + "^{tree}",
                "-p",
                W04_POST_MERGE_BASE_SHA,
                "-m",
                "docs: control parent",
                repo=fixture,
            )
            .decode()
            .strip()
        )
        wrong = (
            git(
                "commit-tree",
                tree,
                "-p",
                documentation,
                "-m",
                W04_P2_03_HARDENING_SUBJECT,
                repo=fixture,
            )
            .decode()
            .strip()
        )
        git("checkout", "-q", "--detach", wrong, repo=fixture)
        no("git-wrong-parent", lambda: w04_p2_03_hardening_revision(fixture), "P2_03")
    require(
        len(completed) == len(W04_P2_03_CONTROL_LABELS)
        and set(completed) == set(W04_P2_03_CONTROL_LABELS),
        "P2_03 deterministic control coverage/count drift",
    )
    return len(completed)

def w04_p2_03_r2_repair_revision(repo: Path = ROOT) -> str | None:
    """Discover the sole repair only after validating the complete ordered history."""
    if w04_p2_03_hardening_revision(repo) is None:
        return None
    history = w04_p2_03_source_history(w04_p2_03_source_tip(repo), repo)
    return cast(str, history[2]["sha"]) if len(history) >= 3 else None


def validate_w04_p2_03_r2_test_sources(entry: str, current: str, repo: Path = ROOT) -> None:
    path = "tests/test_c09_ci_gate.py"
    require(
        entry == git("show", W04_P2_03_DOC_SYNC_SHA + ":" + path, repo=repo).decode("utf-8"),
        "P2_03 R2 C09 baseline identity",
    )
    repair = w04_p2_03_r2_repair_revision(repo)
    require(repair is not None, "P2_03 R2 C09 requires exact committed repair")
    old_order, old = source_units(entry)
    new_order, new = source_units(current)
    _, frozen = source_units(git("show", str(repair) + ":" + path, repo=repo).decode("utf-8"))
    require(old_order == new_order, "P2_03 R2 C09 unit/name/order drift")
    old_lines, new_lines = entry.splitlines(keepends=True), current.splitlines(keepends=True)
    for name in old_order:
        if name != W04_P2_03_R2_C09_TARGET:
            require(old[name][0] == new[name][0], "P2_03 R2 unrelated C09 span: " + name)
            continue
        a, b = old[name][1], new[name][1]
        require(
            isinstance(a, ast.FunctionDef) and isinstance(b, ast.FunctionDef),
            "P2_03 R2 C09 function kind",
        )
        a, b = cast(ast.FunctionDef, a), cast(ast.FunctionDef, b)
        left, right = copy.deepcopy(a), copy.deepcopy(b)
        left.body, right.body = [], []
        require(
            ast.dump(left, include_attributes=False) == ast.dump(right, include_attributes=False),
            "P2_03 R2 C09 signature/decorator/parameter drift",
        )
        a_start = min([a.lineno, *(d.lineno for d in a.decorator_list)]) - 1
        b_start = min([b.lineno, *(d.lineno for d in b.decorator_list)]) - 1
        require(
            old_lines[a_start : a.body[0].lineno - 1] == new_lines[b_start : b.body[0].lineno - 1],
            "P2_03 R2 C09 declaration source drift",
        )
        require(new[name][0] == frozen[name][0], "P2_03 R2 C09 committed target body drift")
    require(
        current.encode("utf-8") == git("show", str(repair) + ":" + path, repo=repo),
        "P2_03 R2 C09 committed bytes drift",
    )


def validate_w04_p2_03_r2_verifier_sources(review_ready: str, current: str) -> None:
    """Execute the accepted R1 chain, then admit only literal R2 connectors/additions."""
    if "W04_P2_03_R2_SHA = " in current:
        validate_w04_p2_03_pr8_verifier_sources(review_ready, current)
        return
    accepted = git("show", W04_P2_03_DOC_SYNC_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode("utf-8")
    validate_w04_p2_03_verifier_sources(review_ready, accepted)
    old_order, old = source_units(accepted)
    new_order, new = source_units(current)
    additions = set(W04_P2_03_R2_SOURCE_ADDITIONS)
    require(set(new) == set(old) | additions, "P2_03 R2 verifier unit addition/removal")
    require(
        [name for name in new_order if name not in additions] == old_order
        and [name for name in new_order if name in additions]
        == list(W04_P2_03_R2_SOURCE_ADDITIONS),
        "P2_03 R2 verifier unit order",
    )
    require(
        set(W04_P2_03_R2_CONNECTORS)
        == {
            "validate_w04_pr7_merge_verifier_sources",
            "w04_pr7_merge_verifier_blob_guard",
            "validate_w04_p2_03_history",
            "validate_w04_p2_03_meta_ci_sources",
            "w04_p2_03_protected_source_guard",
            "check_w04_p2_03_controls",
        },
        "P2_03 R2 connector authority drift",
    )
    for name in old_order:
        expected = old[name][0].encode("utf-8")
        for before, after in W04_P2_03_R2_CONNECTORS.get(name, ()):
            expected = replace_once(expected, before.encode("utf-8"), after.encode("utf-8"))
        require(
            new[name][0].encode("utf-8") == expected, "P2_03 R2 unrelated verifier span: " + name
        )
        if name in W04_P2_03_R2_CONNECTORS:
            a, b = copy.deepcopy(old[name][1]), copy.deepcopy(new[name][1])
            require(
                isinstance(a, ast.FunctionDef) and isinstance(b, ast.FunctionDef),
                "P2_03 R2 connector function kind",
            )
            a, b = cast(ast.FunctionDef, a), cast(ast.FunctionDef, b)
            a.body, b.body = [], []
            require(
                ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False),
                "P2_03 R2 connector signature/decorator drift",
            )
    repair = w04_p2_03_r2_repair_revision()
    require(repair is not None, "P2_03 R2 source requires exact repair")
    frozen_source = git("show", str(repair) + ":" + CLOSEOUT_VERIFIER_PATH).decode("utf-8")
    frozen_order, frozen = source_units(frozen_source)
    require(new_order == frozen_order, "P2_03 R2 committed unit order")
    for name in W04_P2_03_R2_SOURCE_ADDITIONS:
        require(new[name][0] == frozen[name][0], "P2_03 R2 admitted span drift: " + name)
    require(
        current.encode("utf-8") == frozen_source.encode("utf-8")
        and git("ls-tree", "HEAD", "--", CLOSEOUT_VERIFIER_PATH)
        == git("ls-tree", str(repair), "--", CLOSEOUT_VERIFIER_PATH),
        "P2_03 R2 committed verifier bytes/tree drift",
    )


def check_w04_p2_03_r2_controls() -> int:
    """Prove the reported real-Git escape and every narrow recovery boundary."""
    completed: list[str] = []

    def yes(label: str, condition: bool) -> None:
        require(condition, "P2_03 R2 positive control failed: " + label)
        require(
            label in W04_P2_03_R2_CONTROL_LABELS and label not in completed,
            "P2_03 R2 control identity",
        )
        completed.append(label)

    def no(label: str, action: Any) -> None:
        rejected("P2_03 R2 " + label, action)
        yes(label, True)

    hardening = w04_p2_03_commit_record(W04_P2_03_HARDENING_SHA)
    docs = w04_p2_03_commit_record(W04_P2_03_DOC_SYNC_SHA)
    repair_sha = w04_p2_03_r2_repair_revision()
    require(repair_sha is not None, "P2_03 R2 controls require committed repair")
    repair_sha = cast(str, repair_sha)
    repair = w04_p2_03_commit_record(repair_sha)
    history = [hardening, docs, repair]
    for length in (1, 2, 3):
        yes(
            "state-" + str(length),
            validate_w04_p2_03_history(history[:length]) == W04_P2_03_HARDENING_SHA,
        )
    extra = {
        "sha": "f" * 40,
        "parents": [W04_P2_03_DOC_SYNC_SHA],
        "subject": "docs: arbitrary EXTRA",
        "delta": {"EXTRA.md": "A"},
    }
    no("arbitrary-third", lambda: validate_w04_p2_03_history([hardening, docs, extra]))
    no("arbitrary-fourth", lambda: validate_w04_p2_03_history(history + [extra]))
    for index, record in enumerate(history):
        for label, key, value in (
            ("sha", "sha", "0" * 40),
            ("invalid-sha", "sha", "g" * 40),
            ("parent", "parents", [W04_PR7_MAIN_SHA]),
            ("root", "parents", []),
            ("merge", "parents", [*record["parents"], "e" * 40]),
            ("subject", "subject", "ci: unauthorized"),
            ("missing-path", "delta", {}),
            ("extra-path", "delta", {**record["delta"], "EXTRA.md": "M"}),
        ):
            damaged_history = copy.deepcopy(history)
            damaged_history[index][key] = value
            no(
                str(index) + "-" + label,
                lambda damaged_history=damaged_history: validate_w04_p2_03_history(damaged_history),
            )
    for index in (0, 1):
        damaged_history = copy.deepcopy(history)
        damaged_history[index]["sha"] = "a" * 40
        no(
            str(index) + "-unpinned-sha",
            lambda damaged_history=damaged_history: validate_w04_p2_03_history(damaged_history),
        )
    no("reordered", lambda: validate_w04_p2_03_history([docs, hardening, repair]))
    no("duplicate", lambda: validate_w04_p2_03_history([hardening, docs, docs]))
    no("record-shape", lambda: validate_w04_p2_03_history([{**hardening, "extra": True}]))
    for path in W04_P2_03_R2_REPAIR_PATHS:
        damaged_history = copy.deepcopy(history)
        damaged_history[2]["delta"].pop(path)
        no(
            "repair-missing:" + path,
            lambda damaged_history=damaged_history: validate_w04_p2_03_history(damaged_history),
        )
        for status in ("A", "D", "R", "T"):
            damaged_history = copy.deepcopy(history)
            damaged_history[2]["delta"][path] = status
            no(
                "repair-" + status + ":" + path,
                lambda damaged_history=damaged_history: validate_w04_p2_03_history(damaged_history),
            )
    path = "tests/test_c09_ci_gate.py"
    entry = git("show", W04_P2_03_DOC_SYNC_SHA + ":" + path).decode("utf-8")
    current = (ROOT / path).read_text(encoding="utf-8")
    validate_w04_p2_03_r2_test_sources(entry, current)
    _, units = source_units(current)
    target = units[W04_P2_03_R2_C09_TARGET][0]
    yes(
        "c09-stale-publication-freeze-removed",
        '"scripts/ci/verify_publication.py",\n' not in target,
    )
    for frozen in ("pyproject.toml", "uv.lock", "docker-compose.yml"):
        yes(
            "c09-historical:" + frozen,
            '"' + frozen + '"' in target and 'git("show", f"{gate.ENTRY}:{path}")' in target,
        )
    yes(
        "c09-publication-e260",
        '"e2606585829153a2f69c9628c916cf42dcc1b926"' in target
        and "assert hardening == W04_P2_03_HARDENING_SHA" in target
        and 'git("show", f"{hardening}:{path}").encode("utf-8")' in target
        and "assert (ROOT / path).read_bytes() == expected" in target,
    )
    unrelated = next(
        name for name in units if name.startswith("test_") and name != W04_P2_03_R2_C09_TARGET
    )
    import_unit = next(text for text, node in units.values() if isinstance(node, ast.Import))
    name = W04_P2_03_R2_C09_TARGET
    mutations = {
        "unrelated": current.replace(units[unrelated][0], units[unrelated][0] + "    pass\n", 1),
        "extra": current + "\ndef test_r2_unapproved():\n    pass\n",
        "rename": current.replace("def " + name + "(", "def renamed(", 1),
        "signature": current.replace("def " + name + "()", "def " + name + "(extra)", 1),
        "decorator": current.replace(
            "def " + name + "(", "@pytest.mark.skip\ndef " + name + "(", 1
        ),
        "import": current.replace(import_unit, "import fractions\n", 1),
        "body": current.replace(target, target + "    pass\n", 1),
    }
    for label, damaged in mutations.items():
        require(damaged != current, "P2_03 R2 C09 adversary did not mutate")
        no(
            "c09-" + label,
            lambda damaged=damaged: validate_w04_p2_03_r2_test_sources(entry, damaged),
        )
    review = git("show", CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode("utf-8")
    source = (ROOT / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")
    validate_w04_p2_03_r2_verifier_sources(review, source)
    _, source_spans = source_units(source)
    for name in ("require", "validate_w04_p2_03_history", "w04_p2_03_r2_repair_revision"):
        damaged = source.replace(source_spans[name][0], source_spans[name][0] + "    pass\n", 1)
        no(
            "verifier:" + name,
            lambda damaged=damaged: validate_w04_p2_03_r2_verifier_sources(review, damaged),
        )
    no(
        "verifier-extra",
        lambda: validate_w04_p2_03_r2_verifier_sources(
            review, source + "\ndef unapproved():\n    pass\n"
        ),
    )
    for frozen in W04_P2_03_HARDENING_PATHS:
        if frozen == CLOSEOUT_VERIFIER_PATH:
            continue
        yes(
            "e260-freeze:" + frozen,
            (ROOT / frozen).read_bytes() == git("show", W04_P2_03_HARDENING_SHA + ":" + frozen),
        )
    with tempfile.TemporaryDirectory(prefix="w04-p203-r2-") as temporary:
        directory = Path(temporary)
        fixture = directory / "repo"
        git(
            "clone",
            "--quiet",
            "--no-hardlinks",
            "--no-checkout",
            str(ROOT),
            str(fixture),
            repo=directory,
        )
        git("config", "core.autocrlf", "false", repo=fixture)
        git("config", "user.name", "CI Test", repo=fixture)
        git("config", "user.email", "ci@example.test", repo=fixture)
        git("checkout", "-q", "--detach", W04_P2_03_DOC_SYNC_SHA, repo=fixture)
        yes("git-doc-discovery", w04_p2_03_hardening_revision(fixture) == W04_P2_03_HARDENING_SHA)
        yes("git-doc-no-repair", w04_p2_03_r2_repair_revision(fixture) is None)
        # Execute the exact accepted R1 validator, not a simulated approximation.
        legacy_source = git("show", W04_P2_03_DOC_SYNC_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode(
            "utf-8"
        )
        legacy: dict[str, Any] = {
            "__name__": "accepted_r1_control",
            "__file__": str(ROOT / CLOSEOUT_VERIFIER_PATH),
        }
        exec(compile(legacy_source, "<accepted-ca250-verifier>", "exec"), legacy)
        (fixture / "EXTRA.md").write_text(
            "# Unauthorized descendant\n", encoding="utf-8", newline="\n"
        )
        git("add", "--", "EXTRA.md", repo=fixture)
        git("commit", "-q", "-m", "docs: arbitrary EXTRA", repo=fixture)
        yes(
            "git-old-finding-reproduced",
            legacy["w04_p2_03_hardening_revision"](fixture) == W04_P2_03_HARDENING_SHA,
        )
        legacy["w04_p2_03_protected_source_guard"](fixture)
        yes("git-old-protected-escape-reproduced", True)
        no("git-third-rejected", lambda: w04_p2_03_hardening_revision(fixture))
        no("git-third-protected-rejected", lambda: w04_p2_03_protected_source_guard(fixture))
        git("checkout", "-q", "--detach", repair_sha, repo=fixture)
        yes("git-r2-discovery", w04_p2_03_r2_repair_revision(fixture) == repair_sha)
        w04_p2_03_protected_source_guard(fixture)
        yes("git-r2-protected", True)
        frozen_paths = tuple(
            dict.fromkeys((*W04_P2_03_HARDENING_PATHS, *W04_P2_03_R2_REPAIR_PATHS))
        )
        for frozen in frozen_paths:
            target_path = fixture / frozen
            original = target_path.read_bytes()
            target_path.write_bytes(original + b"\n# unauthorized R2 drift\n")
            no("git-working-drift:" + frozen, lambda: w04_p2_03_protected_source_guard(fixture))
            target_path.write_bytes(original)
        (fixture / "EXTRA.md").write_text("# Unauthorized fourth\n", encoding="utf-8", newline="\n")
        git("add", "--", "EXTRA.md", repo=fixture)
        git("commit", "-q", "-m", "docs: arbitrary fourth", repo=fixture)
        no("git-fourth-rejected", lambda: w04_p2_03_hardening_revision(fixture))
        no("git-fourth-repair-rejected", lambda: w04_p2_03_r2_repair_revision(fixture))
        git("checkout", "-q", "--detach", repair_sha, repo=fixture)
        real_git = git

        def fixture_git(*arguments: str, repo: Path = ROOT) -> bytes:
            return real_git(*arguments, repo=fixture)

        for frozen in (
            ".github/workflows/ci.yml",
            "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json",
            "src/flowlens/investigation/__init__.py",
        ):
            target_path = fixture / frozen
            original = target_path.read_bytes()
            target_path.write_bytes(original + b"\n# unauthorized frozen drift\n")
            if frozen == ".github/workflows/ci.yml":
                no("git-frozen:" + frozen, lambda: workflow_guard(fixture))
            elif frozen.endswith("c09_gate_manifest.json"):
                no(
                    "git-frozen:" + frozen,
                    lambda target_path=target_path: runner.load_manifest(target_path),
                )
            else:
                git("add", "--", frozen, repo=fixture)
                git("commit", "-q", "-m", "fixture frozen runtime drift", repo=fixture)
                # Isolate the unchanged historical runtime guard from the topology guard.
                with patch.dict(
                    globals(),
                    {
                        "ROOT": fixture,
                        "git": fixture_git,
                        "w04_p2_03_protected_source_guard": lambda: None,
                    },
                ):
                    no("git-frozen:" + frozen, verify_collection_and_scope)
            target_path.write_bytes(original)
    require(
        len(completed) == len(W04_P2_03_R2_CONTROL_LABELS)
        and set(completed) == set(W04_P2_03_R2_CONTROL_LABELS),
        "P2_03 R2 deterministic control coverage/count drift",
    )
    return len(completed)


def w04_p2_03_source_history(tip: str, repo: Path = ROOT) -> list[dict[str, Any]]:
    """Validate source rows at an explicit tip; never discover an integration here."""
    revision = git("rev-parse", "--verify", tip + "^{commit}", repo=repo).decode().strip()
    rows = (
        git(
            "rev-list",
            "--reverse",
            "--topo-order",
            W04_POST_MERGE_BASE_SHA + ".." + revision,
            repo=repo,
        )
        .decode("ascii")
        .splitlines()
    )
    history = [w04_p2_03_commit_record(row, repo) for row in rows]
    validate_w04_p2_03_history(history)
    return history


def validate_w04_p2_03_pr8_merge_topology(
    head: str,
    parents: list[str],
    repair: str,
    merge_tree: bytes,
    repair_tree: bytes,
    feature_delta: bytes,
    reachable: bool,
) -> None:
    """Only an exact reachable main-first, repair-second, tree-identical merge."""
    require(
        re.fullmatch(r"[0-9a-f]{40}", head) is not None
        and head != "0" * 40
        and re.fullmatch(r"[0-9a-f]{40}", repair) is not None
        and repair
        not in {
            "0" * 40,
            W04_POST_MERGE_BASE_SHA,
            W04_P2_03_HARDENING_SHA,
            W04_P2_03_DOC_SYNC_SHA,
            W04_P2_03_R2_SHA,
        }
        and head != repair,
        "P2_03 PR8 invalid merge/repair identity",
    )
    require(
        parents == [W04_POST_MERGE_BASE_SHA, repair],
        "P2_03 PR8 exact two-parent main/repair order",
    )
    require(
        re.fullmatch(rb"[0-9a-f]{40}", merge_tree) is not None and merge_tree == repair_tree,
        "P2_03 PR8 merge tree drift",
    )
    require(not feature_delta, "P2_03 PR8 nonempty repair-to-merge delta")
    require(reachable, "P2_03 PR8 integration not reachable")


def w04_p2_03_pr8_integration_anchor(repo: Path = ROOT) -> str | None:
    """Discover integration independently, validating its explicit feature tip."""
    rows = (
        git(
            "rev-list",
            "--parents",
            "--reverse",
            "--topo-order",
            W04_POST_MERGE_BASE_SHA + "..HEAD",
            repo=repo,
        )
        .decode("ascii")
        .splitlines()
    )
    anchors: list[str] = []
    for row in rows:
        head, *parents = row.split()
        # Later ordinary merges are descendants, not additional integrations.
        if len(parents) < 2 or W04_POST_MERGE_BASE_SHA not in parents:
            continue
        require(
            len(parents) == 2 and parents[0] == W04_POST_MERGE_BASE_SHA,
            "P2_03 PR8 integration parent shape/order",
        )
        history = w04_p2_03_source_history(parents[1], repo)
        require(len(history) == 4, "P2_03 PR8 requires exact State-4 feature")
        repair = cast(str, history[3]["sha"])
        git("merge-base", "--is-ancestor", head, "HEAD", repo=repo)
        validate_w04_p2_03_pr8_merge_topology(
            head,
            parents,
            repair,
            git("rev-parse", head + "^{tree}", repo=repo).strip(),
            git("rev-parse", repair + "^{tree}", repo=repo).strip(),
            git("diff", repair, head, "--", repo=repo),
            True,
        )
        anchors.append(head)
    require(len(anchors) <= 1, "P2_03 PR8 multiple integration anchors")
    return anchors[0] if anchors else None


def w04_p2_03_source_tip(repo: Path = ROOT) -> str:
    """Dispatch after independent anchor discovery; descendants cannot add source rows."""
    anchor = w04_p2_03_pr8_integration_anchor(repo)
    tip = (
        git("show", "-s", "--format=%P", anchor, repo=repo).decode().split()[1]
        if anchor is not None
        else git("rev-parse", "HEAD", repo=repo).decode().strip()
    )
    w04_p2_03_source_history(tip, repo)
    return tip


def w04_p2_03_pr8_merge_repair_revision(repo: Path = ROOT) -> str | None:
    history = w04_p2_03_source_history(w04_p2_03_source_tip(repo), repo)
    return cast(str, history[3]["sha"]) if len(history) == 4 else None


def w04_p2_03_pr8_lifecycle(repo: Path = ROOT) -> str | None:
    repair = w04_p2_03_pr8_merge_repair_revision(repo)
    if repair is None:
        return None
    anchor = w04_p2_03_pr8_integration_anchor(repo)
    if anchor is None:
        return "P2_03_PR8_PREMERGE_REPAIR"
    head = git("rev-parse", "HEAD", repo=repo).decode().strip()
    return "P2_03_PR8_MERGED_MAIN" if head == anchor else "P2_03_POST_PR8_INTEGRATED"


def validate_w04_p2_03_pr8_verifier_sources(review_ready: str, current: str) -> None:
    """Prove exact e706 through the old chain before admitting literal R4 connectors."""
    accepted = git("show", W04_P2_03_R2_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode("utf-8")
    real_git = git

    def historical_git(*arguments: str, repo: Path = ROOT) -> bytes:
        # Historical diffs compare immutable snapshots, not e706 with live R4 files.
        if arguments in (
            ("diff", "--name-only", "HEAD", "--"),
            ("diff", "--name-only", ENTRY, "--"),
        ):
            left = W04_P2_03_R2_SHA if arguments[2] == "HEAD" else ENTRY
            return real_git("diff", "--name-only", left, W04_P2_03_R2_SHA, "--", repo=repo)
        bounded = [
            W04_P2_03_R2_SHA
            if argument == "HEAD"
            else argument[:-4] + W04_P2_03_R2_SHA
            if argument.endswith("..HEAD")
            else W04_P2_03_R2_SHA + argument[4:]
            if argument.startswith("HEAD:")
            else argument
            for argument in arguments
        ]
        return real_git(*bounded, repo=repo)

    with patch.dict(globals(), {"git": historical_git}):
        validate_w04_p2_03_r2_verifier_sources(review_ready, accepted)
    old_order, old = source_units(accepted)
    new_order, new = source_units(current)
    additions = set(W04_P2_03_PR8_MERGE_SOURCE_ADDITIONS)
    require(set(new) == set(old) | additions, "P2_03 PR8 verifier unit addition/removal")
    require(
        [name for name in new_order if name not in additions] == old_order
        and [name for name in new_order if name in additions]
        == list(W04_P2_03_PR8_MERGE_SOURCE_ADDITIONS),
        "P2_03 PR8 verifier unit identity/order",
    )
    require(
        set(W04_P2_03_PR8_MERGE_CONNECTORS)
        == {
            "validate_w04_p2_03_history",
            "w04_p2_03_hardening_revision",
            "w04_p2_03_r2_repair_revision",
            "w04_p2_03_protected_source_guard",
            "validate_w04_p2_03_r2_verifier_sources",
            "w04_pr7_merge_verifier_blob_guard",
        },
        "P2_03 PR8 connector authority drift",
    )
    for name in old_order:
        expected = old[name][0].encode("utf-8")
        for before, after in W04_P2_03_PR8_MERGE_CONNECTORS.get(name, ()):
            expected = replace_once(expected, before.encode("utf-8"), after.encode("utf-8"))
        require(new[name][0].encode("utf-8") == expected, "P2_03 PR8 unrelated span: " + name)
        if name in W04_P2_03_PR8_MERGE_CONNECTORS:
            a, b = copy.deepcopy(old[name][1]), copy.deepcopy(new[name][1])
            require(
                isinstance(a, ast.FunctionDef) and isinstance(b, ast.FunctionDef),
                "P2_03 PR8 connector function kind",
            )
            a, b = cast(ast.FunctionDef, a), cast(ast.FunctionDef, b)
            a.body, b.body = [], []
            require(
                ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False),
                "P2_03 PR8 connector signature/decorator drift",
            )
    require(
        W04_P2_03_R2_SHA == "e706e1f8ed920af0e840fbb9e97725d47d79a2c6"
        and W04_P2_03_PR8_MERGE_REPAIR_SUBJECT == "ci(post-w04): admit PR #8 merge lifecycle"
        and W04_P2_03_PR8_MERGE_REPAIR_PATHS
        == (
            CLOSEOUT_VERIFIER_PATH,
            "AGENTS.md",
            "docs/CURRENT_STATE.md",
        ),
        "P2_03 PR8 immutable authority constants",
    )
    repair = w04_p2_03_pr8_merge_repair_revision()
    require(repair is not None, "P2_03 PR8 source requires exact committed repair")
    frozen_source = git("show", str(repair) + ":" + CLOSEOUT_VERIFIER_PATH).decode("utf-8")
    frozen_order, frozen = source_units(frozen_source)
    require(new_order == frozen_order, "P2_03 PR8 committed unit order")
    for name in W04_P2_03_PR8_MERGE_SOURCE_ADDITIONS:
        require(new[name][0] == frozen[name][0], "P2_03 PR8 admitted span drift: " + name)
    require(
        current.encode("utf-8") == frozen_source.encode("utf-8")
        and git("ls-tree", "HEAD", "--", CLOSEOUT_VERIFIER_PATH)
        == git("ls-tree", str(repair), "--", CLOSEOUT_VERIFIER_PATH),
        "P2_03 PR8 committed verifier bytes/tree drift",
    )


def check_w04_p2_03_pr8_merge_controls() -> int:
    """Bounded helpers and one real-Git fixture; never recurse into the full gate."""
    completed: list[str] = []

    def yes(label: str, condition: bool) -> None:
        require(condition, "P2_03 PR8 positive control failed: " + label)
        require(
            label in W04_P2_03_PR8_MERGE_CONTROL_LABELS and label not in completed,
            "P2_03 PR8 control identity",
        )
        completed.append(label)

    def no(label: str, action: Any) -> None:
        rejected("P2_03 PR8 " + label, action)
        yes(label, True)

    repair = w04_p2_03_pr8_merge_repair_revision()
    require(repair is not None, "P2_03 PR8 controls require committed State-4 repair")
    repair = cast(str, repair)
    history = w04_p2_03_source_history(repair)
    yes("state-0", validate_w04_p2_03_history([]) is None)
    for length in (1, 2, 3, 4):
        yes(
            "state-" + str(length),
            validate_w04_p2_03_history(history[:length]) == W04_P2_03_HARDENING_SHA,
        )
    extra = {
        "sha": "f" * 40,
        "parents": [W04_P2_03_R2_SHA],
        "subject": "docs: unrelated descendant",
        "delta": {"EXTRA.md": "A"},
    }
    no("arbitrary-fourth", lambda: validate_w04_p2_03_history(history[:3] + [extra]))
    no("arbitrary-fifth", lambda: validate_w04_p2_03_history(history + [extra]))
    damaged = copy.deepcopy(history)
    damaged[2]["sha"] = "a" * 40
    no("unpinned-e706", lambda: validate_w04_p2_03_history(damaged))
    for label, key, value in (
        ("sha-zero", "sha", "0" * 40),
        ("sha-malformed", "sha", "g" * 40),
        ("sha-duplicate", "sha", W04_P2_03_R2_SHA),
        ("parent", "parents", [W04_POST_MERGE_BASE_SHA]),
        ("root", "parents", []),
        ("merge", "parents", [W04_P2_03_R2_SHA, W04_POST_MERGE_BASE_SHA]),
        ("subject", "subject", "ci: unrelated"),
        ("extra-path", "delta", {**history[3]["delta"], "EXTRA.md": "M"}),
    ):
        rows = copy.deepcopy(history)
        rows[3][key] = value
        no(
            "r4-" + label,
            lambda rows=rows: validate_w04_p2_03_history(rows),
        )
    for path in W04_P2_03_PR8_MERGE_REPAIR_PATHS:
        for status in ("missing", "A", "D", "R", "T"):
            rows = copy.deepcopy(history)
            if status == "missing":
                rows[3]["delta"].pop(path)
            else:
                rows[3]["delta"][path] = status
            no(
                "r4-" + status + ":" + path,
                lambda rows=rows: validate_w04_p2_03_history(rows),
            )
    no("reordered", lambda: validate_w04_p2_03_history([*history[:2], history[3], history[2]]))
    no("record-shape", lambda: validate_w04_p2_03_history([{**history[0], "extra": True}]))
    source = (ROOT / CLOSEOUT_VERIFIER_PATH).read_text(encoding="utf-8")
    _, units = source_units(source)
    forbidden = {
        "w04_p2_03_hardening_revision",
        "w04_p2_03_r2_repair_revision",
        "w04_p2_03_pr8_merge_repair_revision",
        "w04_p2_03_source_tip",
    }
    for name in ("w04_p2_03_source_history", "w04_p2_03_pr8_integration_anchor"):
        calls = {
            n.func.id
            for n in ast.walk(units[name][1])
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        }
        yes("nonrecursive:" + name, not (calls & forbidden))
    review = git("show", CLOSEOUT_REVIEW_READY_SHA + ":" + CLOSEOUT_VERIFIER_PATH).decode("utf-8")
    validate_w04_p2_03_pr8_verifier_sources(review, source)
    yes("source-chain", True)
    for name in (
        "require",
        "validate_w04_p2_03_history",
        "w04_p2_03_source_history",
        "w04_p2_03_pr8_integration_anchor",
        "w04_p2_03_source_tip",
        "w04_p2_03_protected_source_guard",
        "validate_w04_p2_03_pr8_verifier_sources",
    ):
        damaged_source = source.replace(units[name][0], units[name][0] + "    pass\n", 1)
        no(
            "source:" + name,
            lambda damaged_source=damaged_source: validate_w04_p2_03_pr8_verifier_sources(
                review, damaged_source
            ),
        )
    no(
        "source-extra",
        lambda: validate_w04_p2_03_pr8_verifier_sources(
            review,
            source + "\ndef unauthorized_r4_unit():\n    pass\n",
        ),
    )
    w04_p2_03_protected_source_guard()
    yes("current-protected", True)
    with tempfile.TemporaryDirectory(prefix="w04-p203-pr8-") as temporary:
        directory = Path(temporary)
        fixture = directory / "repo"
        git(
            "clone",
            "--quiet",
            "--no-hardlinks",
            "--no-checkout",
            str(ROOT),
            str(fixture),
            repo=directory,
        )
        for key, value in (
            ("core.autocrlf", "false"),
            ("user.name", "CI Test"),
            ("user.email", "ci@example.test"),
        ):
            git("config", key, value, repo=fixture)

        def checkout(revision: str) -> None:
            git("checkout", "-q", "--detach", revision, repo=fixture)

        def commit(tree: str, parents: list[str], subject: str) -> str:
            arguments = ["commit-tree", tree]
            for parent in parents:
                arguments.extend(("-p", parent))
            return git(*arguments, "-m", subject, repo=fixture).decode().strip()

        tree = git("rev-parse", repair + "^{tree}", repo=fixture).decode().strip()
        for index, revision in enumerate(
            (
                W04_POST_MERGE_BASE_SHA,
                W04_P2_03_HARDENING_SHA,
                W04_P2_03_DOC_SYNC_SHA,
                W04_P2_03_R2_SHA,
                repair,
            )
        ):
            checkout(revision)
            yes("git-state-" + str(index), w04_p2_03_source_tip(fixture) == revision)
        checkout(W04_P2_03_R2_SHA)
        (fixture / "EXTRA.md").write_text("unapproved fourth\n", encoding="utf-8")
        git("add", "--", "EXTRA.md", repo=fixture)
        git("commit", "-q", "-m", "docs: arbitrary fourth", repo=fixture)
        no("git-fourth-rejected", lambda: w04_p2_03_source_tip(fixture))
        checkout(repair)
        (fixture / "EXTRA.md").write_text("unapproved fifth\n", encoding="utf-8")
        git("add", "--", "EXTRA.md", repo=fixture)
        git("commit", "-q", "-m", "docs: arbitrary fifth", repo=fixture)
        no("git-fifth-rejected", lambda: w04_p2_03_source_tip(fixture))
        checkout(repair)
        protected = (
            "scripts/ci/classify_change.py",
            "scripts/ci/verify_publication.py",
            "tests/test_ci_change_classifier.py",
            "tests/test_ci_publication_gate.py",
            "tests/test_c09_ci_gate.py",
            CLOSEOUT_VERIFIER_PATH,
        )
        for path in (*protected, "AGENTS.md", "docs/CURRENT_STATE.md"):
            target = fixture / path
            original = target.read_bytes()
            target.write_bytes(original + b"\n# unapproved premerge drift\n")
            no("pre-protected:" + path, lambda: w04_p2_03_protected_source_guard(fixture))
            target.write_bytes(original)
        merge = commit(tree, [W04_POST_MERGE_BASE_SHA, repair], "Any merge subject is admissible")
        topology: dict[str, Any] = {
            "head": merge,
            "parents": [W04_POST_MERGE_BASE_SHA, repair],
            "repair": repair,
            "merge_tree": tree.encode("ascii"),
            "repair_tree": tree.encode("ascii"),
            "feature_delta": b"",
            "reachable": True,
        }
        validate_w04_p2_03_pr8_merge_topology(**topology)
        yes("topology-positive", True)
        for label, key, case_value in (
            ("wrong-main", "parents", [W04_P2_03_HARDENING_SHA, repair]),
            ("wrong-feature", "parents", [W04_POST_MERGE_BASE_SHA, W04_P2_03_DOC_SYNC_SHA]),
            ("direct-e706", "parents", [W04_POST_MERGE_BASE_SHA, W04_P2_03_R2_SHA]),
            ("reversed", "parents", [repair, W04_POST_MERGE_BASE_SHA]),
            ("octopus", "parents", [W04_POST_MERGE_BASE_SHA, repair, W04_P2_03_R2_SHA]),
            ("root", "parents", []),
            ("single", "parents", [repair]),
            ("tree", "merge_tree", b"a" * 40),
            ("delta", "feature_delta", b"M\tREADME.md\n"),
            ("unreachable", "reachable", False),
        ):
            no(
                "topology-" + label,
                lambda key=key, case_value=case_value: validate_w04_p2_03_pr8_merge_topology(
                    **{**topology, key: case_value}
                ),
            )
        for label, parents in (
            ("wrong-main", [W04_P2_03_HARDENING_SHA, repair]),
            ("wrong-feature", [W04_POST_MERGE_BASE_SHA, W04_P2_03_DOC_SYNC_SHA]),
            ("direct-e706", [W04_POST_MERGE_BASE_SHA, W04_P2_03_R2_SHA]),
            ("reversed", [repair, W04_POST_MERGE_BASE_SHA]),
            ("octopus", [W04_POST_MERGE_BASE_SHA, repair, W04_P2_03_R2_SHA]),
        ):
            checkout(commit(tree, parents, "hostile " + label))
            no("git-" + label, lambda: w04_p2_03_source_tip(fixture))
        checkout(merge)
        yes("git-anchor", w04_p2_03_pr8_integration_anchor(fixture) == merge)
        yes("git-merge-tip", w04_p2_03_source_tip(fixture) == repair)
        yes("git-merge-lifecycle", w04_p2_03_pr8_lifecycle(fixture) == "P2_03_PR8_MERGED_MAIN")
        for path in protected:
            target = fixture / path
            original = target.read_bytes()
            target.write_bytes(original + b"\n# unapproved postmerge drift\n")
            no("post-protected:" + path, lambda: w04_p2_03_protected_source_guard(fixture))
            target.write_bytes(original)
        # A genuine changed tree also has a nonempty repair-to-merge diff.
        target = fixture / "README.md"
        target.write_bytes(target.read_bytes() + b"\nDisposable resolution drift\n")
        git("add", "--", "README.md", repo=fixture)
        drift_tree = git("write-tree", repo=fixture).decode().strip()
        drift_merge = commit(drift_tree, [W04_POST_MERGE_BASE_SHA, repair], "resolution drift")
        yes("git-real-nonempty-delta", bool(git("diff", repair, drift_merge, "--", repo=fixture)))
        checkout(drift_merge)
        no("git-tree-drift", lambda: w04_p2_03_source_tip(fixture))
        checkout(merge)
        for path in ("README.md", "AGENTS.md", "docs/CURRENT_STATE.md"):
            target = fixture / path
            target.write_bytes(
                target.read_bytes() + b"\nDisposable post-integration lifecycle note.\n"
            )
        git("add", "--", "README.md", "AGENTS.md", "docs/CURRENT_STATE.md", repo=fixture)
        git("commit", "-q", "-m", "docs: post-integration fixture", repo=fixture)
        docs = git("rev-parse", "HEAD", repo=fixture).decode().strip()
        docs_tree = git("rev-parse", "HEAD^{tree}", repo=fixture).decode().strip()
        w04_p2_03_protected_source_guard(fixture)
        yes("git-docs-protected", True)
        yes("git-docs-tip", w04_p2_03_source_tip(fixture) == repair)
        yes("git-docs-lifecycle", w04_p2_03_pr8_lifecycle(fixture) == "P2_03_POST_PR8_INTEGRATED")
        side = commit(docs_tree, [merge], "docs: independent benign side")
        later_merge = commit(docs_tree, [docs, side], "docs: later benign two-parent merge")
        checkout(later_merge)
        yes("git-later-merge-tip", w04_p2_03_source_tip(fixture) == repair)
        yes("git-later-merge-anchor", w04_p2_03_pr8_integration_anchor(fixture) == merge)
        yes(
            "git-later-merge-lifecycle",
            w04_p2_03_pr8_lifecycle(fixture) == "P2_03_POST_PR8_INTEGRATED",
        )
        (fixture / "NONPROTECTED_TOPOLOGY.txt").write_text(
            "Topology continuity only; no W05 planner claim.\n",
            encoding="utf-8",
        )
        git("add", "--", "NONPROTECTED_TOPOLOGY.txt", repo=fixture)
        git("commit", "-q", "-m", "fixture: benign non-protected descendant", repo=fixture)
        yes("git-nonprotected-tip", w04_p2_03_source_tip(fixture) == repair)
        yes("git-nonprotected-anchor", w04_p2_03_pr8_integration_anchor(fixture) == merge)
        yes(
            "git-nonprotected-lifecycle",
            w04_p2_03_pr8_lifecycle(fixture) == "P2_03_POST_PR8_INTEGRATED",
        )
        checkout(merge)
        target = fixture / "src/flowlens/investigation/__init__.py"
        target.write_bytes(target.read_bytes() + b"\n# unauthorized runtime descendant\n")
        git("add", "--", "src/flowlens/investigation/__init__.py", repo=fixture)
        git("commit", "-q", "-m", "fixture: protected runtime drift", repo=fixture)
        real_git = git
        protected_guard = w04_p2_03_protected_source_guard

        def fixture_git(*arguments: str, repo: Path = ROOT) -> bytes:
            return real_git(*arguments, repo=fixture)

        with patch.dict(
            globals(),
            {
                "ROOT": fixture,
                "git": fixture_git,
                "w04_p2_03_protected_source_guard": lambda: protected_guard(fixture),
            },
        ):
            no("git-post-runtime-drift", verify_collection_and_scope)
        checkout(merge)
        second_anchor = commit(tree, [W04_POST_MERGE_BASE_SHA, repair], "second integration")
        combined = commit(tree, [merge, second_anchor], "combine duplicate integrations")
        checkout(combined)
        no("git-multiple-anchors", lambda: w04_p2_03_source_tip(fixture))
    require(
        len(completed) == len(W04_P2_03_PR8_MERGE_CONTROL_LABELS)
        and set(completed) == set(W04_P2_03_PR8_MERGE_CONTROL_LABELS),
        "P2_03 PR8 deterministic control coverage/count drift",
    )
    return len(completed)


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
    if len(history) > 4:
        return validate_c10_lifecycle(history, working, changed)
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
    integration = w04_pr7_integration_anchor(repo)
    if integration is not None:
        working = set(git("diff", "--name-only", "HEAD", "--", repo=repo).decode().splitlines())
        working.update(
            git("ls-files", "--others", "--exclude-standard", repo=repo).decode().splitlines()
        )
        require(not working, "uncommitted post-integration lifecycle delta")
        return "W04_PR7_MERGED_MAIN" if head == integration else "W04_POST_MERGE_INTEGRATED"
    repaired = w04_pr7_pre_integration_guard(changed, repo)
    if repaired is not None:
        return repaired
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
    if "C10_ENTRY_SHA = " in current:
        validate_c10_verifier_sources(review_ready, current)
        return
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
    c10_verifier_blob_guard(repo)
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
        "scripts/ci/plan_non_integration_shards.py",
        "scripts/ci/pytest_outcome_receipt.py",
        "scripts/ci/run_non_integration_shard.py",
        "scripts/ci/verify_non_integration_shards.py",
        "scripts/ci/run_w03_ai_loop_gate.py",
        "scripts/ci/verify_w04_source_evolution.py",
    )
    w04_p2_03_protected_source_guard()
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
