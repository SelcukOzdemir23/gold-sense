from __future__ import annotations

from dataclasses import dataclass

from .models import AnalysisResult, MarketSummary


@dataclass
class MarketEngine:
    bullish_threshold: float = 7.0
    bearish_threshold: float = 4.0
    
    # Category weights for weighted average calculation
    CATEGORY_WEIGHTS = {
        "Macro": 1.5,          # Highest impact: economy, central banks, policy
        "Geopolitical": 1.2,   # Medium-high: geopolitical risk, safe-haven demand
        "Industrial": 1.0,     # Baseline: industrial demand, mining, jewelry
        "Irrelevant": 0.0,     # No impact on gold markets
    }

    def summarize(self, results: list[AnalysisResult]) -> MarketSummary:
        total = len(results)
        relevant = [r for r in results if r.is_relevant and r.category != "Irrelevant"]
        relevant_count = len(relevant)

        average_score = (
            sum(r.sentiment_score for r in relevant) / relevant_count
            if relevant_count
            else 0.0
        )
        
        # Calculate weighted score: ∑(Score × Weight × Confidence) / ∑(Weight × Confidence)
        weighted_score = self._calculate_weighted_score(relevant)
        
        # Average confidence across all analyses
        confidence_average = (
            sum(r.confidence_score for r in relevant) / relevant_count
            if relevant_count
            else 0.0
        )

        if weighted_score > self.bullish_threshold:
            trend = "Strong Bullish"
        elif weighted_score < self.bearish_threshold and relevant_count > 0:
            trend = "Bearish"
        else:
            trend = "Neutral"

        return MarketSummary(
            average_score=average_score,
            trend=trend,
            total_articles=total,
            relevant_articles=relevant_count,
            weighted_score=weighted_score,
            confidence_average=confidence_average,
        )
    
    def _calculate_weighted_score(self, relevant: list[AnalysisResult]) -> float:
        """
        Calculate weighted average score:
        WeightedScore = ∑(Score × Weight × Confidence) / ∑(Weight × Confidence)
        
        This ensures:
        - Macro news (1.5x) influences trend more than industrial (1.0x)
        - Low-confidence analyses are down-weighted
        """
        if not relevant:
            return 0.0
        
        numerator = 0.0
        denominator = 0.0
        
        for result in relevant:
            weight = self.CATEGORY_WEIGHTS.get(result.category, 0.0)
            confidence = result.confidence_score
            
            numerator += result.sentiment_score * weight * confidence
            denominator += weight * confidence
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator

