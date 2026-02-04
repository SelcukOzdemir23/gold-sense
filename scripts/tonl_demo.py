from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from goldsense.tonl import decode_news_articles, encode_news_articles


def main() -> None:
    sample = [
        {
            "title": "Gold, silver prices continue to slide",
            "description": "Gold fell 2.5%, silver 3%",
            "publishedAt": "2026-02-02T15:36:16Z",
            "source": {"name": "CBC News"},
            "url": "https://example.com/a",
        },
        {
            "title": "Item, with comma",
            "description": "He said \"buy\" now",
            "publishedAt": "2026-02-02T14:00:00Z",
            "source": {"name": "Test, Source"},
            "url": "https://example.com/b",
        },
    ]

    print("=== INPUT JSON ===")
    print(json.dumps(sample, ensure_ascii=False, indent=2))

    tonl_text = encode_news_articles(sample)
    print("\n=== TONL OUTPUT ===")
    print(tonl_text)

    logs_dir = ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    (logs_dir / "test_raw_news.json").write_text(
        json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (logs_dir / "test_news.tonl").write_text(tonl_text, encoding="utf-8")

    decoded = decode_news_articles(tonl_text)
    print("\n=== DECODED BACK ===")
    print(json.dumps(decoded, ensure_ascii=False, indent=2))

    ok = len(decoded) == len(sample) and all(
        decoded[i]["title"] == sample[i]["title"] for i in range(len(sample))
    )
    print(f"\nROUNDTRIP OK: {ok}")


if __name__ == "__main__":
    main()
