#!/usr/bin/env python3
"""Test script to verify Opinion Labs API integration"""

import asyncio
import os
from markets.opinion_labs import OpinionLabs

async def test_opinion():
    print("=" * 60)
    print("Testing Opinion Labs API Integration")
    print("=" * 60)
    print()

    # Check for API key
    api_key = os.getenv('OPINION_LABS_API_KEY', '')
    if not api_key:
        print("⚠️  No API key found!")
        print()
        print("To use Opinion Labs API:")
        print("1. Go to https://opinion.trade")
        print("2. Connect your wallet and generate an API key")
        print("3. Add it to your .env file:")
        print("   OPINION_LABS_API_KEY=your_api_key_here")
        print()
        return

    opinion = OpinionLabs(api_key=api_key)
    platform_info = opinion.get_platform_info()

    print(f"Platform: {platform_info['name']}")
    print(f"Chain: {platform_info['chain']}")
    print(f"Description: {platform_info['description']}")
    print()

    print("Fetching markets from Opinion Labs...")
    markets = await opinion.fetch_markets()

    print(f"✓ Found {len(markets)} active markets")
    print()

    if markets:
        print("Top 5 markets by volume:")
        print("-" * 60)

        for i, market in enumerate(markets[:5], 1):
            print(f"\n{i}. {market.question}")
            print(f"   Outcomes: {', '.join(market.outcomes)}")
            print(f"   Volume 24h: ${market.volume_24h:,.2f}")

    else:
        print("⚠️  No markets found. This could mean:")
        print("   - API key is invalid")
        print("   - Network connectivity issue")
        print("   - No active markets at the moment")

    print()
    print("=" * 60)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    asyncio.run(test_opinion())
