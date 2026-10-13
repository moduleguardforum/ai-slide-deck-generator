"""PlanCache — disk cache keyed by (model, prompt, target_slides) hash.

Reuse across runs keeps iteration cheap while drafting a deck.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from ..core.plan import DeckPlan, Slide, SlideBlock

log = logging.getLogger(__name__)


class PlanCache:
    def __init__(self, cache_dir: Path) -> None:
        self.dir = cache_dir
        self.dir.mkdir(parents=True, exist_ok=True)

    def _key(self, model: str, prompt: str, n: int) -> str:
        h = hashlib.sha256(f"{model}|{prompt}|{n}".encode("utf-8")).hexdigest()[:16]
        return f"plan_{h}.json"

    def get(self, model: str, prompt: str, n: int) -> DeckPlan | None:
        path = self.dir / self._key(model, prompt, n)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.warning("cache entry corrupt: %s", path)
            return None
        slides = [
            Slide(
                title=s["title"],
                layout=s.get("layout", "bullets"),
                blocks=[SlideBlock(b["kind"], b["text"]) for b in s.get("blocks", [])],
                speaker_notes=s.get("speaker_notes", ""),
            )
            for s in data.get("slides", [])
        ]
        return DeckPlan(title=data.get("title", ""), subtitle=data.get("subtitle", ""), slides=slides)

    def put(self, model: str, prompt: str, n: int, plan: DeckPlan) -> None:
        path = self.dir / self._key(model, prompt, n)
        payload = {
            "title": plan.title,
            "subtitle": plan.subtitle,
            "slides": [
                {
                    "title": s.title,
                    "layout": s.layout,
                    "blocks": [{"kind": b.kind, "text": b.text} for b in s.blocks],
                    "speaker_notes": s.speaker_notes,
                }
                for s in plan.slides
            ],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")