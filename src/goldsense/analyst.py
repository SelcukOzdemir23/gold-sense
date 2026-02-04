from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Literal

import dspy

from .config import Settings
from .exceptions import ExternalServiceError
from .models import AnalysisResult, Category, NewsArticle


class GoldSignalSignature(dspy.Signature):
    """Analyze a news article for gold market impact. Respond in Turkish."""

    title: str = dspy.InputField(
        desc="The news headline or title to be analyzed"
    )
    description: str = dspy.InputField(
        desc="The news summary or description providing context"
    )

    is_relevant: bool = dspy.OutputField(
        desc="True if the news has material impact on gold markets, False otherwise"
    )
    category: Literal["Macro", "Geopolitical", "Industrial", "Irrelevant"] = dspy.OutputField(
        desc="Primary category: Macro (economy/policy), Geopolitical (conflicts/politics), Industrial (gold industry), or Irrelevant"
    )
    sentiment_score: int = dspy.OutputField(
        desc="Gold market sentiment score from 1 (strongly bearish) to 10 (strongly bullish), must be integer between 1-10"
    )
    impact_reasoning: str = dspy.OutputField(
        desc="A detailed, insightful analysis in TURKISH explaining how this news affects gold markets. Include specific mechanisms (e.g., USD correlation, safe-haven demand, industrial usage, central bank policies). 2-3 sentences maximum, must be in Turkish language with clear financial reasoning."
    )
    confidence_score: float = dspy.OutputField(
        desc="Your confidence in this analysis on a scale of 0.0 (completely uncertain) to 1.0 (completely certain). For clear economic data: 0.9+. For ambiguous geopolitical news: 0.5-0.8. For contradictory signals: <0.5."
    )

    class Config:
        instructions = (
            "You are a senior financial analyst and geopolitics expert analyzing news for gold market impact. "
            "IMPORTANT: Always respond to impact_reasoning field in TURKISH language. "
            "Provide DETAILED, INSIGHTFUL analysis that shows deep understanding of gold market dynamics. "
            "Explain the specific causal mechanisms - don't just state the obvious. "
            "Consider: USD strength/weakness, inflation expectations, central bank actions, geopolitical risk premium, "
            "industrial demand shifts, investor sentiment, technical factors. "
            "Make your reasoning educational and valuable for investors - avoid generic statements. "
            "For each analysis, also objectively rate your confidence (0.0-1.0) in the conclusion. "
            "High confidence (0.9+): Clear, unambiguous economic data or policy decisions. "
            "Medium confidence (0.6-0.8): Multiple supporting signals but some uncertainty. "
            "Low confidence (<0.6): Contradictory signals, speculative interpretations, or weak data."
        )


@dataclass
class GoldAnalyst:
    settings: Settings

    def __post_init__(self) -> None:
        self._configure_lm()
        # Use ChainOfThought instead of Predict for better quality
        self._predict = dspy.ChainOfThought(GoldSignalSignature)

    def _configure_lm(self) -> None:
        try:
            lm = dspy.LM(
                f"openai/{self.settings.cerebras_model}",
                api_key=self.settings.cerebras_api_key,
                api_base=self.settings.cerebras_api_base,
                temperature=self.settings.analysis_temperature,
                cache=False,  # Disable cache to ensure fresh analysis every time
            )
            # Enable usage tracking for token cost analysis
            dspy.configure(lm=lm, track_usage=True)
        except Exception as exc:  # pragma: no cover - defensive
            raise ExternalServiceError(f"Failed to configure DSPy LM: {exc}") from exc

    async def analyze_articles(self, articles: list[NewsArticle]) -> list[AnalysisResult]:
        semaphore = asyncio.Semaphore(self.settings.max_concurrency)

        async def _bound_analyze(article: NewsArticle) -> AnalysisResult:
            async with semaphore:
                return await asyncio.to_thread(self._analyze_one, article)

        tasks = [_bound_analyze(article) for article in articles]
        return await asyncio.gather(*tasks)

    def _analyze_one(self, article: NewsArticle) -> AnalysisResult:
        try:
            result = self._predict(
                title=article.title,
                description=article.description
            )
            
            # DSPy Assertions for validation
            score_value = int(result.sentiment_score) if hasattr(result, 'sentiment_score') else 5
            dspy.Assert(
                1 <= score_value <= 10,
                f"Sentiment score must be between 1 and 10, got {score_value}"
            )
            
            # Confidence validation (0.0 - 1.0)
            confidence_value = float(result.confidence_score) if hasattr(result, 'confidence_score') else 0.5
            dspy.Assert(
                0.0 <= confidence_value <= 1.0,
                f"Confidence score must be between 0.0 and 1.0, got {confidence_value}"
            )
            
            # Check Turkish characters in reasoning (basic validation)
            reasoning_text = str(result.impact_reasoning).strip()
            turkish_chars = set('çğıöşüÇĞİÖŞÜ')
            has_turkish = any(char in reasoning_text for char in turkish_chars) or len(reasoning_text) > 10
            dspy.Suggest(
                has_turkish,
                "impact_reasoning should be in Turkish language"
            )
            
            # Capture ChainOfThought reasoning (the thinking process)
            model_reasoning = getattr(result, 'reasoning', None)
            
        except Exception as exc:
            raise ExternalServiceError(f"Cerebras analysis failed: {exc}") from exc

        category = self._normalize_category(result.category)
        is_relevant = self._normalize_bool(result.is_relevant) and category != "Irrelevant"

        sentiment_score = self._clamp_score(result.sentiment_score)
        confidence_score = self._clamp_confidence(confidence_value)

        return AnalysisResult(
            article=article,
            is_relevant=is_relevant,
            category=category,
            sentiment_score=sentiment_score,
            impact_reasoning=reasoning_text,
            reasoning=model_reasoning,  # ChainOfThought's internal reasoning
            confidence_score=confidence_score,  # Model's confidence in this analysis
        )

    @staticmethod
    def _clamp_score(score: int) -> int:
        try:
            value = int(score)
        except (TypeError, ValueError):
            return 5
        return max(1, min(10, value))

    @staticmethod
    def _clamp_confidence(confidence: float) -> float:
        try:
            value = float(confidence)
        except (TypeError, ValueError):
            return 0.5
        return max(0.0, min(1.0, value))

    @staticmethod
    def _normalize_category(raw_category: str) -> Category:
        if not isinstance(raw_category, str):
            return "Irrelevant"
        normalized = raw_category.strip().lower()
        mapping = {
            "macro": "Macro",
            "makro": "Macro",
            "geopolitical": "Geopolitical",
            "jeopolitik": "Geopolitical",
            "industrial": "Industrial",
            "endüstriyel": "Industrial",
            "irrelevant": "Irrelevant",
            "alakasız": "Irrelevant",
        }
        return mapping.get(normalized, "Irrelevant")

    @staticmethod
    def _normalize_bool(raw_value: object) -> bool:
        if isinstance(raw_value, bool):
            return raw_value
        if isinstance(raw_value, str):
            value = raw_value.strip().lower()
            return value in {"evet", "true", "yes", "1"}
        if isinstance(raw_value, (int, float)):
            return bool(raw_value)
        return False
