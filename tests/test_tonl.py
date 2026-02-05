from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from goldsense.tonl import decode_news_articles, encode_news_articles


def test_tonl_roundtrip_basic() -> None:
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

    tonl = encode_news_articles(sample)
    back = decode_news_articles(tonl)

    assert len(back) == len(sample)
    assert back[0]["title"] == "Gold, silver prices continue to slide"
    assert back[0]["description"] == "Gold fell 2.5%, silver 3%"
    assert back[0]["published_at"] == "2026-02-02T15:36:16Z"
    assert back[0]["source"] == "CBC News"
    assert back[0]["url"] == "https://example.com/a"

    assert back[1]["title"] == "Item, with comma"
    assert back[1]["description"] == "He said \"buy\" now"
    assert back[1]["published_at"] == "2026-02-02T14:00:00Z"
    assert back[1]["source"] == "Test, Source"
    assert back[1]["url"] == "https://example.com/b"


def test_tonl_handles_empty_fields() -> None:
    sample = [
        {
            "title": "",
            "description": None,
            "publishedAt": "",
            "source": {"name": ""},
            "url": "",
        }
    ]

    tonl = encode_news_articles(sample)
    back = decode_news_articles(tonl)

    assert len(back) == 1
    assert back[0]["title"] == ""
    assert back[0]["description"] is None
    assert back[0]["published_at"] == ""
    assert back[0]["source"] == ""
    assert back[0]["url"] == ""

def test_news_url_removal() -> None:
    articles = [
        {
            "title": "A",
            "urlToImage": "http://img",
            "source": {"name": "S"}
        }
    ]
    
    # Default -> Remove
    tonl_def = encode_news_articles(articles)
    assert "http://img" not in tonl_def
    assert "urlToImage" not in tonl_def
    
    # Explicit False -> Keep
    tonl_keep = encode_news_articles(articles, remove_url_to_image=False)
    assert "http://img" in tonl_keep
    # check that it is encoded correctly
    assert 'urlToImage: "http://img"' in tonl_keep or 'urlToImage' in tonl_keep

