from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from goldsense.config import Settings
from goldsense.fetcher import NewsFetcher
from goldsense.healthcheck import ServiceCheck
from goldsense.price import GoldPriceService


def main() -> None:
    load_dotenv()
    settings = Settings.from_env()

    checker = ServiceCheck(
        fetcher=NewsFetcher(settings),
        price_service=GoldPriceService(settings),
    )

    print("NewsAPI kontrol ediliyor...")
    try:
        news_result = asyncio.run(checker.check_newsapi())
        print(f"NewsAPI OK | Haber sayısı: {news_result['count']}")
    except Exception as exc:
        print(f"NewsAPI failed: {exc}")

    print("Altın fiyat kaynağı kontrol ediliyor...")
    try:
        price = checker.check_yfinance()
        print(f"Fiyat OK | {price:.2f}")
    except Exception as exc:
        print(f"Fiyat hatası: {exc}")


if __name__ == "__main__":
    main()
