from __future__ import annotations

from dataclasses import dataclass

from .fetcher import NewsFetcher
from .price import GoldPriceService


@dataclass
class ServiceCheck:
    fetcher: NewsFetcher
    price_service: GoldPriceService

    async def check_newsapi(self) -> dict:
        articles = await self.fetcher.fetch_latest()
        return {"count": len(articles), "status": "ok"}

    def check_yfinance(self) -> float:
        price = self.price_service.get_current_price()
        if price is None:
            raise Exception("Price service returned None")
        return price