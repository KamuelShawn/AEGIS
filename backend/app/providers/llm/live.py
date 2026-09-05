"""
Gemini — explanation layer only. Called with an already-computed algorithm
result (a dict of numbers/labels); the prompt explicitly forbids inventing
new figures. If this call fails or is unconfigured, callers fall back to
`app.providers.llm.mock.TemplateExplanationProvider`, which is fully
functional without any LLM at all — the app's explainability never depends
on this provider being present.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

SYSTEM_PREAMBLE = (
    "You are explaining a result that has ALREADY been computed by a deterministic "
    "algorithm. Do not invent, adjust, or estimate any numeric value. Only explain, "
    "in 2-3 plain sentences, what the given numbers mean and why, using exactly the "
    "figures provided."
)


class LiveGeminiProvider(DataProvider):
    name = "gemini"

    def is_configured(self) -> bool:
        return bool(settings.GEMINI_API_KEY)

    def fetch(self, *, computed_result: dict, question: str | None = None, **_params) -> dict:
        prompt = f"{SYSTEM_PREAMBLE}\n\nComputed result: {computed_result}\n"
        if question:
            prompt += f"\nUser question: {question}"
        try:
            resp = httpx.post(
                GEMINI_URL,
                params={"key": settings.GEMINI_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=15.0,
            )
        except httpx.RequestError as exc:
            raise ProviderError(f"Gemini network error: {exc}") from exc
        if resp.status_code == 401 or resp.status_code == 403:
            raise ProviderError("Gemini API key rejected")
        if resp.status_code == 429:
            raise ProviderError("Gemini rate limited")
        if resp.status_code >= 500:
            raise ProviderError("Gemini temporarily unavailable")
        if resp.status_code != 200:
            raise ProviderError(f"Gemini returned {resp.status_code}")
        return resp.json()

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "candidates" in raw

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        text = raw["candidates"][0]["content"]["parts"][0]["text"]
        return NormalizedResult(
            data={"explanation": text.strip()},
            source_status=SourceStatus.DERIVED,
            source_name="Gemini (explanation of pre-computed result)",
            retrieved_at=now_iso(),
        )
