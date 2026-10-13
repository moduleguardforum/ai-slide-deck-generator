"""File handler — outline ingestion and output path resolution."""

from __future__ import annotations

from pathlib import Path


class FileHandler:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = (base_dir or Path.cwd()).resolve()

    def read_outline(self, path: str | Path) -> list[str]:
        p = Path(path)
        if not p.is_absolute():
            p = self.base_dir / p
        if not p.exists():
            raise FileNotFoundError(f"outline not found: {p}")
        lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()]
        return [ln for ln in lines if ln and not ln.startswith("#")]

    def resolve_output(self, out: str | Path) -> Path:
        p = Path(out)
        if not p.is_absolute():
            p = self.base_dir / p
        if p.suffix.lower() != ".pptx":
            p = p.with_suffix(".pptx")
        p.parent.mkdir(parents=True, exist_ok=True)
        return p