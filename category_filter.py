"""
Category filter for prediction markets.
Filters markets based on keyword matching for sports and crypto categories.
"""

from typing import List, Optional, Set

class CategoryFilter:
    """Filter markets by category using keyword matching"""
    
    # Category keyword mappings
    CATEGORY_KEYWORDS = {
        'sports': {
            # Major leagues
            'nba', 'nfl', 'mlb', 'nhl', 'mls', 'f1', 'formula 1', 'formula one',
            'premier league', 'la liga', 'bundesliga', 'serie a', 'champions league',
            # Sports types
            'soccer', 'football', 'basketball', 'baseball', 'hockey', 'tennis',
            'golf', 'boxing', 'ufc', 'mma', 'wrestling', 'cricket', 'rugby',
            'volleyball', 'swimming', 'athletics', 'olympics',
            # Events
            'world cup', 'super bowl', 'playoffs', 'championship', 'tournament',
            'finals', 'match', 'game vs', 'win game', 'world series',
            # Teams/Players context
            'lakers', 'celtics', 'warriors', 'bulls', 'heat', 'nets',
            'cowboys', 'patriots', 'chiefs', 'eagles', '49ers',
            'yankees', 'dodgers', 'red sox', 'mets', 'cubs',
            'manchester', 'liverpool', 'arsenal', 'chelsea', 'barcelona', 'real madrid',
        },
        'crypto': {
            # Major coins
            'bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol', 'xrp', 'ripple',
            'cardano', 'ada', 'dogecoin', 'doge', 'polkadot', 'dot', 'avalanche', 'avax',
            'chainlink', 'link', 'polygon', 'matic', 'litecoin', 'ltc', 'shiba', 'shib',
            'uniswap', 'uni', 'aave', 'maker', 'mkr', 'compound', 'comp',
            # General terms
            'crypto', 'cryptocurrency', 'token', 'coin', 'defi', 'nft',
            'blockchain', 'web3', 'binance', 'coinbase', 'kraken',
            'memecoin', 'meme coin', 'altcoin', 'stablecoin',
            # Price related
            'ath', 'all time high', 'market cap', 'mcap',
        }
    }
    
    @classmethod
    def categorize_market(cls, question: str) -> Optional[str]:
        """
        Determine the category of a market based on its question.
        Returns 'sports', 'crypto', or None if no match.
        """
        question_lower = question.lower()
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in question_lower:
                    return category
        
        return None
    
    @classmethod
    def filter_markets(cls, markets: List, allowed_categories: Set[str]) -> List:
        """
        Filter markets to only include those matching allowed categories.
        
        Args:
            markets: List of Market objects
            allowed_categories: Set of category names to include ('sports', 'crypto')
            
        Returns:
            Filtered list of markets
        """
        if not allowed_categories:
            return markets
        
        filtered = []
        for market in markets:
            category = cls.categorize_market(market.question)
            if category in allowed_categories:
                filtered.append(market)
        
        return filtered
    
    @classmethod
    def get_category_stats(cls, markets: List) -> dict:
        """Get count of markets per category"""
        stats = {'sports': 0, 'crypto': 0, 'other': 0}
        
        for market in markets:
            category = cls.categorize_market(market.question)
            if category:
                stats[category] += 1
            else:
                stats['other'] += 1
        
        return stats
