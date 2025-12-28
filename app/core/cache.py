"""
Caching utilities for API responses.

Provides in-memory caching with TTL support.
Can be easily extended to use Redis for production/multi-instance deployments.
"""

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class CacheEntry:
    """A cached value with expiration time."""
    value: Any
    expires_at: float
    created_at: float = field(default_factory=time.time)
    
    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    @property
    def ttl_remaining(self) -> float:
        """Remaining TTL in seconds."""
        return max(0, self.expires_at - time.time())


class InMemoryCache:
    """
    Thread-safe in-memory cache with TTL support.
    
    Features:
    - Automatic expiration
    - Periodic cleanup of expired entries
    - Statistics tracking
    - Namespace support for grouping related keys
    """
    
    def __init__(self, cleanup_interval: int = 300):
        """
        Initialize cache.
        
        Args:
            cleanup_interval: Interval in seconds for cleanup task (default: 5 min)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._cleanup_interval = cleanup_interval
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._sets = 0
    
    async def start(self):
        """Start the cleanup background task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Cache cleanup task started")
    
    async def stop(self):
        """Stop the cleanup background task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Cache cleanup task stopped")
    
    async def _cleanup_loop(self):
        """Periodically remove expired entries."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    async def _cleanup_expired(self):
        """Remove all expired entries."""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired
            ]
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                return None
            
            if entry.is_expired:
                del self._cache[key]
                self._misses += 1
                return None
            
            self._hits += 1
            return entry.value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 60
    ) -> None:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: 60)
        """
        async with self._lock:
            self._cache[key] = CacheEntry(
                value=value,
                expires_at=time.time() + ttl,
            )
            self._sets += 1
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if not found
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a prefix pattern.
        
        Args:
            pattern: Key prefix to match
            
        Returns:
            Number of keys deleted
        """
        async with self._lock:
            keys_to_delete = [
                key for key in self._cache.keys() 
                if key.startswith(pattern)
            ]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)
    
    async def clear(self) -> None:
        """Clear all cached entries."""
        async with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")
    
    async def get_or_set(
        self, 
        key: str, 
        factory: Callable[[], T], 
        ttl: int = 60
    ) -> T:
        """
        Get value from cache or compute and cache it.
        
        Args:
            key: Cache key
            factory: Function to compute value if not cached
            ttl: Time-to-live in seconds
            
        Returns:
            Cached or computed value
        """
        value = await self.get(key)
        if value is not None:
            return value
        
        # Compute value
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        await self.set(key, value, ttl)
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "hit_rate": f"{hit_rate:.1f}%",
        }


# Global cache instance
_cache: Optional[InMemoryCache] = None


def get_cache() -> InMemoryCache:
    """Get the global cache instance."""
    global _cache
    if _cache is None:
        _cache = InMemoryCache()
    return _cache


async def init_cache():
    """Initialize and start the cache."""
    cache = get_cache()
    await cache.start()
    logger.info("Cache initialized")


async def shutdown_cache():
    """Shutdown the cache."""
    global _cache
    if _cache:
        await _cache.stop()
        logger.info("Cache shutdown")


def make_cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from arguments.
    
    Args:
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
        
    Returns:
        MD5 hash of the arguments as cache key
    """
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


# Cache TTL constants (in seconds)
class CacheTTL:
    """Standard cache TTL values."""
    
    # Realtime data - short TTL
    REALTIME = 10  # 10 seconds
    MARKET_OVERVIEW = 15  # 15 seconds
    PRICE_BOARD = 10  # 10 seconds
    
    # Intraday data - medium TTL
    INTRADAY = 30  # 30 seconds
    TOP_STOCKS = 60  # 1 minute
    
    # Historical data - longer TTL
    HISTORICAL_RECENT = 300  # 5 minutes (recent data may update)
    HISTORICAL_OLD = 3600  # 1 hour (old data rarely changes)
    
    # Static/slow-changing data - long TTL
    COMPANY_INFO = 3600  # 1 hour
    FINANCIALS = 3600  # 1 hour
    SYMBOL_LIST = 1800  # 30 minutes
    INDUSTRIES = 3600  # 1 hour
    
    # Very static data
    COMPANY_OVERVIEW = 7200  # 2 hours
    OFFICERS = 7200  # 2 hours
    
    # Common Info (Default)
    COMMON_INFO = 3600 # 1 hour
    
    # Analysis Reports (Simplize)
    ANALYSIS_REPORTS = 3600  # 1 hour

    # Technical Analysis (Vietcap IQ)
    TECHNICAL_ANALYSIS = 300  # 5 minutes

    # Macroeconomic data - long TTL (data updates infrequently)
    MACRO = 21600  # 6 hours

    # Commodity prices - medium TTL
    COMMODITY = 1800  # 30 minutes


def cached(
    prefix: str,
    ttl: int = 60,
    key_builder: Optional[Callable[..., str]] = None,
):
    """
    Decorator to cache function results.
    
    Args:
        prefix: Cache key prefix (e.g., "market:overview")
        ttl: Time-to-live in seconds
        key_builder: Optional function to build cache key from args
        
    Example:
        @cached("market:overview", ttl=CacheTTL.MARKET_OVERVIEW)
        async def get_market_overview():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            cache = get_cache()
            
            # Build cache key
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                key_suffix = make_cache_key(*args, **kwargs)
            
            cache_key = f"{prefix}:{key_suffix}" if key_suffix else prefix
            
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Compute value
            logger.debug(f"Cache miss: {cache_key}")
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache the result
            await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cached_method(
    prefix: str,
    ttl: int = 60,
    key_builder: Optional[Callable[..., str]] = None,
):
    """
    Decorator to cache method results (skips self in key generation).
    
    Similar to @cached but for class methods.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> T:
            cache = get_cache()
            
            # Build cache key (skip self)
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                key_suffix = make_cache_key(*args, **kwargs)
            
            cache_key = f"{prefix}:{key_suffix}" if key_suffix else prefix
            
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Compute value
            logger.debug(f"Cache miss: {cache_key}")
            if asyncio.iscoroutinefunction(func):
                result = await func(self, *args, **kwargs)
            else:
                result = func(self, *args, **kwargs)
            
            # Cache the result
            await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
