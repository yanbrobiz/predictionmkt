#!/usr/bin/env python3
"""Test script to verify Drift BET API integration"""

import asyncio
from markets.drift_bet import DriftBET

async def test_drift():
    print("=" * 60)
    print("Testing Drift BET API Integration")
    print("=" * 60)
    print()

    drift = DriftBET()
    platform_info = drift.get_platform_info()

    print(f"Platform: {platform_info['name']}")
    print(f"Chain: {platform_info['chain']}")
    print(f"Description: {platform_info['description']}")
    print()

    print("Fetching prediction markets from Drift BET...")
    markets = await drift.fetch_markets()

    print(f"[OK] Found {len(markets)} prediction markets")
    print()

    if markets:
        print("Prediction markets found:")
        print("-" * 60)

        for i, market in enumerate(markets[:10], 1):
            print(f"\n{i}. {market.question}")
            print(f"   Outcomes: {', '.join(market.outcomes)}")
            print(f"   Odds:")
            for outcome, odds in market.odds.items():
                print(f"     {outcome}: {odds:.2%}")
            print(f"   Volume 24h: ${market.volume_24h:,.2f}")
            if market.liquidity:
                print(f"   Open Interest: ${market.liquidity:,.2f}")

    else:
        print("⚠️  No prediction markets found. This could mean:")
        print("   - No active prediction markets at the moment")
        print("   - API structure changed")
        print("   - Network connectivity issue")

    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_drift())
