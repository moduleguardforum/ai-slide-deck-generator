"""Schema validation for LLM JSON output. Hand-rolled to avoid a pydantic dep
for a hobby project — swap in pydantic v2 if you need coercion."""

from __future__ import annotations

from typing import Any

VALID_LAYOUTS = {"title", "section", "bullets", "two-column", "quote", "closing"}
VALID_KINDS = {"bullet", "paragraph", "note"}


class SchemaError(ValueError):
    pass


def _check_slide(raw: dict[str, Any], idx: int) -> None:
    if not isinstance(raw.get("title"), str):
        raise SchemaError(f"slide[{idx}].title must be a string")
    if raw.get("layout", "bullets") not in VALID_LAYOUTS:
        raise SchemaError(f"slide[{idx}].layout {raw.get('layout')!r} invalid")
    for j, b in enumerate(raw.get("blocks", [])):
        if b.get("kind", "bullet") not in VALID_KINDS:
            raise SchemaError(f"slide[{idx}].blocks[{j}].kind invalid")
        if not isinstance(b.get("text"), str):
            raise SchemaError(f"slide[{idx}].blocks[{j}].text must be a string")


def validate_deck(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise SchemaError("deck payload must be an object")
    if not isinstance(data.get("title"), str):
        raise SchemaError("deck.title must be a string")
    for i, s in enumerate(data.get("slides", [])):
        _check_slide(s, i)
    return data


SlideSchema = dict  # alias for typing docs
DeckSchema = dict