"""Template-based explanation — the app's default explainability, no LLM needed."""
from __future__ import annotations

from app.providers.base import DataProvider, NormalizedResult, SourceStatus, now_iso


class TemplateExplanationProvider(DataProvider):
    name = "template_explanation"

    def is_configured(self) -> bool:
        return True

    def fetch(self, *, computed_result: dict, question: str | None = None, **_params) -> dict:
        # Every algorithm result in this app already carries an `explanation`
        # field (see algorithms/*.py) — this provider just surfaces it.
        return {"explanation": computed_result.get("explanation", "No explanation available for this result.")}

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        return NormalizedResult(
            data=raw,
            source_status=SourceStatus.DERIVED,
            source_name="Template explanation (algorithm-generated)",
            retrieved_at=now_iso(),
        )
