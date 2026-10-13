"""Deck plan: the intermediate representation between LLM output and .pptx."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Layout = Literal["title", "section", "bullets", "two-column", "quote", "closing"]


@dataclass(slots=True)
class SlideBlock:
    kind: Literal["bullet", "paragraph", "note"]
    text: str

    def trimmed(self, max_chars: int) -> "SlideBlock":
        if len(self.text) <= max_chars:
            return self
        return SlideBlock(self.kind, self.text[: max_chars - 1].rstrip() + "\u2026")


@dataclass(slots=True)
class Slide:
    title: str
    layout: Layout = "bullets"
    blocks: list[SlideBlock] = field(default_factory=list)
    speaker_notes: str = ""
    column_split: int = 0  # for two-column: number of blocks in left column


@dataclass(slots=True)
class DeckPlan:
    title: str
    subtitle: str = ""
    slides: list[Slide] = field(default_factory=list)
    theme: str = "midnight"

    def validate(self, max_bullets: int, max_chars: int) -> list[str]:
        problems: list[str] = []
        if not self.slides:
            problems.append("deck has no slides")
        for i, s in enumerate(self.slides):
            if not s.title.strip():
                problems.append(f"slide[{i}] missing title")
            bullets = [b for b in s.blocks if b.kind == "bullet"]
            if len(bullets) > max_bullets:
                problems.append(f"slide[{i}] has {len(bullets)} bullets (max {max_bullets})")
            for j, b in enumerate(s.blocks):
                if len(b.text) > max_chars:
                    s.blocks[j] = b.trimmed(max_chars)
        return problems