#!/usr/bin/env python3
"""Test script to find sports/NBA markets across platforms"""

import asyncio
import sys
import io

# Set stdout to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from markets.kalshi import Kalshi
from markets.polymarket import Polymarket

async def test_sports():
    print("Searching for sports markets...")
    print("=" * 60)
    
    # Test Kalshi
    print("\n[Kalshi - All markets sample]")
    kalshi = Kalshi()
    markets = await kalshi.fetch_markets()
    print(f"Total markets: {len(markets)}")
    
    # Show first 10 markets
    print("\nFirst 10 markets:")
    for i, m in enumerate(markets[:10], 1):
        # Clean title for display
        title = m.question.encode('ascii', 'replace').decode('ascii')[:70]
        yes = m.odds.get("Yes", 0)
        no = m.odds.get("No", 0)
        vol = m.volume_24h
        print(f"\n{i}. {title}")
        print(f"   Yes: {yes:.1%}, No: {no:.1%}, Volume: ${vol:,.0f}")
    
    # Search for sports keywords
    sports_keywords = ["GAME", "BOWL", "SPREAD", "POINTS", "WIN", "CHAMPIONSHIP"]
    sports_markets = [m for m in markets if any(kw in m.question.upper() for kw in sports_keywords)]
    
    print(f"\n\nFound {len(sports_markets)} sports-related markets")
    if sports_markets:
        print("\nSports markets sample:")
        for i, m in enumerate(sports_markets[:5], 1):
            title = m.question.encode('ascii', 'replace').decode('ascii')[:70]
            yes = m.odds.get("Yes", 0)
            print(f"\n{i}. {title}")
            print(f"   Yes: {yes:.1%}")
    
    # Test Polymarket
    print("\n" + "=" * 60)
    print("[Polymarket]")
    poly = Polymarket()
    markets = await poly.fetch_markets()
    print(f"Total markets: {len(markets)}")
    
    sports_markets = [m for m in markets if any(kw in m.question.upper() for kw in sports_keywords)]
    print(f"Sports-related: {len(sports_markets)}")
    
    for i, m in enumerate(sports_markets[:5], 1):
        title = m.question.encode('ascii', 'replace').decode('ascii')[:70]
        print(f"\n{i}. {title}")
        for outcome, odds in list(m.odds.items())[:2]:
            print(f"   {outcome}: {odds:.1%}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_sports())
