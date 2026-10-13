"""Renderer smoke test — produces a .pptx and asserts it opens."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation

from ai_slides.config.loader import DeckConfig
from ai_slides.core.plan import DeckPlan, Slide, SlideBlock
from ai_slides.render.pptx_renderer import SlideRenderer


def _sample_plan() -> DeckPlan:
    return DeckPlan(
        title="Sample Deck",
        subtitle="Renderer smoke test",
        slides=[
            Slide(title="Overview", layout="bullets", blocks=[
                SlideBlock("bullet", "First bullet"),
                SlideBlock("bullet", "Second bullet"),
            ], speaker_notes="Talk track goes here."),
            Slide(title="Closing", layout="closing", blocks=[]),
        ],
        theme="midnight",
    )


def test_render_writes_valid_pptx(tmp_path: Path) -> None:
    cfg = DeckConfig(theme="midnight")
    out = tmp_path / "deck.pptx"
    SlideRenderer(cfg).render(_sample_plan(), out)
    assert out.exists() and out.stat().st_size > 0
    prs = Presentation(str(out))
    assert len(prs.slides) >= 1