from __future__ import annotations

from pathlib import Path
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from goldsense.config import Settings
from goldsense.engine import MarketEngine
from goldsense.exceptions import ConfigError, GoldSenseError
from goldsense.fetcher import NewsFetcher
from goldsense.analyst import GoldAnalyst
from goldsense.logger import JsonlLogger
from goldsense.pipeline import AnalysisPipeline, run_pipeline_sync
from goldsense.price import GoldPriceService


def main() -> None:
    load_dotenv()
    settings = Settings.from_env()

    try:
        settings.validate()
    except ConfigError as exc:
        raise SystemExit(f"Config error: {exc}")

    pipeline = AnalysisPipeline(
        fetcher=NewsFetcher(settings),
        analyst=GoldAnalyst(settings),
        engine=MarketEngine(),
        price_service=GoldPriceService(settings),
        logger=JsonlLogger(path=Path("logs/analysis.jsonl")),
    )

    try:
        price, summary, results = run_pipeline_sync(pipeline)
    except GoldSenseError as exc:
        raise SystemExit(f"Run failed: {exc}")

    trend_map = {
        "Strong Bullish": "Güçlü Boğa",
        "Bearish": "Ayı",
        "Neutral": "Nötr",
    }
    trend_tr = trend_map.get(summary.trend, summary.trend)

    print(f"Altın fiyatı: {price:.2f} USD")
    print(f"Eğilim: {trend_tr} (ort. skor: {summary.average_score:.2f})")
    print(
        f"İlgili haber sayısı: {summary.relevant_articles}/{summary.total_articles}"
    )

    category_map = {
        "Macro": "Makro",
        "Geopolitical": "Jeopolitik",
        "Industrial": "Endüstriyel",
        "Irrelevant": "Alakasız",
    }

    for item in results[:5]:
        category_tr = category_map.get(item.category, item.category)
        print(
            f"- {item.article.title} | {category_tr} | "
            f"{item.sentiment_score}/10 | {item.impact_reasoning}"
        )


if __name__ == "__main__":
    main()
