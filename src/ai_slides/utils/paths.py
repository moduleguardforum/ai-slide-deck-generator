"""Path helpers — safe filenames, directory creation."""

from __future__ import annotations

from pathlib import Path

_UNSAFE = set('<>:"/\\|?*')


def safe_filename(name: str, fallback: str = "deck") -> str:
    cleaned = "".join(c for c in name if c not in _UNSAFE).strip().strip(".")
    return cleaned or fallback


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path