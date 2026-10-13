"""Small text utilities used by the outline builder and renderer."""

from __future__ import annotations

import re

_SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def truncate(text: str, limit: int, ellipsis: str = "\u2026") -> str:
    if len(text) <= limit:
        return text
    return text[: limit - len(ellipsis)].rstrip() + ellipsis


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_RE.split(text.strip()) if s.strip()]


def slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.lower()).strip("-")