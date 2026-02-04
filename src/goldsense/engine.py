from __future__ import annotations

from dataclasses import dataclass

from .models import AnalysisResult, MarketSummary


@dataclass
class MarketEngine:
    bullish_threshold: float = 7.0
    bearish_threshold: float = 4.0

    def summarize(self, results: list[AnalysisResult]) -> MarketSummary:
        total = len(results)
        relevant = [r for r in results if r.is_relevant and r.category != "Irrelevant"]
        relevant_count = len(relevant)

        average_score = (
            sum(r.sentiment_score for r in relevant) / relevant_count
            if relevant_count
            else 0.0
        )

        if average_score > self.bullish_threshold:
            trend = "Strong Bullish"
        elif average_score < self.bearish_threshold and relevant_count > 0:
            trend = "Bearish"
        else:
            trend = "Neutral"

        return MarketSummary(
            average_score=average_score,
            trend=trend,
            total_articles=total,
            relevant_articles=relevant_count,
        )
