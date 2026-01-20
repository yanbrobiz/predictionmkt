import aiohttp
from typing import List, Dict
from .base import MarketPlatform, Market

class Myriad(MarketPlatform):
    """
    Myriad integration (Abstract/EVM)
    
    NOTE: Myriad does not have a documented public REST API.
    It uses SDK/smart contract integration which requires on-chain calls.
    This integration is currently unavailable.
    """

    def __init__(self):
        super().__init__("Myriad", "Abstract/EVM")

    async def fetch_markets(self) -> List[Market]:
        """
        Myriad does not have a public REST API.
        Returns empty list with a warning message.
        """
        print(f"  [N/A] {self.name}: No public REST API available (uses SDK/smart contract integration)")
        return []

    def get_platform_info(self) -> Dict:
        return {
            'name': self.name,
            'chain': self.chain,
            'description': 'AI 驅動、社群文化與遊戲化主題（無公開 API）'
        }
