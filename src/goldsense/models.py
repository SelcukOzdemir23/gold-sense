from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Category = Literal["Macro", "Geopolitical", "Industrial", "Irrelevant"]


@dataclass(frozen=True)
class NewsArticle:
    title: str
    description: str
    published_at: datetime
    source: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class AnalysisResult:
    article: NewsArticle
    is_relevant: bool
    category: Category
    sentiment_score: int
    impact_reasoning: str
    rationale: str | None = None  # DSPy ChainOfThought reasoning - how the model arrived at its conclusion
    confidence_score: float = 0.5  # Model's confidence (0.0-1.0) in this analysis


@dataclass(frozen=True)
class MarketSummary:
    average_score: float
    trend: str
    total_articles: int
    relevant_articles: int
    weighted_score: float = 0.0  # Weighted by category and confidence
    confidence_average: float = 0.0  # Average confidence across all analyses
