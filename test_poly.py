#!/usr/bin/env python3
"""Test Polymarket API"""

import asyncio
from markets.polymarket import Polymarket

async def test():
    p = Polymarket()
    markets = await p.fetch_markets()
    print(f"Polymarket: {len(markets)} markets")
    for m in markets[:5]:
        title = m.question[:50]
        yes = m.odds.get("Yes", 0)
        print(f"  {title}... Yes: {yes:.1%}")

asyncio.run(test())
