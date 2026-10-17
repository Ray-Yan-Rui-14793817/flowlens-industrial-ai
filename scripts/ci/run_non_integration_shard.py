"""Run one validated file-atomic shard in a fresh pytest receipt process."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from plan_non_integration_shards import (
    BASELINE,
    MARKER,
    SHARD_COUNT,
    WEIGHTS,
    ProofError,
    collect_nodes,
    read_json,
    validate_plan,
    verify_head,
)


def run_shard(plan_path: Path, head: str, shard_id: int, role: str, output: Path) -> int:
    verify_head(head)
    if type(shard_id) is not int or shard_id not in range(SHARD_COUNT):
        raise ProofError("unexpected shard ID")
    if role not in {"shadow-shard", "nonint-shard"}:
        raise ProofError("unexpected shard role")
    plan = read_json(plan_path)
    validate_plan(plan, read_json(WEIGHTS), read_json(BASELINE), head)
    shard = plan["shards"][shard_id]
    if collect_nodes(MARKER, files=shard["files"]) != shard["nodeids"]:
        raise ProofError("shard collect-only exact-set mismatch")
    print(
        "SHARD_ASSIGNMENT "
        + json.dumps(
            {
                key: shard[key]
                for key in (
                    "shard_id",
                    "file_count",
                    "node_count",
                    "nodeids_sha256",
                    "estimated_weight_seconds",
                )
            },
            sort_keys=True,
        ),
        flush=True,
    )
    arguments = [
        sys.executable,
        "-B",
        str(Path(__file__).with_name("pytest_outcome_receipt.py")),
        "--plan",
        str(plan_path),
        "--expected-head",
        head,
        "--role",
        role,
        "--marker",
        MARKER,
        "--shard-id",
        str(shard_id),
        "--output-dir",
        str(output),
    ]
    return subprocess.run(arguments, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--shard-id", type=int, required=True)
    parser.add_argument("--role", choices=["shadow-shard", "nonint-shard"], required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run_shard(args.plan, args.expected_head, args.shard_id, args.role, args.output_dir)
    except (ProofError, OSError) as exc:
        print(f"SHARD_FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
