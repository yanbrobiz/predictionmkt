import aiohttp
import logging
from typing import List, Dict
from .base import MarketPlatform, Market

logger = logging.getLogger(__name__)


class Kalshi(MarketPlatform):
    """Kalshi integration - CFTC-regulated prediction market"""

    BASE_URL = "https://api.elections.kalshi.com"

    def __init__(self):
        super().__init__("Kalshi", "Centralized (US)")

    async def fetch_markets(self) -> List[Market]:
        """Fetch markets from Kalshi public API"""
        from utils import fetch_with_retry

        markets = []

        try:
            url = f"{self.BASE_URL}/trade-api/v2/markets"
            params = {
                'status': 'open',
                'limit': 100
            }

            # Use shared session if available, otherwise create new one
            if self._session:
                data = await fetch_with_retry(self._session, url, params=params)
                if data:
                    markets = self._parse_markets(data)
            else:
                async with aiohttp.ClientSession() as session:
                    data = await fetch_with_retry(session, url, params=params)
                    if data:
                        markets = self._parse_markets(data)

        except Exception as e:
            print(f"Error fetching Kalshi markets: {e}")

        return markets

    def _parse_markets(self, data: Dict) -> List[Market]:
        """Parse market data from API response"""
        markets = []

        for market_data in data.get('markets', []):
            try:
                # Get market title as question
                question = market_data.get('title', '')
                if not question:
                    continue

                # Binary outcomes
                outcomes = ['Yes', 'No']

                # Kalshi uses cents (0-100), convert to probability (0-1)
                # For arbitrage, use ask prices (the price to BUY)
                # yes_ask = price to buy Yes, no_ask = price to buy No
                yes_ask = market_data.get('yes_ask')
                no_ask = market_data.get('no_ask')

                # Fallback to bid prices if ask not available
                if yes_ask is None:
                    yes_ask = market_data.get('yes_bid', 0)
                if no_ask is None:
                    no_ask = market_data.get('no_bid', 0)

                # Convert from cents to probability (0-1)
                yes_prob = float(yes_ask) / 100.0
                no_prob = float(no_ask) / 100.0

                # Validate odds are in reasonable range
                if not (0 <= yes_prob <= 1) or not (0 <= no_prob <= 1):
                    logger.debug(f"Kalshi: Invalid odds for '{question}': yes={yes_prob}, no={no_prob}")
                    continue

                odds = {
                    'Yes': yes_prob,
                    'No': no_prob
                }

                # Volume and liquidity
                volume_24h = float(market_data.get('volume_24h', 0))
                liquidity = float(market_data.get('liquidity', 0))

                market = Market(
                    question=question,
                    outcomes=outcomes,
                    odds=odds,
                    volume_24h=volume_24h,
                    liquidity=liquidity
                )
                markets.append(market)

            except (KeyError, ValueError, TypeError) as e:
                logger.debug(f"Kalshi: Error parsing market: {e}")
                continue

        return markets

    def get_platform_info(self) -> Dict:
        return {
            'name': self.name,
            'chain': self.chain,
            'description': 'CFTC 監管的美國預測市場，涵蓋經濟、政治、體育等'
        }
