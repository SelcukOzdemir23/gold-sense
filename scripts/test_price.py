#!/usr/bin/env python3
"""Test price service with error handling."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

from goldsense.config import Settings
from goldsense.price import GoldPriceService

load_dotenv()

settings = Settings.from_env()
price_service = GoldPriceService(settings)

print("=" * 60)
print("🧪 GOLD PRICE SERVICE TEST")
print("=" * 60)
print(f"Truncgil URL: {settings.truncgil_url}")
print(f"Binance Fallback: {'✅ Aktif' if settings.use_yfinance_fallback else '❌ Pasif'}")
print("=" * 60)

print("\n🔍 Altın fiyatı sorgulanıyor...")
price = price_service.get_current_price()

print("\n" + "=" * 60)
if price is None:
    print("❌ SONUÇ: Fiyat bilgisi alınamadı")
    print("   (Truncgil ve Binance yanıt vermedi)")
else:
    print(f"✅ SONUÇ: ${price:.2f}")
    print(f"   (1 oz altın = ${price:.2f} USDT)")
print("=" * 60)

