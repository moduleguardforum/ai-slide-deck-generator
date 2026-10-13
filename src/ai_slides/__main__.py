"""Console entry: `python -m ai_slides --prompt "..." --out deck.pptx`."""

from __future__ import annotations

import argparse
import logging
import sys

from .config.loader import load_config
from .core.generator import DeckGenerator


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ai_slides", description="AI slide deck generator")
    p.add_argument("--prompt", "-p", required=False, help="Topic or prompt for the deck")
    p.add_argument("--outline", "-o", help="Path to a plaintext outline (one bullet per line)")
    p.add_argument("--out", default="deck.pptx", help="Output .pptx path")
    p.add_argument("--theme", default=None, help="Theme name from config/deck.toml [themes]")
    p.add_argument("--slides", type=int, default=None, help="Target slide count")
    p.add_argument("--model", default=None, help="Override provider model id")
    p.add_argument("--dry-run", action="store_true", help="Plan only, skip rendering")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    cfg = load_config()
    if args.theme:
        cfg.theme = args.theme
    if args.model:
        cfg.model_id = args.model
    if args.slides:
        cfg.target_slides = args.slides

    generator = DeckGenerator(cfg)
    plan = generator.plan(prompt=args.prompt, outline_path=args.outline)
    logging.info("planned %d slides", len(plan.slides))

    if args.dry_run:
        for s in plan.slides:
            print(f"[{s.layout}] {s.title}")
        return 0

    generator.render(plan, out_path=args.out)
    logging.info("wrote %s", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())