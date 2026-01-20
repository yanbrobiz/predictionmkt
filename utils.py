"""
Utility functions for the prediction market arbitrage monitor.
"""
import asyncio
import aiohttp
import logging
from typing import Optional, Any, Dict
from functools import wraps

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def fetch_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    *,
    method: str = "GET",
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    max_retries: int = 3,
    base_delay: float = 1.0,
    timeout: int = 15
) -> Optional[Any]:
    """
    Fetch URL with exponential backoff retry.

    Args:
        session: aiohttp ClientSession
        url: URL to fetch
        method: HTTP method (GET, POST, etc.)
        params: Query parameters
        headers: HTTP headers
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (will be multiplied exponentially)
        timeout: Request timeout in seconds

    Returns:
        JSON response or None on failure
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            async with session.request(
                method,
                url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limited - use longer delay
                    delay = base_delay * (2 ** attempt) * 2
                    logger.warning(f"Rate limited on {url}, waiting {delay}s before retry")
                    await asyncio.sleep(delay)
                    continue
                elif response.status >= 500:
                    # Server error - retry
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Server error {response.status} on {url}, retrying in {delay}s")
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Client error - don't retry
                    logger.error(f"Client error {response.status} on {url}")
                    return None

        except asyncio.TimeoutError:
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Timeout on {url}, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
            last_error = "Timeout"
            await asyncio.sleep(delay)

        except aiohttp.ClientError as e:
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Client error on {url}: {e}, retrying in {delay}s")
            last_error = str(e)
            await asyncio.sleep(delay)

        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            last_error = str(e)
            break

    logger.error(f"Failed to fetch {url} after {max_retries} attempts. Last error: {last_error}")
    return None


class SessionManager:
    """
    Manages a shared aiohttp ClientSession for all platforms.
    Usage:
        async with SessionManager() as manager:
            session = manager.session
            # use session...
    """
    _instance: Optional['SessionManager'] = None
    _session: Optional[aiohttp.ClientSession] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def __aenter__(self) -> 'SessionManager':
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'PredictionMarketArbitrageMonitor/1.0'
                }
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Don't close on context exit - let it be reused
        pass

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError("SessionManager not initialized. Use 'async with SessionManager()' first.")
        return self._session

    async def close(self):
        """Explicitly close the session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None


def setup_logging(level: int = logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
