"""Layout engine — chooses a slide layout by name, maps our Layout literal
to the template's layout index. Keeps renderer dumb and layout-aware here."""

from __future__ import annotations

import logging

from ..core.plan import Slide

log = logging.getLogger(__name__)

_LAYOUT_INDEX = {
    "title": 0,
    "section": 2,
    "bullets": 1,
    "two-column": 3,
    "quote": 5,
    "closing": 6,
}


def apply_layout(prs, slide: Slide, theme):
    idx = _LAYOUT_INDEX.get(slide.layout, 1)
    try:
        layout = prs.slide_layouts[idx]
    except IndexError:
        log.warning("layout index %d missing in template; falling back to 1", idx)
        layout = prs.slide_layouts[1]
    s = prs.slides.add_slide(layout)
    if s.shapes.title is not None and slide.title:
        s.shapes.title.text = slide.title
    return s