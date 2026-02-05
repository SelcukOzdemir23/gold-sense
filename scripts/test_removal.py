
import sys
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir / "src"))

from goldsense.tonl import encode_news_articles

def test_removal():
    articles = [
        {
            "source": {"name": "Test"},
            "title": "A Title",
            "urlToImage": "http://image.com/fake.jpg",
            "other": "value"
        }
    ]
    
    # helper to check if string exists in output
    out_default = encode_news_articles(articles)
    out_keep = encode_news_articles(articles, remove_url_to_image=False)
    
    print(f"Default Output:\n{out_default}")
    print("-" * 20)
    print(f"Keep Output:\n{out_keep}")
    print("-" * 20)
    
    if "http://image.com/fake.jpg" not in out_default:
        print("PASS: urlToImage removed by default.")
    else:
        print("FAIL: urlToImage present in default.")
        
    if "http://image.com/fake.jpg" in out_keep:
        print("PASS: urlToImage kept when requested.")
    else:
        print("FAIL: urlToImage missing when requested.")

if __name__ == "__main__":
    test_removal()
