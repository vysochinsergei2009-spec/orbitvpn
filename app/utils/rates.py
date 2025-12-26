from decimal import Decimal
from datetime import datetime, timedelta
import aiohttp

_ton_price_cache = {"price": None, "timestamp": None}
_usdt_price_cache = {"price": None, "timestamp": None}
_PRICE_CACHE_TTL_SECONDS = 60

async def get_ton_price() -> Decimal:
    now = datetime.utcnow()

    if (_ton_price_cache["price"] and
        _ton_price_cache["timestamp"] and
        (now - _ton_price_cache["timestamp"]).total_seconds() < _PRICE_CACHE_TTL_SECONDS):
        return _ton_price_cache["price"]

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "the-open-network", "vs_currencies": "rub"},
            timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            data = await resp.json()
            price = Decimal(str(data["the-open-network"]["rub"]))

            _ton_price_cache["price"] = price
            _ton_price_cache["timestamp"] = now

            return price


async def get_usdt_rub_rate() -> Decimal:
    """Get USDT to RUB exchange rate from CoinGecko API with caching"""
    now = datetime.utcnow()

    if (_usdt_price_cache["price"] and
        _usdt_price_cache["timestamp"] and
        (now - _usdt_price_cache["timestamp"]).total_seconds() < _PRICE_CACHE_TTL_SECONDS):
        return _usdt_price_cache["price"]

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "tether", "vs_currencies": "rub"},
            timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            data = await resp.json()
            price = Decimal(str(data["tether"]["rub"]))

            _usdt_price_cache["price"] = price
            _usdt_price_cache["timestamp"] = now

            return price