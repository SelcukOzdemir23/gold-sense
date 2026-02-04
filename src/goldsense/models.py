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
    reasoning: str | None = None  # DSPy ChainOfThought reasoning - how the model arrived at its conclusion


@dataclass(frozen=True)
class MarketSummary:
    average_score: float
    trend: str
    total_articles: int
    relevant_articles: int
