import pytest
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from goldsense.tonl import encode_news_articles, decode_news_articles
from goldsense.analyst import GoldAnalyst
from goldsense.models import NewsArticle
from goldsense.config import Settings
import dspy

# Load prod env
load_dotenv()

def test_tonl_roundtrip():
    """Test if TONL encoding/decoding preserves data integrity."""
    original = [
        {
            "title": "Test Title",
            "description": "Test Description with \n multiple lines.",
            "source": {"name": "Test Source"},
            "publishedAt": "2024-01-01T00:00:00Z"
        }
    ]
    
    encoded = encode_news_articles(original)
    assert "Test Title" in encoded
    assert '"""' in encoded # Should use triple quotes for multiline
    
    decoded = decode_news_articles(encoded)
    assert len(decoded) == 1
    # Check if multiline description is preserved
    assert "Test Description with \n multiple lines." in decoded[0]["description"]

def test_analyst_configuration():
    """Test if Analyst can be initialized and configured (DSPy logic)."""
    settings = Settings.from_env()
    
    # Configure Global LM (simulating app.py)
    lm = dspy.LM(
        f"openai/{settings.cerebras_model}",
        api_key=settings.cerebras_api_key,
        api_base=settings.cerebras_api_base,
        temperature=0.1
    )
    dspy.configure(lm=lm)
    
    analyst = GoldAnalyst(settings)
    
    # Check if predictor has few-shot examples compiled
    # The _predict object should be a LabeledFewShot instance wrapping ChainOfThought?
    # Actually compile() returns a new module.
    
    # Simple check: does it have demos?
    assert hasattr(analyst._predict, 'demos')
    assert len(analyst._predict.demos) > 0
    print(f"Analyst loaded with {len(analyst._predict.demos)} few-shot examples.")
