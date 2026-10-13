"""DeckGenerator — orchestrates prompt -> plan -> rendered deck.

Flow:
    prompt/outline  ->  OutlineBuilder (LLM or heuristic)
                    ->  DeckPlan
                    ->  SlideRenderer -> .pptx
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..config.loader import DeckConfig
from ..render.pptx_renderer import SlideRenderer
from ..services.llm_client import LLMClient, LLMError
from ..services.outline_builder import OutlineBuilder
from .plan import DeckPlan

log = logging.getLogger(__name__)


class DeckGenerator:
    def __init__(self, config: DeckConfig, client: LLMClient | None = None) -> None:
        self.config = config
        self.client = client or LLMClient(config)
        self.builder = OutlineBuilder(config, self.client)

    def plan(self, prompt: str | None = None, outline_path: str | None = None) -> DeckPlan:
        if not prompt and not outline_path:
            raise ValueError("either --prompt or --outline is required")

        if outline_path:
            text = Path(outline_path).read_text(encoding="utf-8")
            plan = self.builder.from_outline(text, title_hint=prompt)
        else:
            try:
                plan = self.builder.from_prompt(prompt or "")
            except LLMError as exc:
                log.warning("LLM unavailable (%s); falling back to heuristic outline", exc)
                plan = self.builder.heuristic(prompt or "")

        plan.theme = self.config.theme
        problems = plan.validate(
            self.config.max_bullets_per_slide,
            self.config.max_chars_per_bullet,
        )
        for p in problems:
            log.warning("plan issue: %s", p)
        return plan

    def render(self, plan: DeckPlan, out_path: str | Path) -> Path:
        renderer = SlideRenderer(self.config)
        return renderer.render(plan, Path(out_path))