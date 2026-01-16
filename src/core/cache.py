"""Caching utilities for Jira agent"""
from functools import lru_cache, wraps
from typing import Any, Callable, Optional
import time


class TTLCache:
    """Simple Time-To-Live cache implementation"""
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize TTL cache.
        
        Args:
            ttl_seconds: Time to live in seconds (default: 5 minutes)
        """
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None
        
        # Check if expired
        if time.time() - self._timestamps[key] > self.ttl_seconds:
            # Expired, remove it
            del self._cache[key]
            del self._timestamps[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cached values"""
        self._cache.clear()
        self._timestamps.clear()
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        return self.get(key) is not None


def ttl_cache(ttl_seconds: int = 300):
    """
    Decorator for caching function results with TTL.
    
    Args:
        ttl_seconds: Time to live in seconds
    
    Example:
        @ttl_cache(ttl_seconds=60)
        def get_user(user_id):
            return fetch_user_from_api(user_id)
    """
    cache = TTLCache(ttl_seconds=ttl_seconds)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Not in cache, compute value
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result)
            
            return result
        
        # Add cache control methods
        wrapper.cache_clear = cache.clear
        wrapper.cache = cache
        
        return wrapper
    
    return decorator


# Global caches for specific use cases
user_cache = TTLCache(ttl_seconds=600)  # 10 minutes for user data
config_cache = TTLCache(ttl_seconds=3600)  # 1 hour for config


@lru_cache(maxsize=1)
def get_singleton_client():
    """
    Get singleton Jira client instance.
    Uses LRU cache with maxsize=1 to create only one instance.
    """
    from .client import JiraClient
    return JiraClient()
