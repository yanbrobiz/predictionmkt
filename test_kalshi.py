#!/usr/bin/env python3
"""Test script to verify Kalshi API integration"""

import asyncio
from markets.kalshi import Kalshi

async def test_kalshi():
    print("=" * 60)
    print("Testing Kalshi API Integration")
    print("=" * 60)
    print()

    kalshi = Kalshi()
    platform_info = kalshi.get_platform_info()

    print(f"Platform: {platform_info['name']}")
    print(f"Chain: {platform_info['chain']}")
    print(f"Description: {platform_info['description']}")
    print()

    print("Fetching markets from Kalshi...")
    markets = await kalshi.fetch_markets()

    print(f"[OK] Found {len(markets)} active markets")
    print()

    if markets:
        print("Top 10 markets:")
        print("-" * 60)

        for i, market in enumerate(markets[:10], 1):
            # Truncate long titles
            title = market.question[:60] + "..." if len(market.question) > 60 else market.question
            print(f"\n{i}. {title}")
            print(f"   Outcomes: {', '.join(market.outcomes)}")
            print(f"   Odds:")
            for outcome, odds in market.odds.items():
                print(f"     {outcome}: {odds:.2%}")
            print(f"   Volume 24h: ${market.volume_24h:,.2f}")
            if market.liquidity:
                print(f"   Liquidity: ${market.liquidity:,.2f}")

    else:
        print("⚠️  No markets found. This could mean:")
        print("   - API endpoint changed")
        print("   - Network connectivity issue")
        print("   - No active markets at the moment")

    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_kalshi())
