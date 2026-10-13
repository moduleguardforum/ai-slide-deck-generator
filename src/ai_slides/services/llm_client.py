"""LLM client wrapper.

Targets the OpenAI Chat Completions API by default. Swap `provider` in
config/deck.toml to hit an OpenAI-compatible endpoint (Ollama, vLLM,
LiteLLM proxy) — the request shape is identical.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx

from ..config.loader import DeckConfig

log = logging.getLogger(__name__)


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, config: DeckConfig) -> None:
        self.config = config
        self._base_url = "https://api.openai.com/v1"
        self._api_key = _read_api_key()

    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        payload = {
            "model": self.config.model_id,
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        last_exc: Exception | None = None
        for attempt in range(1, self.config.retry_attempts + 1):
            try:
                with httpx.Client(timeout=self.config.request_timeout_s) as client:
                    r = client.post(f"{self._base_url}/chat/completions", json=payload, headers=headers)
                    r.raise_for_status()
                    body = r.json()
                content = body["choices"][0]["message"]["content"]
                return json.loads(content)
            except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
                last_exc = exc
                backoff = 2 ** attempt * 0.4
                log.warning("LLM attempt %d/%d failed (%s); retrying in %.1fs",
                            attempt, self.config.retry_attempts, exc, backoff)
                time.sleep(backoff)
        raise LLMError(f"LLM request failed after {self.config.retry_attempts} attempts: {last_exc}")


def _read_api_key() -> str:
    import os
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("AISLIDES_API_KEY")
    if not key:
        raise LLMError("OPENAI_API_KEY (or AISLIDES_API_KEY) is not set")
    return key