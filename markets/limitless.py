import aiohttp
import logging
from typing import List, Dict
from .base import MarketPlatform, Market

logger = logging.getLogger(__name__)


class Limitless(MarketPlatform):
    """Limitless integration (Base)"""

    BASE_URL = "https://api.limitless.exchange"

    def __init__(self):
        super().__init__("Limitless", "Base")

    def _normalize_price(self, price) -> float:
        """Normalize price to 0-1 range, handling both percentage (0-100) and decimal (0-1) formats"""
        price_float = float(price)
        if price_float > 1.0:
            # Assume it's in percentage format (0-100)
            return price_float / 100.0
        return price_float

    async def fetch_markets(self) -> List[Market]:
        """Fetch markets from Limitless API"""
        from utils import fetch_with_retry

        markets = []

        try:
            url = f"{self.BASE_URL}/markets/active"
            params = {
                'page': 1,
                'limit': 25,  # API max limit is 25
                'sortBy': 'high_value'  # Options: ending_soon, high_value, lp_rewards, newest, trending
            }

            # Use shared session if available, otherwise create new one
            if self._session:
                data = await fetch_with_retry(self._session, url, params=params, timeout=10)
                if data:
                    markets = self._parse_markets(data)
            else:
                async with aiohttp.ClientSession() as session:
                    data = await fetch_with_retry(session, url, params=params, timeout=10)
                    if data:
                        markets = self._parse_markets(data)

        except Exception as e:
            print(f"Error fetching Limitless markets: {e}")

        return markets

    def _parse_markets(self, data: Dict) -> List[Market]:
        """Parse market data from API response"""
        markets = []

        for market_data in data.get('data', []):
            try:
                question = market_data.get('title', '')
                if not question:
                    continue

                # Limitless uses binary outcomes (Yes/No)
                outcomes = ['Yes', 'No']

                # Prices array: [yes_probability, no_probability]
                prices_array = market_data.get('prices', [])
                odds = {}

                if len(prices_array) >= 2:
                    # Normalize prices to 0-1 range
                    yes_price = self._normalize_price(float(prices_array[0]))
                    no_price = self._normalize_price(float(prices_array[1]))

                    # Validate odds are in reasonable range
                    if not (0 <= yes_price <= 1) or not (0 <= no_price <= 1):
                        logger.debug(f"Limitless: Invalid odds for '{question}': yes={yes_price}, no={no_price}")
                        continue

                    odds['Yes'] = yes_price
                    odds['No'] = no_price
                else:
                    # Skip markets without valid prices
                    continue

                # Volume might be string or number, convert appropriately
                volume_raw = market_data.get('volume', 0)
                liquidity_raw = market_data.get('liquidity', 0)

                # Handle string or numeric volume (may be in USDC with 6 decimals)
                volume_24h = float(volume_raw) if volume_raw else 0
                liquidity = float(liquidity_raw) if liquidity_raw else 0

                # If values are large (> 1M), assume they're in micro-USDC
                if volume_24h > 1_000_000:
                    volume_24h = volume_24h / 1e6
                if liquidity > 1_000_000:
                    liquidity = liquidity / 1e6

                market = Market(
                    question=question,
                    outcomes=outcomes,
                    odds=odds,
                    volume_24h=volume_24h,
                    liquidity=liquidity
                )
                markets.append(market)

            except (KeyError, ValueError, TypeError) as e:
                logger.debug(f"Limitless: Error parsing market: {e}")
                continue

        return markets

    def get_platform_info(self) -> Dict:
        return {
            'name': self.name,
            'chain': self.chain,
            'description': 'Base 生態龍頭、擅長加密貨幣相關預測'
        }
