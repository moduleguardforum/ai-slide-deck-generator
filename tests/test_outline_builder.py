"""Unit tests for OutlineBuilder — offline heuristic + outline parsing."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_slides.config.loader import DeckConfig
from ai_slides.services.outline_builder import OutlineBuilder


class _NoopClient:
    def complete_json(self, system, user):  # pragma: no cover - not used here
        raise AssertionError("LLM should not be called in these tests")


@pytest.fixture()
def builder() -> OutlineBuilder:
    cfg = DeckConfig(target_slides=6)
    return OutlineBuilder(cfg, _NoopClient())  # type: ignore[arg-type]


def test_heuristic_returns_target_slide_count(builder: OutlineBuilder) -> None:
    plan = builder.heuristic("vector databases for retrieval")
    assert plan.title
    assert 1 <= len(plan.slides) <= 6


def test_from_outline_parses_sections_and_bullets(builder: OutlineBuilder) -> None:
    text = (
        "# Intro\n"
        "- first point\n"
        "- second point\n"
        "# Architecture\n"
        "- components\n"
    )
    plan = builder.from_outline(text, title_hint="My Deck")
    assert plan.title == "My Deck"
    titles = [s.title for s in plan.slides]
    assert "Intro" in titles and "Architecture" in titles


def test_plan_validate_trims_long_bullets(builder: OutlineBuilder) -> None:
    plan = builder.from_outline("# S\n- " + "x" * 500)
    problems = plan.validate(max_bullets=5, max_chars=140)
    assert problems == []
    bullet = next(b for s in plan.slides for b in s.blocks if b.kind == "bullet")
    assert len(bullet.text) <= 140