from __future__ import annotations

from dataclasses import dataclass
import time

import httpx

from .config import Settings
from .exceptions import ExternalServiceError


@dataclass
class GoldPriceService:
    settings: Settings
    max_retries: int = 2
    base_delay_seconds: float = 0.6

    def get_current_price(self) -> float | None:
        """Get current gold price. Returns None if unavailable instead of raising exception."""
        try:
            return self._fetch_price_from_truncgil()
        except Exception as truncgil_error:
            # Log the error but don't crash
            print(f"⚠️  Truncgil fiyat alınamadı: {truncgil_error}")
            
            # Try Binance as fallback
            if self.settings.use_yfinance_fallback:  # Config name kept for compatibility
                try:
                    return self._fetch_from_binance()
                except Exception as binance_error:
                    print(f"⚠️  Binance fallback da başarısız: {binance_error}")
                    return None
            return None

    def _fetch_from_binance(self) -> float:
        """Fetch gold price from Binance API (PAXGUSDT = Paxos Gold in USDT)."""
        url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
        
        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.get(url, timeout=10)
                if response.status_code != 200:
                    raise ExternalServiceError(
                        f"Binance API yanıt vermedi (HTTP {response.status_code})"
                    )
                
                data = response.json()
                price_str = data.get("price")
                if not price_str:
                    raise ExternalServiceError("Binance price field bulunamadı")
                
                return float(price_str)
            except httpx.ConnectError as exc:
                if attempt < self.max_retries:
                    time.sleep(self.base_delay_seconds * (attempt + 1))
                else:
                    raise ExternalServiceError("Binance sunucusuna bağlanılamadı") from exc
            except httpx.ReadTimeout as exc:
                if attempt < self.max_retries:
                    time.sleep(self.base_delay_seconds * (attempt + 1))
                else:
                    raise ExternalServiceError("Binance zaman aşımı") from exc
            except Exception as exc:
                if attempt < self.max_retries:
                    time.sleep(self.base_delay_seconds * (attempt + 1))
                else:
                    raise ExternalServiceError(f"Binance hatası: {exc}") from exc
        
        raise ExternalServiceError("Binance yanıt vermedi")

    def _fetch_price_from_truncgil(self) -> float:
        url = self.settings.truncgil_url
        symbol = self.settings.truncgil_gold_symbol
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.get(url, timeout=15)
                if response.status_code != 200:
                    raise ExternalServiceError(
                        f"Truncgil API yanıt vermedi (HTTP {response.status_code})"
                    )

                payload = response.json()
                entry = payload.get(symbol)
                if not isinstance(entry, dict):
                    raise ExternalServiceError(f"Truncgil sembol bulunamadı: {symbol}")

                price = entry.get("Selling") or entry.get("Buying")
                if price is None:
                    raise ExternalServiceError(
                        f"Truncgil fiyat bilgisi eksik: {symbol}"
                    )

                return float(price)
            except httpx.ConnectError:
                last_error = ExternalServiceError("Truncgil sunucusuna bağlanılamadı")
                if attempt < self.max_retries:
                    time.sleep(self.base_delay_seconds * (attempt + 1))
            except httpx.ReadTimeout:
                last_error = ExternalServiceError("Truncgil zaman aşımı")
                if attempt < self.max_retries:
                    time.sleep(self.base_delay_seconds * (attempt + 1))
            except Exception as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(self.base_delay_seconds * (attempt + 1))

        raise ExternalServiceError(f"Truncgil yanıt vermedi: {last_error}")


