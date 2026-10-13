"""Config loader: TOML defaults + env overrides + CLI-friendly dataclass.

Precedence (lowest -> highest):
    config/deck.toml  ->  AISLIDES_* env vars  ->  explicit kwargs
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "deck.toml"


@dataclass(slots=True)
class DeckConfig:
    model_id: str = "gpt-4o-mini"
    provider: str = "openai"
    target_slides: int = 10
    theme: str = "midnight"
    max_bullets_per_slide: int = 5
    max_chars_per_bullet: int = 140
    temperature: float = 0.6
    request_timeout_s: float = 45.0
    retry_attempts: int = 3
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".cache" / "ai_slides")
    extra: dict[str, Any] = field(default_factory=dict)

    def with_overrides(self, **kw: Any) -> "DeckConfig":
        return replace(self, **{k: v for k, v in kw.items() if v is not None})


def _coerce(value: str) -> Any:
    low = value.lower()
    if low in {"true", "false"}:
        return low == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def load_config(path: Path | None = None) -> DeckConfig:
    cfg_path = path or DEFAULT_CONFIG_PATH
    raw: dict[str, Any] = {}
    if cfg_path.exists():
        raw = tomllib.loads(cfg_path.read_text(encoding="utf-8"))

    deck = raw.get("deck", {})
    provider = raw.get("provider", {})

    cfg = DeckConfig(
        model_id=provider.get("model", deck.get("model_id", DeckConfig.model_id)),
        provider=provider.get("name", DeckConfig.provider),
        target_slides=int(deck.get("target_slides", DeckConfig.target_slides)),
        theme=deck.get("theme", DeckConfig.theme),
        max_bullets_per_slide=int(deck.get("max_bullets_per_slide", DeckConfig.max_bullets_per_slide)),
        max_chars_per_bullet=int(deck.get("max_chars_per_bullet", DeckConfig.max_chars_per_bullet)),
        temperature=float(provider.get("temperature", DeckConfig.temperature)),
        request_timeout_s=float(provider.get("timeout_s", DeckConfig.request_timeout_s)),
        retry_attempts=int(provider.get("retry_attempts", DeckConfig.retry_attempts)),
    )

    for key, value in os.environ.items():
        if not key.startswith("AISLIDES_"):
            continue
        field_name = key[len("AISLIDES_"):].lower()
        if hasattr(cfg, field_name):
            setattr(cfg, field_name, _coerce(value))
        else:
            cfg.extra[field_name] = _coerce(value)

    return cfg