import re
import logging
from typing import List, Dict, Tuple, Optional, Set
from markets.base import Market
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class ArbitrageOpportunity:
    """Represents an arbitrage opportunity between two markets"""

    def __init__(self, question: str,
                 platform1: str, action1: str, odds1: float,
                 platform2: str, action2: str, odds2: float,
                 profit_percentage: float, volume1: float = 0, volume2: float = 0):
        self.question = question
        self.platform1 = platform1
        self.action1 = action1  # e.g., "Buy Yes"
        self.odds1 = odds1      # Price on platform 1
        self.platform2 = platform2
        self.action2 = action2  # e.g., "Buy No"
        self.odds2 = odds2      # Price on platform 2
        self.profit_percentage = profit_percentage
        self.volume1 = volume1
        self.volume2 = volume2

    def __str__(self):
        return (f"Arbitrage: {self.question}\n"
                f"{self.platform1} ({self.action1}): {self.odds1:.2%} + "
                f"{self.platform2} ({self.action2}): {self.odds2:.2%}\n"
                f"Cost: {self.odds1+self.odds2:.2%} | Profit: {self.profit_percentage:.2%}")

    def get_unique_key(self) -> str:
        """Generate a unique key for deduplication"""
        # Sort platforms to ensure consistent ordering
        if self.platform1 < self.platform2:
            return f"{self.question}|{self.platform1}|{self.platform2}"
        else:
            return f"{self.question}|{self.platform2}|{self.platform1}"

class ArbitrageDetector:
    """Detects arbitrage opportunities across prediction markets"""

    # Pattern to extract years (4-digit numbers between 2020-2030)
    YEAR_PATTERN = re.compile(r'\b(202[0-9]|2030)\b')

    # Pattern to extract dates (various formats)
    DATE_PATTERNS = [
        re.compile(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b'),  # MM/DD/YYYY or DD-MM-YYYY
        re.compile(r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})?\b', re.IGNORECASE),
        re.compile(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december),?\s*(\d{4})?\b', re.IGNORECASE),
        re.compile(r'\bQ([1-4])\s*(\d{4})\b'),  # Q1 2024
    ]

    # Pattern to extract price targets
    PRICE_PATTERN = re.compile(r'\$[\d,]+(?:\.\d+)?[kKmMbB]?|\b[\d,]+(?:\.\d+)?\s*(?:dollars?|usd)\b', re.IGNORECASE)

    def __init__(self, min_profit_threshold: float = 2.0):
        self.min_profit_threshold = min_profit_threshold

    def _extract_years(self, text: str) -> Set[str]:
        """Extract all years from text"""
        return set(self.YEAR_PATTERN.findall(text))

    def _extract_dates(self, text: str) -> List[str]:
        """Extract date-like patterns from text"""
        dates = []
        for pattern in self.DATE_PATTERNS:
            matches = pattern.findall(text)
            dates.extend([str(m) for m in matches])
        return dates

    def _extract_price_targets(self, text: str) -> Set[str]:
        """Extract price targets from text"""
        return set(self.PRICE_PATTERN.findall(text.lower()))

    def _temporal_compatible(self, question1: str, question2: str) -> bool:
        """Check if two questions refer to the same time period"""
        years1 = self._extract_years(question1)
        years2 = self._extract_years(question2)

        # If both have years, they must match
        if years1 and years2:
            if years1 != years2:
                logger.debug(f"Year mismatch: {years1} vs {years2}")
                return False

        # Check for date conflicts
        dates1 = self._extract_dates(question1)
        dates2 = self._extract_dates(question2)

        # If both have specific dates, they should roughly match
        # (This is a simplified check - dates1 and dates2 should have some overlap)
        if dates1 and dates2:
            # For now, just ensure they both have dates (detailed comparison would need normalization)
            pass

        return True

    def _price_target_compatible(self, question1: str, question2: str) -> bool:
        """Check if two questions have compatible price targets"""
        prices1 = self._extract_price_targets(question1)
        prices2 = self._extract_price_targets(question2)

        # If both have price targets, they should match
        if prices1 and prices2:
            if prices1 != prices2:
                logger.debug(f"Price target mismatch: {prices1} vs {prices2}")
                return False

        return True

    def similarity_ratio(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def are_same_event(self, question1: str, question2: str, similarity_threshold: float = 0.75) -> Tuple[bool, float]:
        """
        Determine if two questions refer to the same event.
        Returns (is_match, similarity_score)
        """
        similarity = self.similarity_ratio(question1, question2)

        if similarity < similarity_threshold:
            return False, similarity

        # Additional checks for high-similarity matches
        if not self._temporal_compatible(question1, question2):
            return False, similarity

        if not self._price_target_compatible(question1, question2):
            return False, similarity

        return True, similarity

    def find_matching_markets(self, markets_by_platform: Dict[str, List[Market]],
                             similarity_threshold: float = 0.75) -> List[Tuple]:
        """Find markets with similar questions across platforms"""
        matching_pairs = []

        platforms = list(markets_by_platform.keys())

        for i, platform1 in enumerate(platforms):
            for platform2 in platforms[i+1:]:
                markets1 = markets_by_platform[platform1]
                markets2 = markets_by_platform[platform2]

                for market1 in markets1:
                    for market2 in markets2:
                        is_match, similarity = self.are_same_event(
                            market1.question,
                            market2.question,
                            similarity_threshold
                        )

                        if is_match:
                            matching_pairs.append((platform1, market1, platform2, market2, similarity))

        return matching_pairs

    def _validate_odds(self, odds: float) -> bool:
        """Validate that odds are in acceptable range"""
        if odds is None:
            return False
        try:
            odds_float = float(odds)
            return 0.0 < odds_float < 1.0
        except (TypeError, ValueError):
            return False

    def check_cross_platform_arbitrage(self, price_a: float, price_b: float) -> Optional[float]:
        """
        Check if buying A and B together costs < 1.
        Returns profit percentage if true.
        """
        # Validate inputs
        if not self._validate_odds(price_a) or not self._validate_odds(price_b):
            return None

        total_cost = price_a + price_b
        if total_cost < 1.0 and total_cost > 0:
            # Profit = (Revenue - Cost) / Cost
            # Revenue is always 1 (since one event must happen: Yes or No)
            profit_pct = ((1.0 - total_cost) / total_cost) * 100
            return profit_pct
        return None

    def detect_opportunities(self, markets_by_platform: Dict[str, List[Market]]) -> List[ArbitrageOpportunity]:
        """Detect all arbitrage opportunities across platforms"""
        opportunities = []
        seen_keys: Set[str] = set()  # For deduplication

        matching_markets = self.find_matching_markets(markets_by_platform)

        for platform1, market1, platform2, market2, similarity in matching_markets:
            # We specifically look for Binary Markets (Yes/No)
            # Strategy: Buy Yes on P1 + Buy No on P2 < 1.0
            #       OR  Buy No on P1 + Buy Yes on P2 < 1.0

            p1_yes = market1.odds.get('Yes')
            p1_no = market1.odds.get('No')
            p2_yes = market2.odds.get('Yes')
            p2_no = market2.odds.get('No')

            # Scenario 1: Buy Yes @ P1 + Buy No @ P2
            if self._validate_odds(p1_yes) and self._validate_odds(p2_no):
                profit = self.check_cross_platform_arbitrage(p1_yes, p2_no)
                if profit and profit >= self.min_profit_threshold:
                    opp = ArbitrageOpportunity(
                        question=market1.question,
                        platform1=platform1,
                        action1="Buy Yes",
                        odds1=p1_yes,
                        platform2=platform2,
                        action2="Buy No",
                        odds2=p2_no,
                        profit_percentage=profit,
                        volume1=market1.volume_24h or 0,
                        volume2=market2.volume_24h or 0
                    )
                    # Deduplication check
                    key = opp.get_unique_key()
                    if key not in seen_keys:
                        seen_keys.add(key)
                        opportunities.append(opp)

            # Scenario 2: Buy No @ P1 + Buy Yes @ P2
            if self._validate_odds(p1_no) and self._validate_odds(p2_yes):
                profit = self.check_cross_platform_arbitrage(p1_no, p2_yes)
                if profit and profit >= self.min_profit_threshold:
                    opp = ArbitrageOpportunity(
                        question=market1.question,
                        platform1=platform1,
                        action1="Buy No",
                        odds1=p1_no,
                        platform2=platform2,
                        action2="Buy Yes",
                        odds2=p2_yes,
                        profit_percentage=profit,
                        volume1=market1.volume_24h or 0,
                        volume2=market2.volume_24h or 0
                    )
                    # Deduplication check
                    key = opp.get_unique_key()
                    if key not in seen_keys:
                        seen_keys.add(key)
                        opportunities.append(opp)

        # Sort by profit percentage descending
        opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)

        return opportunities
