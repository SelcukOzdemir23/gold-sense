
import json
import sys
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir / "src"))

from goldsense.tonl import encode_news_articles

def verify():
    # Load raw json
    raw_path = root_dir / "logs/test_raw_news.json"
    if not raw_path.exists():
        print("No raw logs found.")
        return

    with open(raw_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = data.get("articles", [])
    if not articles:
        print("No articles found in raw json.")
        return

    # Encode with default (remove_url_to_image=True)
    tonl_output = encode_news_articles(articles, remove_url_to_image=True)
    
    print("--- TONL OUTPUT PREVIEW ---")
    print("\n".join(tonl_output.splitlines()[:5]))
    print("---------------------------")

    # Check for urlToImage
    if "urlToImage" not in tonl_output:
        print("SUCCESS: 'urlToImage' was correctly removed.")
    else:
        print("FAILURE: 'urlToImage' is still present in the output.")

    # Convert back to check if we lost it? No, we can't convert back if we removed it.
    # But let's check structure.
    if "news[" in tonl_output:
         print("SUCCESS: Root key is 'news' as expected.")
    else:
         print("FAILURE: Root key is NOT 'news'.")

if __name__ == "__main__":
    verify()
