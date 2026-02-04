from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from dotenv import load_dotenv

from goldsense.config import Settings
from goldsense.fetcher import NewsFetcher
from goldsense.tonl import encode_news_articles


async def _fetch_and_save(limit: int) -> None:
    load_dotenv()
    settings = Settings.from_env()
    settings.validate()

    fetcher = NewsFetcher(settings)
    articles, payload = await fetcher.fetch_latest_with_payload()

    limited_articles = payload.get("articles", [])[:limit]
    payload_path = ROOT / "logs" / "test_raw_news.json"
    tonl_path = ROOT / "logs" / "test_news.tonl"

    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    tonl_text = encode_news_articles(limited_articles)
    tonl_path.write_text(tonl_text, encoding="utf-8")

    print(f"✅ Raw JSON saved: {payload_path}")
    print(f"✅ TONL saved: {tonl_path}")
    print(f"✅ Articles used: {len(limited_articles)}")


def main() -> None:
    asyncio.run(_fetch_and_save(limit=10))


if __name__ == "__main__":
    main()
