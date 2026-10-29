"""LLM client wrapper with graceful fallback when no API key is configured."""

from __future__ import annotations

from typing import Any, Optional

from src.config import get_settings
from src.utils import setup_logging

logger = setup_logging("llm")


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None
        if self.settings.openai_configured:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.settings.openai_api_key)
            except Exception as e:  # pragma: no cover
                logger.warning("Failed to init OpenAI client: %s", e)
                self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def complete(self, prompt: str, system: str = "", max_tokens: Optional[int] = None) -> str:
        if not self._client:
            return ""
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = self._client.chat.completions.create(
                model=self.settings.llm_model,
                messages=messages,
                max_tokens=max_tokens or self.settings.max_tokens,
                temperature=self.settings.temperature,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            logger.warning("LLM call failed: %s", e)
            return ""

    def embed(self, texts: list[str]) -> list[list[float]]:
        # Use OpenAI embeddings if available
        if self._client and self.settings.openai_configured:
            try:
                resp = self._client.embeddings.create(model=self.settings.embedding_model, input=texts)
                return [d.embedding for d in resp.data]
            except Exception as e:
                logger.warning("Embedding call failed: %s", e)
        # Fallback dummy
        from src.bootstrap import dummy_embedding
        return [dummy_embedding(t) for t in texts]
