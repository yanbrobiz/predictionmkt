import asyncio
from telegram import Bot
from telegram.error import TelegramError
from typing import List
from arbitrage_detector import ArbitrageOpportunity
from config import Config

class TelegramNotifier:
    """Sends arbitrage alerts via Telegram"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

    def format_message(self, opportunity: ArbitrageOpportunity, index: int, total: int) -> str:
        """Format arbitrage opportunity as Telegram message"""

        # Calculate star rating based on profit percentage
        if opportunity.profit_percentage > 2.0:
            stars = 5
        elif opportunity.profit_percentage > 1.0:
            stars = 3
        elif opportunity.profit_percentage > 0.5:
            stars = 2
        else:
            stars = 1
            
        star_emoji = "⭐" * stars

        # Format volumes
        vol1_str = self._format_volume(opportunity.volume1)
        vol2_str = self._format_volume(opportunity.volume2)

        message = f"📊 <b>套利機會 ({index}/{total})</b>\n\n"
        message += f"<b>{opportunity.question}</b>\n\n"
        message += f"🔥 此對沖策略必勝 (Yes+No < 1)\n"
        message += f"星等：{star_emoji}\n"
        message += f"💰 利潤：<b>{opportunity.profit_percentage:.4f}%</b>\n\n"
        
        message += f"👇 操作指南：\n"
        message += f"1. 在 <b>{opportunity.platform1}</b> 買入 <b>{opportunity.action1.split()[-1]}</b>\n"
        message += f"   價格: ${opportunity.odds1:.3f}\n"
        message += f"2. 在 <b>{opportunity.platform2}</b> 買入 <b>{opportunity.action2.split()[-1]}</b>\n"
        message += f"   價格: ${opportunity.odds2:.3f}\n\n"
        
        total_cost = opportunity.odds1 + opportunity.odds2
        
        message += f"💵總成本: ${total_cost:.3f}\n"
        
        message += f"💹 交易量24H：\n"
        message += f"  • {opportunity.platform1}: {vol1_str}\n"
        message += f"  • {opportunity.platform2}: {vol2_str}\n"

        return message

    def _format_volume(self, volume: float) -> str:
        """Format volume to human readable string"""
        if volume >= 1_000_000:
            return f"${volume/1_000_000:.2f}M"
        elif volume >= 1_000:
            return f"${volume/1_000:.2f}K"
        else:
            return f"${volume:.2f}"

    async def send_alert(self, opportunity: ArbitrageOpportunity, index: int = 1, total: int = 1):
        """Send a single arbitrage alert"""
        try:
            message = self.format_message(opportunity, index, total)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            print(f"[OK] Alert sent for: {opportunity.question[:50]}...")
        except TelegramError as e:
            print(f"[FAIL] Failed to send Telegram message: {e}")

    async def send_alerts(self, opportunities: List[ArbitrageOpportunity]):
        """Send multiple arbitrage alerts"""
        if not opportunities:
            print("No arbitrage opportunities to send")
            return

        total = len(opportunities)
        print(f"Sending {total} arbitrage alert(s)...")

        for i, opportunity in enumerate(opportunities, 1):
            await self.send_alert(opportunity, i, total)
            # Small delay between messages to avoid rate limiting
            if i < total:
                await asyncio.sleep(1)

    async def send_test_message(self):
        """Send a test message to verify bot setup"""
        try:
            message = "🤖 預測市場套利監測機器人已啟動\n\n"
            message += "✅ Telegram 連接成功\n"
            message += f"📊 監控頻率：每 {Config.CHECK_INTERVAL} 秒\n"
            message += f"💰 利潤門檻：{Config.MIN_PROFIT_THRESHOLD}%\n"

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            print("[OK] Test message sent successfully")
            return True
        except TelegramError as e:
            print(f"[FAIL] Failed to send test message: {e}")
            return False
