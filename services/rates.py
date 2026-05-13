import aiohttp
from datetime import datetime, timedelta

class RatesService:
    def __init__(self):
        self._cache = {}
        self._updated_at = None

    async def get_rates(self) -> dict:
        if self._is_cache_valid():
            return self._cache
        async with aiohttp.ClientSession() as session:
            url = "https://api.frankfurter.app/latest?base=USD"
            async with session.get(url) as resp:
                data = await resp.json()
                self._cache = data["rates"]
                self._cache["USD"] = 1.0
                self._updated_at = datetime.now()
                return self._cache

    def _is_cache_valid(self):
        if not self._updated_at:
            return False
        return datetime.now() - self._updated_at < timedelta(hours=1)

    async def convert(self, amount: float, from_cur: str, to_cur: str):
        rates = await self.get_rates()
        if from_cur not in rates or to_cur not in rates:
            return None
        in_usd = amount / rates[from_cur]
        return round(in_usd * rates[to_cur], 2)

rates_service = RatesService()