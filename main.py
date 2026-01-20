#!/usr/bin/env python3
import asyncio
import aiohttp
import logging
import time
from datetime import datetime
from typing import Dict, List

from config import Config
from markets.polymarket import Polymarket
from markets.drift_bet import DriftBET
from markets.limitless import Limitless
from markets.myriad import Myriad
from markets.opinion_labs import OpinionLabs
from markets.kalshi import Kalshi
from markets.base import Market
from arbitrage_detector import ArbitrageDetector
from telegram_notifier import TelegramNotifier
from category_filter import CategoryFilter
from utils import setup_logging

# Setup logging
setup_logging(logging.INFO)
logger = logging.getLogger(__name__)


class ArbitrageMonitor:
    """Main arbitrage monitoring system"""

    def __init__(self):
        self.platforms = [
            Polymarket(),
            DriftBET(),
            Limitless(),
            Myriad(),
            OpinionLabs(),
            Kalshi()
        ]
        self.detector = ArbitrageDetector(min_profit_threshold=Config.MIN_PROFIT_THRESHOLD)
        self.notifier = None
        self._session: aiohttp.ClientSession = None

        # Initialize Telegram notifier if credentials are provided
        if Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID:
            self.notifier = TelegramNotifier(
                bot_token=Config.TELEGRAM_BOT_TOKEN,
                chat_id=Config.TELEGRAM_CHAT_ID
            )

    async def _ensure_session(self):
        """Ensure we have an active session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'PredictionMarketArbitrageMonitor/1.0'}
            )
            # Set session for all platforms
            for platform in self.platforms:
                platform.set_session(self._session)

    async def _close_session(self):
        """Close the shared session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def fetch_all_markets(self) -> Dict[str, List[Market]]:
        """Fetch markets from all platforms concurrently"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching markets from all platforms...")

        # Ensure we have a shared session
        await self._ensure_session()

        tasks = []
        platform_names = []

        for platform in self.platforms:
            tasks.append(platform.fetch_markets())
            platform_names.append(platform.name)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        markets_by_platform = {}
        total_markets_before = 0
        total_markets_after = 0

        for platform_name, result in zip(platform_names, results):
            if isinstance(result, Exception):
                logger.error(f"{platform_name}: Error - {result}")
                print(f"  [ERROR] {platform_name}: Error - {result}")
                markets_by_platform[platform_name] = []
            else:
                # Apply category filtering
                raw_count = len(result)
                filtered_markets = CategoryFilter.filter_markets(result, Config.ALLOWED_CATEGORIES)
                filtered_count = len(filtered_markets)

                total_markets_before += raw_count
                total_markets_after += filtered_count

                markets_by_platform[platform_name] = filtered_markets

                if Config.ALLOWED_CATEGORIES:
                    print(f"  [OK] {platform_name}: {filtered_count} markets (filtered from {raw_count})")
                else:
                    print(f"  [OK] {platform_name}: {filtered_count} markets")

        if Config.ALLOWED_CATEGORIES:
            categories_str = ', '.join(Config.ALLOWED_CATEGORIES)
            print(f"  [Filter] Retained {total_markets_after} / {total_markets_before} markets ({categories_str})")

        return markets_by_platform

    async def scan_for_arbitrage(self):
        """Scan all platforms for arbitrage opportunities"""
        start_time = time.time()

        # Fetch markets from all platforms
        markets_by_platform = await self.fetch_all_markets()

        # Detect arbitrage opportunities
        opportunities = self.detector.detect_opportunities(markets_by_platform)

        elapsed = time.time() - start_time
        print(f"  Scan completed in {elapsed:.2f}s")
        print(f"  Found {len(opportunities)} arbitrage opportunities")

        # Send alerts if opportunities found
        if opportunities and self.notifier:
            await self.notifier.send_alerts(opportunities)

        return opportunities

    async def run_once(self):
        """Run a single scan cycle"""
        try:
            opportunities = await self.scan_for_arbitrage()
            return opportunities
        except Exception as e:
            print(f"Error during scan: {e}")
            return []

    async def run_continuous(self):
        """Run continuous monitoring"""
        print("=" * 60)
        print("[START] Prediction Market Arbitrage Monitor Started")
        print("=" * 60)
        print(f"Check interval: {Config.CHECK_INTERVAL} seconds")
        print(f"Profit threshold: {Config.MIN_PROFIT_THRESHOLD}%")
        print(f"Monitoring platforms: {', '.join([p.name for p in self.platforms])}")
        print("=" * 60)

        # Send test message
        if self.notifier:
            test_success = await self.notifier.send_test_message()
            if not test_success:
                print("[WARNING] Failed to send test message. Check your Telegram configuration.")
        else:
            print("[WARNING] Telegram notifier not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")

        print("\nStarting monitoring loop...\n")

        cycle = 0
        while True:
            cycle += 1
            print(f"\n{'='*60}")
            print(f"Scan Cycle #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")

            await self.run_once()

            print(f"\nNext scan in {Config.CHECK_INTERVAL} seconds...")
            await asyncio.sleep(Config.CHECK_INTERVAL)

async def main():
    """Main entry point"""
    monitor = ArbitrageMonitor()

    try:
        await monitor.run_continuous()
    except KeyboardInterrupt:
        print("\n\n[BYE] Shutting down monitor...")
    finally:
        # Clean up shared session
        await monitor._close_session()
        print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
