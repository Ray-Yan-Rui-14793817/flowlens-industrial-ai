"""Deterministic identifier helpers for synthetic baseline rows."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from flowlens.data.generation.config import GenerationConfig


def dataset_namespace(config: GenerationConfig) -> str:
    """Derive a stable namespace from every business-content identity input."""

    identity = {
        "generator_version": config.generator_version,
        "period_end": config.period_end.isoformat(),
        "period_start": config.period_start.isoformat(),
        "profile": config.profile.value,
        "seed": config.seed,
    }
    payload = json.dumps(identity, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class DeterministicIdFactory:
    """Create compact, human-inspectable IDs from stable row ordinals."""

    namespace: str

    @classmethod
    def from_config(cls, config: GenerationConfig) -> DeterministicIdFactory:
        return cls(dataset_namespace(config))

    @property
    def dataset_version_id(self) -> str:
        return f"dsv_{self.namespace[:32]}"

    def make(self, prefix: str, ordinal: int, max_length: int) -> str:
        if not prefix or not prefix.isascii() or not prefix.isalnum():
            raise ValueError("ID prefix must be non-empty ASCII alphanumeric text")
        if ordinal < 1:
            raise ValueError("ID ordinal must be positive")
        value = f"{prefix}_{self.namespace[:12]}_{ordinal:08d}"
        if len(value) > max_length:
            raise ValueError(f"generated identifier exceeds VARCHAR({max_length})")
        return value
