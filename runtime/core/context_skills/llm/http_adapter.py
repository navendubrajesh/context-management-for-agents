"""Optional HTTP LLM adapter — operator-configured endpoint only."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from context_skills.llm.offline import OfflineLLMProvider
from context_skills.llm.provider import LLMProvider


class HttpLLMProvider(LLMProvider):
    def __init__(self, *, base_url: str, model: str, api_key: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key or os.environ.get("CONTEXT_SKILLS_LLM_API_KEY")

    @property
    def name(self) -> str:
        return f"http:{self.model}"

    def summarize(self, text: str, *, instruction: str, max_tokens: int = 512) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": text},
            ],
            "max_tokens": max_tokens,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
                body = json.loads(response.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"].strip()
        except (urllib.error.URLError, KeyError, json.JSONDecodeError):
            return OfflineLLMProvider().summarize(text, instruction=instruction, max_tokens=max_tokens)
