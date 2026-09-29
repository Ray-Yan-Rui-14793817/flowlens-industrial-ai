"""Frozen prompt bytes, manifest, and output schema tests for W03-C08."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flowlens.decision.c08_policy import (
    MODEL_SECTION_KEYS,
    PROMPT_SHA256,
    PROMPT_VERSION,
    RUNTIME_SYSTEM_PROMPT,
    provider_output_schema,
)

ROOT = Path(__file__).parents[1]


def test_runtime_prompt_bytes_match_frozen_hash_and_manifest() -> None:
    prompt_bytes = RUNTIME_SYSTEM_PROMPT.encode("utf-8")
    manifest = json.loads(
        (
            ROOT / "docs/w03/checkpoints/c08/specs/prompt_manifest.json"
        ).read_text(encoding="utf-8")
    )

    assert PROMPT_VERSION == "w03-c08-runtime-prompt-v1"
    assert len(prompt_bytes) == 2479
    assert hashlib.sha256(prompt_bytes).hexdigest() == PROMPT_SHA256
    assert manifest["sha256"] == PROMPT_SHA256
    assert manifest["byte_length"] == len(prompt_bytes)
    assert "\r" not in RUNTIME_SYSTEM_PROMPT
    assert RUNTIME_SYSTEM_PROMPT.endswith("\n")


def test_embedded_output_schema_matches_published_schema() -> None:
    published = json.loads(
        (
            ROOT / "docs/w03/checkpoints/c08/specs/explanation_output_schema.json"
        ).read_text(encoding="utf-8")
    )
    embedded = provider_output_schema()

    assert published == embedded
    assert tuple(
        published["properties"]["sections"]["items"]["properties"]["section_key"][
            "enum"
        ]
    ) == MODEL_SECTION_KEYS
