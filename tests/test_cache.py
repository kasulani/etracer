"""Tests for the cache module."""

import unittest
import os
import time
import tempfile
import shutil
import json

from etracer.utils import CacheConfig, FileBasedCache
from etracer import CacheData

CACHE_TTL = 86400


class TestCacheConfig(unittest.TestCase):
    """Test the CacheConfig class."""

    def test_init(self):
        """Test the __init__ method."""
        config = CacheConfig()
        self.assertEqual(config.ttl, CACHE_TTL)
        self.assertTrue(config.use_cache)

    def test_configure(self):
        """Test the configure method."""
        # Test setting all values
        config = CacheConfig()
        config.configure(cache_ttl=3600, use_cache=False)
        self.assertEqual(config.ttl, 3600)
        self.assertFalse(config.use_cache)

        # Test setting only some values
        config = CacheConfig()
        config.configure(cache_ttl=7200)
        self.assertEqual(config.ttl, 7200)
        self.assertTrue(config.use_cache)  # Default unchanged

        config = CacheConfig()
        config.configure(use_cache=False)
        self.assertEqual(config.ttl, CACHE_TTL)  # Default unchanged
        self.assertFalse(config.use_cache)


class TestFileBasedCache(unittest.TestCase):
    """Test the FileBasedCache class."""

    def setUp(self):
        """Set up the test."""
        # Create a temporary directory for cache testing
        self._test_cache_dir = tempfile.mkdtemp()
        self._config = CacheConfig()
        self._cache = FileBasedCache(self._config, cache_dir=self._test_cache_dir)

    def tearDown(self):
        """Clean up after the test."""
        # Remove the temporary directory
        shutil.rmtree(self._test_cache_dir)

    def test_init(self):
        """Test the __init__ method."""
        # Test with existing directory
        cache = FileBasedCache(self._config, cache_dir=self._test_cache_dir)
        self.assertEqual(cache._cache_dir, self._test_cache_dir)
        self.assertEqual(cache._ttl, CACHE_TTL)
        self.assertTrue(cache.use_cache)

        # Test with non-existing directory to test directory creation
        new_dir = os.path.join(self._test_cache_dir, "new_cache_dir")
        self.assertFalse(os.path.exists(new_dir))

        cache = FileBasedCache(self._config, cache_dir=new_dir)
        self.assertTrue(os.path.exists(new_dir))
        self.assertEqual(cache._cache_dir, new_dir)

    def test_set_and_get(self):
        """Test the set and get methods."""
        # Create test data
        test_data = CacheData(
            timestamp=time.time(),
            explanation="Test explanation",
            suggested_fix="Test fix",
        )

        # Test set
        self._cache.set("test_key", test_data)
        cache_file = os.path.join(self._test_cache_dir, "test_key.json")
        self.assertTrue(os.path.exists(cache_file))

        # Verify file contents
        with open(cache_file, "r") as f:
            stored_data = json.load(f)
        self.assertIn("timestamp", stored_data)
        self.assertEqual(stored_data["explanation"], "Test explanation")
        self.assertEqual(stored_data["suggested_fix"], "Test fix")

        # Test get
        retrieved_data = self._cache.get("test_key")
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data.explanation, "Test explanation")
        self.assertEqual(retrieved_data.suggested_fix, "Test fix")

        # Test get with non-existent key
        not_found = self._cache.get("non_existent_key")
        self.assertIsNone(not_found)

    def test_expired_cache(self):
        """Test handling of expired cache entries."""
        # Create a cache entry with a timestamp in the past
        expired_time = time.time() - (CACHE_TTL + 10)  # 10 seconds past expiration
        expired_data = CacheData(
            timestamp=expired_time,
            explanation="Expired explanation",
            suggested_fix="Expired fix",
        )

        # Write directly to file
        key = "expired_key"
        cache_file = os.path.join(self._test_cache_dir, f"{key}.json")
        with open(cache_file, "w") as f:
            json.dump(expired_data.model_dump(), f)
        self.assertTrue(os.path.exists(cache_file))

        # Test that get returns None for expired data and removes the file
        result = self._cache.get(key)
        self.assertIsNone(result)
        self.assertFalse(os.path.exists(cache_file))  # File should be removed


if __name__ == "__main__":
    unittest.main()
