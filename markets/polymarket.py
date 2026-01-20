import aiohttp
import json
import logging
from typing import List, Dict
from .base import MarketPlatform, Market

logger = logging.getLogger(__name__)


class Polymarket(MarketPlatform):
    """Polymarket integration (Polygon)"""

    BASE_URL = "https://gamma-api.polymarket.com"

    def __init__(self):
        super().__init__("Polymarket", "Polygon")

    async def fetch_markets(self) -> List[Market]:
        """Fetch markets from Polymarket API"""
        from utils import fetch_with_retry

        markets = []

        try:
            # Use shared session if available, otherwise create new one
            if self._session:
                data = await fetch_with_retry(
                    self._session,
                    f"{self.BASE_URL}/markets",
                    params={
                        'closed': 'false',
                        'limit': 50,
                        '_sort': 'volume24hr:desc'
                    }
                )
                if data:
                    markets = self._parse_markets(data)
            else:
                async with aiohttp.ClientSession() as session:
                    data = await fetch_with_retry(
                        session,
                        f"{self.BASE_URL}/markets",
                        params={
                            'closed': 'false',
                            'limit': 50,
                            '_sort': 'volume24hr:desc'
                        }
                    )
                    if data:
                        markets = self._parse_markets(data)

        except Exception as e:
            print(f"Error fetching Polymarket markets: {e}")

        return markets

    def _parse_markets(self, data: List[Dict]) -> List[Market]:
        """Parse market data from API response"""
        markets = []

        for market_data in data:
            try:
                question = market_data.get('question', '')
                if not question:
                    continue

                # outcomes and outcomePrices are JSON strings, need to parse
                outcomes_raw = market_data.get('outcomes', '[]')
                prices_raw = market_data.get('outcomePrices', '[]')

                # Parse JSON strings
                if isinstance(outcomes_raw, str):
                    outcomes = json.loads(outcomes_raw)
                else:
                    outcomes = outcomes_raw

                if isinstance(prices_raw, str):
                    outcome_prices = json.loads(prices_raw)
                else:
                    outcome_prices = prices_raw

                # Get odds from outcome prices
                odds = {}
                for i, outcome in enumerate(outcomes):
                    if i < len(outcome_prices):
                        # Polymarket prices are already probabilities (0-1)
                        price = float(outcome_prices[i])
                        # Validate odds
                        if 0 <= price <= 1:
                            odds[outcome] = price

                # Skip if we don't have valid Yes/No odds
                if 'Yes' not in odds or 'No' not in odds:
                    continue

                volume_24h = float(market_data.get('volume24hr', 0))
                liquidity = float(market_data.get('liquidity', 0))

                market = Market(
                    question=question,
                    outcomes=outcomes,
                    odds=odds,
                    volume_24h=volume_24h,
                    liquidity=liquidity
                )
                markets.append(market)

            except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
                logger.debug(f"Polymarket: Error parsing market: {e}")
                continue

        return markets

    def get_platform_info(self) -> Dict:
        return {
            'name': self.name,
            'chain': self.chain,
            'description': '流動性最高、全球知名度最強'
        }
