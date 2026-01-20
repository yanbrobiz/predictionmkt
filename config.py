import os
from typing import Set
from dotenv import load_dotenv

load_dotenv()


def _parse_categories(env_value: str) -> Set[str]:
    """
    Parse ALLOWED_CATEGORIES from environment variable.
    Format: comma-separated values, e.g., "sports,crypto"
    Empty string or "all" means all categories (no filtering).
    """
    if not env_value or env_value.lower() == 'all':
        return set()

    categories = set()
    for cat in env_value.split(','):
        cat = cat.strip().lower()
        if cat in ('sports', 'crypto'):
            categories.add(cat)
    return categories


class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    # Monitoring
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL_SECONDS', 30))
    MIN_PROFIT_THRESHOLD = float(os.getenv('MIN_PROFIT_THRESHOLD', 0.1))

    # API Keys
    POLYMARKET_API_KEY = os.getenv('POLYMARKET_API_KEY', '')
    DRIFT_API_KEY = os.getenv('DRIFT_API_KEY', '')
    LIMITLESS_API_KEY = os.getenv('LIMITLESS_API_KEY', '')
    MYRIAD_API_KEY = os.getenv('MYRIAD_API_KEY', '')
    OPINION_LABS_API_KEY = os.getenv('OPINION_LABS_API_KEY', '')

    # RPC Endpoints
    POLYGON_RPC = os.getenv('POLYGON_RPC', 'https://polygon-rpc.com')
    SOLANA_RPC = os.getenv('SOLANA_RPC', 'https://api.mainnet-beta.solana.com')
    BASE_RPC = os.getenv('BASE_RPC', 'https://mainnet.base.org')

    # Market Platforms
    PLATFORMS = [
        {'name': 'Polymarket', 'chain': 'Polygon', 'enabled': True},
        {'name': 'Drift BET', 'chain': 'Solana', 'enabled': True},
        {'name': 'Limitless', 'chain': 'Base', 'enabled': True},
        {'name': 'Myriad', 'chain': 'Abstract/EVM', 'enabled': True},
        {'name': 'Opinion Labs', 'chain': 'Multi-chain', 'enabled': True},
    ]

    # Category Filtering - only monitor these market categories
    # Available: 'sports', 'crypto'
    # Set via environment variable: ALLOWED_CATEGORIES=sports,crypto
    # Use "all" or empty string to monitor all categories
    # Default: sports and crypto only
    ALLOWED_CATEGORIES = _parse_categories(os.getenv('ALLOWED_CATEGORIES', 'sports,crypto'))
