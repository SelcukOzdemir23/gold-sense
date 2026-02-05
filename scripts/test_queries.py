import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from goldsense.config import Settings
from goldsense.fetcher import NewsFetcher
from dotenv import load_dotenv

async def test_queries():
    load_dotenv()
    
    # Current query
    current_query = "(gold price OR XAU OR central banks OR inflation) AND (Fed OR Geopolitical)"
    
    # Improved queries
    queries = {
        "Current (Restrictive)": current_query,
        "Broader Gold": "gold OR XAU OR \"gold price\" OR \"precious metals\"",
        "Gold + Economics": "(gold OR XAU) AND (price OR market OR Fed OR inflation OR economy)",
        "Comprehensive": "gold OR XAU OR \"gold price\" OR \"precious metals\" OR \"safe haven\" OR \"central bank gold\"",
    }
    
    print("🔍 QUERY COMPARISON TEST")
    print("=" * 50)
    
    for name, query in queries.items():
        print(f"\n📊 {name}:")
        print(f"Query: {query}")
        
        # Create settings with this query
        settings = Settings.from_env()
        settings = Settings(
            newsapi_key=settings.newsapi_key,
            newsapi_base=settings.newsapi_base,
            query=query,
            lookback_days=2,  # Shorter for testing
            cerebras_api_key=settings.cerebras_api_key,
            cerebras_api_base=settings.cerebras_api_base,
            cerebras_model=settings.cerebras_model,
            analysis_temperature=settings.analysis_temperature,
            max_concurrency=settings.max_concurrency,
            truncgil_url=settings.truncgil_url,
            truncgil_gold_symbol=settings.truncgil_gold_symbol,
            use_yfinance_fallback=settings.use_yfinance_fallback,
        )
        
        fetcher = NewsFetcher(settings)
        
        try:
            articles = await fetcher.fetch_latest()
            print(f"✅ Results: {len(articles)} articles")
            
            if articles:
                print("📰 Sample titles:")
                for i, article in enumerate(articles[:3]):
                    print(f"  {i+1}. {article.title}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_queries())