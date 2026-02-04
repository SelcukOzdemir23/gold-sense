from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from .analyst import GoldAnalyst
from .engine import MarketEngine
from .exceptions import GoldSenseError
from .fetcher import NewsFetcher
from .logger import JsonlLogger
from .models import AnalysisResult, MarketSummary
from .price import GoldPriceService


@dataclass
class AnalysisPipeline:
    fetcher: NewsFetcher
    analyst: GoldAnalyst
    engine: MarketEngine
    price_service: GoldPriceService
    logger: JsonlLogger | None = None

    async def run(self) -> tuple[float, MarketSummary, list[AnalysisResult]]:
        articles = await self.fetcher.fetch_latest()
        results = await self.analyst.analyze_articles(articles)

        if self.logger:
            for result in results:
                self.logger.log(result)

        summary = self.engine.summarize(results)
        price = self.price_service.get_current_price()

        return price, summary, results


def run_pipeline_sync(pipeline: AnalysisPipeline) -> tuple[float, MarketSummary, list[AnalysisResult]]:
    try:
        return asyncio.run(pipeline.run())
    except GoldSenseError:
        raise
    except Exception as exc:  # pragma: no cover
        raise GoldSenseError(f"Pipeline failed: {exc}") from exc
