from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import timedelta

from .exceptions import ConfigError


@dataclass(frozen=True)
class Settings:
    newsapi_key: str | None
    newsapi_base: str
    query: str
    lookback_days: int
    cerebras_api_key: str | None
    cerebras_api_base: str | None
    cerebras_model: str | None
    analysis_temperature: float
    max_concurrency: int
    truncgil_url: str
    truncgil_gold_symbol: str
    use_yfinance_fallback: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            newsapi_key=os.getenv("NEWSAPI_KEY"),
            newsapi_base=os.getenv("NEWSAPI_BASE", "https://newsapi.org/v2/everything"),
            query=os.getenv(
                "NEWS_QUERY",
                'gold OR XAU OR "gold price" OR "precious metals" OR ("central bank" AND gold)',
            ),
            lookback_days=int(os.getenv("LOOKBACK_DAYS", "3")),
            cerebras_api_key=os.getenv("CEREBRAS_API_KEY"),
            cerebras_api_base=os.getenv("CEREBRAS_API_BASE"),
            cerebras_model=os.getenv("CEREBRAS_MODEL"),
            analysis_temperature=float(os.getenv("ANALYSIS_TEMPERATURE", "0.2")),
            max_concurrency=int(os.getenv("MAX_CONCURRENCY", "6")),
            truncgil_url=os.getenv(
                "TRUNCGIL_URL", "https://finans.truncgil.com/v4/today.json"
            ),
            truncgil_gold_symbol=os.getenv("TRUNCGIL_GOLD_SYMBOL", "GRA"),
            use_yfinance_fallback=os.getenv("USE_YFINANCE_FALLBACK", "false").lower()
            in {"1", "true", "yes"},
        )

    def validate(self) -> None:
        if not self.newsapi_key:
            raise ConfigError("NEWSAPI_KEY is missing in .env")
        if not self.cerebras_api_key:
            raise ConfigError("CEREBRAS_API_KEY is missing in .env")
        if not self.cerebras_api_base:
            raise ConfigError("CEREBRAS_API_BASE is missing in .env")
        if not self.cerebras_model:
            raise ConfigError("CEREBRAS_MODEL is missing in .env")
        if self.lookback_days <= 0:
            raise ConfigError("LOOKBACK_DAYS must be positive")
        if self.max_concurrency <= 0:
            raise ConfigError("MAX_CONCURRENCY must be positive")
        if not self.truncgil_gold_symbol:
            raise ConfigError("TRUNCGIL_GOLD_SYMBOL must be set")

    @property
    def lookback_delta(self) -> timedelta:
        return timedelta(days=self.lookback_days)
