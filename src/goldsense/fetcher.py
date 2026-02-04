from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

from .config import Settings
from .exceptions import ExternalServiceError
from .models import NewsArticle


@dataclass
class NewsFetcher:
    settings: Settings

    async def fetch_latest(self) -> list[NewsArticle]:
        articles, _ = await self.fetch_latest_with_payload()
        return articles

    async def fetch_latest_with_payload(self) -> tuple[list[NewsArticle], dict]:
        now = datetime.now(timezone.utc)
        from_date = now - self.settings.lookback_delta

        params = {
            "q": self.settings.query,
            "from": from_date.date().isoformat(),
            "to": now.date().isoformat(),
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 50,
            "apiKey": self.settings.newsapi_key,
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(self.settings.newsapi_base, params=params)

        if response.status_code != 200:
            raise ExternalServiceError(
                f"NewsAPI error: {response.status_code} - {response.text}"
            )

        payload = response.json()
        articles = payload.get("articles", [])
        parsed = [self._parse_article(item) for item in articles]
        return parsed, payload

    @staticmethod
    def _parse_article(item: dict) -> NewsArticle:
        published_raw = item.get("publishedAt")
        published_at = datetime.fromisoformat(
            published_raw.replace("Z", "+00:00")
        ) if published_raw else datetime.now(timezone.utc)

        return NewsArticle(
            title=(item.get("title") or "").strip(),
            description=(item.get("description") or "").strip(),
            published_at=published_at,
            source=(item.get("source") or {}).get("name"),
            url=item.get("url"),
        )
