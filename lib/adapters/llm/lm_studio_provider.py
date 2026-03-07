"""
LM Studio implementation of the LLM provider interface.
"""

import re
import httpx
from openai import OpenAI

from lib.domain.llm_provider import LLMProvider
from lib.config import LM_BASE_URL, LM_API_KEY, LM_MODEL, LM_TEMPERATURE, LM_NO_THINK


class LMStudioProvider(LLMProvider):
    """LM Studio local LLM provider using OpenAI-compatible API."""

    def __init__(self):
        self._client: OpenAI | None = None
        self._checked = False

    def chat(self, prompt: str, system_prompt: str | None = None) -> str:
        """Send chat completion to LM Studio."""
        client = self._get_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": f"{LM_NO_THINK}\n{prompt}"})

        response = client.chat.completions.create(
            model=LM_MODEL,
            temperature=LM_TEMPERATURE,
            messages=messages
        )
        
        raw = response.choices[0].message.content or ""
        return self._strip_think(raw)

    def is_available(self) -> bool:
        """Check if LM Studio is running and has a model loaded."""
        try:
            r = httpx.get(f"{LM_BASE_URL}/models", timeout=3)
            models = r.json().get("data", [])
            return len(models) > 0
        except httpx.ConnectError:
            return False

    def _get_client(self) -> OpenAI:
        """Lazily construct and verify the OpenAI client."""
        if self._client is None:
            self._client = OpenAI(base_url=LM_BASE_URL, api_key=LM_API_KEY)

        if not self._checked:
            if not self.is_available():
                raise RuntimeError(
                    "Cannot connect to LM Studio at localhost:1234. "
                    "Open LM Studio → Developer tab → Start Server and load a model."
                )
            self._checked = True

        return self._client

    @staticmethod
    def _strip_think(text: str) -> str:
        """Remove Qwen3 <think>...</think> blocks if they sneak through."""
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
