"""ai-slide-deck-generator — turn a prompt or outline into a rendered .pptx deck.

Public surface:
    DeckGenerator   — high-level orchestrator (prompt -> DeckPlan -> .pptx)
    DeckPlan        — in-memory slide model
    SlideRenderer   — plan -> python-pptx Presentation
    load_config     — reads config/deck.toml with env overrides
"""

from .core.generator import DeckGenerator
from .core.plan import DeckPlan, Slide, SlideBlock
from .render.pptx_renderer import SlideRenderer
from .config.loader import load_config

__version__ = "0.4.2"
__all__ = [
    "DeckGenerator",
    "DeckPlan",
    "Slide",
    "SlideBlock",
    "SlideRenderer",
    "load_config",
    "__version__",
]