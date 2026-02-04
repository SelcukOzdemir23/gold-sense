from __future__ import annotations

from dataclasses import dataclass

from .fetcher import NewsFetcher
from .price import GoldPriceService


@dataclass
class ServiceCheck:
    """Lightweight connectivity checks for external services."""

    fetcher: NewsFetcher
    price_service: GoldPriceService

    async def check_newsapi(self) -> dict[str, int]:
        articles = await self.fetcher.fetch_latest()
        return {
            "count": len(articles),
        }

    def check_yfinance(self) -> float:
        return self.price_service.get_current_price()
