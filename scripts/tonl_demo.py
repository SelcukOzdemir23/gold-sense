# Genel TONL test scripti
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from goldsense.tonl import encode_tonl, decode_tonl, encode_news_articles, decode_news_articles, calculate_token_savings


def test_general_tonl():
    """Test general TONL functionality with various JSON structures."""
    
    print("=== GENEL TONL TESTLERİ ===")
    
    # Test 1: Simple object
    print("\n1. Simple Object:")
    simple_obj = {"name": "Alice", "age": 30, "active": True}
    tonl = encode_tonl(simple_obj)
    decoded = decode_tonl(tonl)
    print(f"Original: {simple_obj}")
    print(f"TONL: {tonl}")
    print(f"Decoded: {decoded}")
    print(f"Round-trip OK: {simple_obj == decoded}")
    
    # Test 2: Array of objects
    print("\n2. Array of Objects:")
    array_obj = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    }
    tonl = encode_tonl(array_obj)
    decoded = decode_tonl(tonl)
    print(f"Original: {array_obj}")
    print(f"TONL: {tonl}")
    print(f"Decoded: {decoded}")
    print(f"Round-trip OK: {array_obj == decoded}")
    
    # Test 3: Primitive array
    print("\n3. Primitive Array:")
    prim_array = {"numbers": [1, 2, 3, 4, 5], "tags": ["urgent", "important"]}
    tonl = encode_tonl(prim_array)
    decoded = decode_tonl(tonl)
    print(f"Original: {prim_array}")
    print(f"TONL: {tonl}")
    print(f"Decoded: {decoded}")
    print(f"Round-trip OK: {prim_array == decoded}")
    
    # Test 4: Nested objects
    print("\n4. Nested Objects:")
    nested = {
        "user": {
            "profile": {
                "name": "Alice",
                "age": 30
            },
            "settings": {
                "theme": "dark"
            }
        }
    }
    tonl = encode_tonl(nested)
    decoded = decode_tonl(tonl)
    print(f"Original: {nested}")
    print(f"TONL: {tonl}")
    print(f"Decoded: {decoded}")
    print(f"Round-trip OK: {nested == decoded}")
    
    # Test 5: Token savings calculation
    print("\n5. Token Savings:")
    test_data = {
        "articles": [
            {"title": "Gold prices rise", "price": 1850.50},
            {"title": "Silver market update", "price": 24.75}
        ]
    }
    savings = calculate_token_savings(test_data)
    print(f"JSON chars: {savings.json_chars}")
    print(f"TONL chars: {savings.tonl_chars}")
    print(f"Savings: {savings.savings_percent:.1f}%")


def test_news_compatibility():
    """Test backward compatibility with news-specific functions."""
    
    print("\n=== HABER UYUMLULUĞU TESTİ ===")
    
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

    print("INPUT JSON:")
    print(json.dumps(sample, ensure_ascii=False, indent=2))

    tonl_text = encode_news_articles(sample)
    print("\nTONL OUTPUT:")
    print(tonl_text)

    decoded = decode_news_articles(tonl_text)
    print("\nDECODED BACK:")
    print(json.dumps(decoded, ensure_ascii=False, indent=2))

    ok = len(decoded) == len(sample) and all(
        decoded[i]["title"] == sample[i]["title"] for i in range(len(sample))
    )
    print(f"\nROUNDTRIP OK: {ok}")


def main() -> None:
    test_general_tonl()
    test_news_compatibility()
    
    # Save test files
    logs_dir = ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    test_data = {"message": "TONL test completed", "success": True}
    tonl_result = encode_tonl(test_data)
    
    (logs_dir / "test_general.tonl").write_text(tonl_result, encoding="utf-8")
    print(f"\n✅ Test files saved to {logs_dir}")


if __name__ == "__main__":
    main()