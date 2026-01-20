from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import aiohttp


class Market:
    """Represents a prediction market"""
    def __init__(self, question: str, outcomes: List[str], odds: Dict[str, float],
                 volume_24h: Optional[float] = None, liquidity: Optional[float] = None):
        self.question = question
        self.outcomes = outcomes
        self.odds = odds  # outcome -> odds/probability
        self.volume_24h = volume_24h
        self.liquidity = liquidity


class MarketPlatform(ABC):
    """Base class for prediction market platforms"""

    def __init__(self, name: str, chain: str):
        self.name = name
        self.chain = chain
        self._session: Optional[aiohttp.ClientSession] = None

    def set_session(self, session: aiohttp.ClientSession):
        """Set a shared session for this platform"""
        self._session = session

    @abstractmethod
    async def fetch_markets(self) -> List[Market]:
        """Fetch available markets from the platform"""
        pass

    @abstractmethod
    def get_platform_info(self) -> Dict:
        """Get platform metadata"""
        pass
