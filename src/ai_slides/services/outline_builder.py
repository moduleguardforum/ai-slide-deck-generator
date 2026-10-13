"""OutlineBuilder — prompt -> DeckPlan.

Two strategies:
  * from_prompt  : LLM call, structured JSON back, strict schema.
  * heuristic    : offline fallback, splits prompt into sections.
"""

from __future__ import annotations

import logging
import re

from ..config.loader import DeckConfig
from ..core.plan import DeckPlan, Slide, SlideBlock
from .llm_client import LLMClient

log = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a presentation architect. Given a topic, return a JSON
object with keys: title (string), subtitle (string), slides (array). Each slide:
{"title": str, "layout": one of ["title","section","bullets","two-column","quote","closing"],
 "blocks": [{"kind": "bullet"|"paragraph"|"note", "text": str}], "speaker_notes": str}.
Keep bullets under 140 characters. No markdown. No commentary outside JSON."""


class OutlineBuilder:
    def __init__(self, config: DeckConfig, client: LLMClient) -> None:
        self.config = config
        self.client = client

    def from_prompt(self, prompt: str) -> DeckPlan:
        user = f"Topic: {prompt}\nTarget slide count: {self.config.target_slides}"
        data = self.client.complete_json(_SYSTEM_PROMPT, user)
        return _plan_from_dict(data)

    def from_outline(self, text: str, title_hint: str | None = None) -> DeckPlan:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        title = title_hint or (lines[0] if lines else "Untitled Deck")
        slides: list[Slide] = [Slide(title=title, layout="title", blocks=[])]
        current: Slide | None = None
        for ln in lines:
            if ln.startswith("#"):
                current = Slide(title=ln.lstrip("# ").strip(), layout="section")
                slides.append(current)
            elif ln.startswith(("-", "*", "\u2022")):
                if current is None:
                    current = Slide(title="Overview", layout="bullets")
                    slides.append(current)
                current.blocks.append(SlideBlock("bullet", ln.lstrip("-*\u2022 ").strip()))
            else:
                if current is None:
                    current = Slide(title=ln, layout="section")
                    slides.append(current)
        return DeckPlan(title=title, slides=slides, theme=self.config.theme)

    def heuristic(self, prompt: str) -> DeckPlan:
        words = re.findall(r"[A-Za-z0-9]+", prompt)
        title = " ".join(words[:8]).title() or "Untitled Deck"
        sections = ["Overview", "Problem", "Approach", "Architecture", "Results", "Next Steps"]
        slides = [Slide(title=title, layout="title")]
        for s in sections[: self.config.target_slides - 1]:
            slides.append(Slide(
                title=s,
                layout="bullets",
                blocks=[SlideBlock("bullet", f"Key point about {s.lower()}")],
                speaker_notes=f"Auto-generated placeholder for '{s}'.",
            ))
        return DeckPlan(title=title, slides=slides, theme=self.config.theme)


def _plan_from_dict(data: dict) -> DeckPlan:
    slides: list[Slide] = []
    for raw in data.get("slides", []):
        blocks = [SlideBlock(b.get("kind", "bullet"), b.get("text", "")) for b in raw.get("blocks", [])]
        slides.append(Slide(
            title=raw.get("title", ""),
            layout=raw.get("layout", "bullets"),
            blocks=blocks,
            speaker_notes=raw.get("speaker_notes", ""),
        ))
    return DeckPlan(
        title=data.get("title", "Untitled Deck"),
        subtitle=data.get("subtitle", ""),
        slides=slides,
    )