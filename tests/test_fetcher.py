import asyncio
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from goldsense.fetcher import NewsFetcher
from goldsense.config import Settings
from goldsense.models import NewsArticle


def test_parse_article():
    """Test article parsing logic"""
    raw_item = {
        "title": "Gold prices rise amid Fed uncertainty",
        "description": "Gold futures climbed as investors await Fed decision",
        "publishedAt": "2024-01-15T10:30:00Z",
        "source": {"name": "Reuters"},
        "url": "https://example.com/news"
    }
    
    article = NewsFetcher._parse_article(raw_item)
    
    assert article.title == "Gold prices rise amid Fed uncertainty"
    assert article.description == "Gold futures climbed as investors await Fed decision"
    assert article.source == "Reuters"
    assert article.url == "https://example.com/news"
    assert isinstance(article.published_at, datetime)


def test_parse_article_missing_fields():
    """Test parsing with missing fields"""
    raw_item = {"title": "Test", "publishedAt": None}
    
    article = NewsFetcher._parse_article(raw_item)
    
    assert article.title == "Test"
    assert article.description == ""
    assert article.source is None
    assert isinstance(article.published_at, datetime)


@pytest.mark.asyncio
async def test_fetch_latest_success():
    """Test successful news fetching"""
    settings = Settings(
        newsapi_key="test_key",
        newsapi_base="https://newsapi.org/v2/everything",
        query="gold",
        lookback_days=2,
        cerebras_api_key="test",
        cerebras_api_base="test",
        cerebras_model="test",
        analysis_temperature=0.2,
        max_concurrency=5,
        truncgil_url="test",
        truncgil_gold_symbol="GRA",
        use_yfinance_fallback=False
    )
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "articles": [
            {
                "title": "Gold hits new high",
                "description": "Gold prices surge",
                "publishedAt": "2024-01-15T10:00:00Z",
                "source": {"name": "Bloomberg"},
                "url": "https://example.com"
            }
        ]
    }
    
    fetcher = NewsFetcher(settings)
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        articles = await fetcher.fetch_latest()
        
        assert len(articles) == 1
        assert articles[0].title == "Gold hits new high"
        assert articles[0].source == "Bloomberg"


if __name__ == "__main__":
    # Run basic test
    test_parse_article()
    test_parse_article_missing_fields()
    print("✅ Fetcher tests passed!")