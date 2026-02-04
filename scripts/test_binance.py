#!/usr/bin/env python3
"""Test Binance API directly."""
import httpx

url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
response = httpx.get(url, timeout=10)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

data = response.json()
print(f"\nSymbol: {data['symbol']}")
print(f"Price (string): {data['price']}")
print(f"Price (float): {float(data['price'])}")
