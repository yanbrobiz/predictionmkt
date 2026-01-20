import aiohttp
import logging
from typing import List, Dict
from .base import MarketPlatform, Market

logger = logging.getLogger(__name__)


class DriftBET(MarketPlatform):
    """Drift BET integration (Solana) - Prediction Markets on Drift Protocol"""

    BASE_URL = "https://data.api.drift.trade"

    def __init__(self):
        super().__init__("Drift BET", "Solana")

    def _format_question(self, ticker_id: str) -> str:
        """
        Convert ticker ID to a more readable question format.
        e.g., "TRUMP-WIN-2024-BET" -> "Will TRUMP WIN 2024?"
        """
        # Remove -BET suffix
        market_name = ticker_id.replace('-BET', '')

        # Replace hyphens with spaces and format as question
        parts = market_name.split('-')

        # Try to create a more natural question
        if len(parts) >= 2:
            # Common patterns: "TRUMP-WIN-2024", "BTC-100K-2024"
            subject = parts[0]
            action = ' '.join(parts[1:])
            return f"Will {subject} {action}?"

        return f"{market_name}?"

    async def fetch_markets(self) -> List[Market]:
        """Fetch prediction markets from Drift Data API"""
        from utils import fetch_with_retry

        markets = []

        try:
            url = f"{self.BASE_URL}/contracts"

            # Use shared session if available, otherwise create new one
            if self._session:
                data = await fetch_with_retry(self._session, url)
                if data:
                    markets = self._parse_markets(data)
            else:
                async with aiohttp.ClientSession() as session:
                    data = await fetch_with_retry(session, url)
                    if data:
                        markets = self._parse_markets(data)

        except Exception as e:
            print(f"Error fetching Drift BET markets: {e}")

        return markets

    def _parse_markets(self, data: Dict) -> List[Market]:
        """Parse market data from API response"""
        markets = []

        # Filter only prediction markets (ticker ends with -BET)
        for contract in data.get('contracts', []):
            try:
                ticker_id = contract.get('ticker_id', '')

                # Only include BET markets (prediction markets)
                if not ticker_id.endswith('-BET'):
                    continue

                # Format question for better matching with other platforms
                question = self._format_question(ticker_id)

                # Prediction markets have prices between 0 and 1
                last_price = float(contract.get('last_price', 0))

                # Outcomes are Yes/No
                outcomes = ['Yes', 'No']

                # last_price is the Yes probability (0-1)
                # Ensure price is in valid range for prediction markets
                if last_price > 1:
                    last_price = last_price / 100  # Handle percentage format

                # Validate odds
                if not (0 < last_price < 1):
                    logger.debug(f"Drift BET: Invalid price for '{ticker_id}': {last_price}")
                    continue

                odds = {
                    'Yes': last_price,
                    'No': 1 - last_price
                }

                # Quote volume is in USD
                volume_24h = float(contract.get('quote_volume', 0))

                # Open interest as proxy for liquidity
                liquidity = float(contract.get('open_interest', 0))

                market = Market(
                    question=question,
                    outcomes=outcomes,
                    odds=odds,
                    volume_24h=volume_24h,
                    liquidity=liquidity
                )
                markets.append(market)

            except (KeyError, ValueError, TypeError) as e:
                logger.debug(f"Drift BET: Error parsing contract: {e}")
                continue

        return markets

    def get_platform_info(self) -> Dict:
        return {
            'name': self.name,
            'chain': self.chain,
            'description': '高頻交易、低延遲、支持多種資產'
        }
