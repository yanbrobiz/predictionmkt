#!/usr/bin/env python3
"""Test script to verify Limitless API integration"""

import asyncio
from markets.limitless import Limitless

async def test_limitless():
    print("=" * 60)
    print("Testing Limitless API Integration")
    print("=" * 60)
    print()

    limitless = Limitless()
    platform_info = limitless.get_platform_info()

    print(f"Platform: {platform_info['name']}")
    print(f"Chain: {platform_info['chain']}")
    print(f"Description: {platform_info['description']}")
    print()

    print("Fetching markets from Limitless...")
    markets = await limitless.fetch_markets()

    print(f"✓ Found {len(markets)} active markets")
    print()

    if markets:
        print("Top 5 markets by volume:")
        print("-" * 60)

        for i, market in enumerate(markets[:5], 1):
            print(f"\n{i}. {market.question}")
            print(f"   Outcomes: {', '.join(market.outcomes)}")
            print(f"   Odds:")
            for outcome, odds in market.odds.items():
                print(f"     {outcome}: {odds:.2%}")
            print(f"   Volume 24h: ${market.volume_24h:,.2f}")
            print(f"   Liquidity: ${market.liquidity:,.2f}")

    else:
        print("⚠️  No markets found. This could mean:")
        print("   - API endpoint changed")
        print("   - Network connectivity issue")
        print("   - No active markets at the moment")

    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_limitless())
