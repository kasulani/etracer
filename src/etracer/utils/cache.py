"""
Cache implementations for etracer.
"""

import json
import os
import time
from typing import Optional, Union

from ..interfaces import CacheInterface
from ..models import CacheData

# Cache settings
_CACHE_DIR = os.path.join(os.getcwd(), ".tracer_cache")  # Local to project directory
_CACHE_TTL = 86400  # Time-to-live in seconds (24 hours)


class CacheConfig:
    """Configuration for cache settings."""

    def __init__(self) -> None:
        self.ttl: int = _CACHE_TTL  # Time-to-live for cache entries in seconds
        self.use_cache: bool = True  # Whether to use caching for AI responses

    def configure(self, cache_ttl: Optional[int] = None, use_cache: Optional[bool] = None) -> None:
        """Configure the cache settings."""
        if cache_ttl is not None:
            self.ttl = cache_ttl
        if use_cache is not None:
            self.use_cache = use_cache


class FileBasedCache(CacheInterface):
    """File-based cache implementation for storing AI responses."""

    def __init__(self, config: CacheConfig, cache_dir: str = _CACHE_DIR):
        self._cache_dir = cache_dir
        self._ttl = config.ttl  # Time-to-live for cache entries in seconds
        self.use_cache = config.use_cache  # Whether to use caching for AI responses

        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)

    def set(self, key: str, value: CacheData) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
        """
        cache_file = os.path.join(self._cache_dir, f"{key}.json")
        with open(cache_file, "w") as f:
            json.dump(value.model_dump(), f)

    def get(self, key: str) -> Union[CacheData, None]:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value or None if not found or expired
        """
        cache_file = os.path.join(self._cache_dir, f"{key}.json")
        if not os.path.exists(cache_file):
            return None

        with open(cache_file, "r") as f:
            data = CacheData.model_validate(json.load(f))

        if time.time() - data.timestamp > self._ttl:
            os.remove(cache_file)

        return data if time.time() - data.timestamp <= self._ttl else None
