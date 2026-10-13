"""Built-in themes. Each theme maps to a python-pptx template file under assets/themes/."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Theme:
    name: str
    template: str
    accent_hex: str
    title_font: str
    body_font: str


THEMES: dict[str, Theme] = {
    "midnight": Theme("midnight", "midnight.pptx", "5B8DEF", "Inter", "Inter"),
    "editorial": Theme("editorial", "editorial.pptx", "C2410C", "Source Serif", "Source Sans"),
    "mono": Theme("mono", "mono.pptx", "111827", "JetBrains Mono", "JetBrains Mono"),
    "sunrise": Theme("sunrise", "sunrise.pptx", "F59E0B", "Poppins", "Poppins"),
}

_THEME_DIR = Path(__file__).resolve().parents[3] / "assets" / "themes"


def resolve_theme(name: str) -> tuple[Theme, Path]:
    theme = THEMES.get(name)
    if theme is None:
        raise KeyError(f"unknown theme {name!r}; available: {sorted(THEMES)}")
    return theme, _THEME_DIR / theme.template