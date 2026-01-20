import aiohttp
import asyncio
import logging
from typing import List, Dict, Optional
from .base import MarketPlatform, Market
import os

logger = logging.getLogger(__name__)


class OpinionLabs(MarketPlatform):
    """Opinion Labs integration (Multi-chain)"""

    BASE_URL = "https://openapi.opinion.trade"

    def __init__(self, api_key: str = None):
        super().__init__("Opinion Labs", "Multi-chain")
        self.api_key = api_key or os.getenv('OPINION_LABS_API_KEY', '')

    async def _fetch_market_detail(self, session: aiohttp.ClientSession, market_id: str) -> Optional[Dict]:
        """Fetch detailed market info including odds"""
        from utils import fetch_with_retry

        try:
            url = f"{self.BASE_URL}/openapi/market/{market_id}"
            headers = {'apikey': self.api_key}

            data = await fetch_with_retry(session, url, headers=headers, timeout=10, max_retries=2)
            if data and data.get('code') == 0:
                return data.get('result', {})
        except Exception as e:
            logger.debug(f"Opinion Labs: Failed to fetch detail for market {market_id}: {e}")
        return None

    async def fetch_markets(self) -> List[Market]:
        """Fetch markets from Opinion Labs API"""
        from utils import fetch_with_retry

        markets = []

        # Skip if no API key provided
        if not self.api_key:
            print(f"Opinion Labs: No API key provided, skipping...")
            return markets

        try:
            url = f"{self.BASE_URL}/openapi/market"
            headers = {'apikey': self.api_key}
            params = {
                'page': 1,
                'limit': 20,
                'marketType': 0,  # 0 = Binary markets
                'status': 'activated',
                'sortBy': 3  # Sort by volume descending
            }

            # Use shared session if available, otherwise create new one
            if self._session:
                data = await fetch_with_retry(self._session, url, headers=headers, params=params, timeout=10)
                if data:
                    markets = await self._parse_markets(self._session, data)
            else:
                async with aiohttp.ClientSession() as session:
                    data = await fetch_with_retry(session, url, headers=headers, params=params, timeout=10)
                    if data:
                        markets = await self._parse_markets(session, data)

        except Exception as e:
            print(f"Error fetching Opinion Labs markets: {e}")

        return markets

    async def _parse_markets(self, session: aiohttp.ClientSession, data: Dict) -> List[Market]:
        """Parse market data from API response"""
        markets = []

        if data.get('code') != 0:
            print(f"Opinion Labs API error: {data.get('msg', 'Unknown error')}")
            return markets

        result = data.get('result', {})
        market_list = result.get('list', [])

        # Fetch detailed odds for each market concurrently
        market_ids = [m.get('marketId') for m in market_list if m.get('marketId')]
        detail_tasks = [self._fetch_market_detail(session, mid) for mid in market_ids]
        details = await asyncio.gather(*detail_tasks)

        # Create market_id -> detail mapping
        detail_map = {}
        for mid, detail in zip(market_ids, details):
            if detail:
                detail_map[mid] = detail

        for market_data in market_list:
            try:
                market_id = market_data.get('marketId')
                question = market_data.get('marketTitle', '')
                if not question:
                    continue

                # Binary markets have Yes/No outcomes
                outcomes = ['Yes', 'No']

                # Get odds from detailed market info
                detail = detail_map.get(market_id, {})
                yes_price = detail.get('yesPrice')
                no_price = detail.get('noPrice')

                if yes_price is not None and no_price is not None:
                    # Prices might be in percentage (0-100) or decimal (0-1)
                    yes_prob = float(yes_price)
                    no_prob = float(no_price)

                    # Normalize to 0-1 range
                    if yes_prob > 1 or no_prob > 1:
                        yes_prob = yes_prob / 100.0
                        no_prob = no_prob / 100.0

                    odds = {
                        'Yes': max(0.0, min(1.0, yes_prob)),
                        'No': max(0.0, min(1.0, no_prob))
                    }
                else:
                    # Skip markets without valid odds
                    logger.debug(f"Opinion Labs: Skipping market '{question}' - no valid odds")
                    continue

                volume_24h = float(market_data.get('volume24h', 0))

                market = Market(
                    question=question,
                    outcomes=outcomes,
                    odds=odds,
                    volume_24h=volume_24h
                )
                markets.append(market)

            except (KeyError, ValueError, TypeError) as e:
                logger.debug(f"Opinion Labs: Error parsing market: {e}")
                continue

        return markets

    def get_platform_info(self) -> Dict:
        return {
            'name': self.name,
            'chain': self.chain,
            'description': '專注宏觀經濟與金融數據'
        }
