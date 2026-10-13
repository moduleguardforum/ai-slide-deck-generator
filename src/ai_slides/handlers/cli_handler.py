"""CLI handler — thin wrapper used by __main__ and by the GUI bridge."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from ..config.loader import DeckConfig
from ..core.generator import DeckGenerator
from ..core.plan import DeckPlan

log = logging.getLogger(__name__)


@dataclass(slots=True)
class RunResult:
    plan: DeckPlan
    out_path: str | None
    warnings: list[str]


class CLIHandler:
    def __init__(self, config: DeckConfig) -> None:
        self.config = config
        self.generator = DeckGenerator(config)

    def run(self, prompt: str | None, outline: str | None, out: str | None, dry: bool) -> RunResult:
        plan = self.generator.plan(prompt=prompt, outline_path=outline)
        if dry or out is None:
            return RunResult(plan=plan, out_path=None, warnings=[])
        path = self.generator.render(plan, out)
        return RunResult(plan=plan, out_path=str(path), warnings=[])