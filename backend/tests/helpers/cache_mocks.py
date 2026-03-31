"""Centralized mock helpers for cache tests."""
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import contextmanager


@contextmanager
def mock_cache_layers(*, supabase_result=None, redis_result=None, local_result=None):
    """Context manager that mocks all cache layers for testing."""
    with patch("cache.supabase._get_from_supabase", new_callable=AsyncMock, return_value=supabase_result) as mock_supa, \
         patch("cache.redis._get_from_redis", return_value=redis_result) as mock_redis, \
         patch("cache.local_file._get_from_local", return_value=local_result) as mock_local:
        yield {"supabase": mock_supa, "redis": mock_redis, "local": mock_local}


@contextmanager
def mock_cache_save():
    """Mock all cache save operations."""
    with patch("cache.supabase._save_to_supabase", new_callable=AsyncMock) as mock_supa, \
         patch("cache.redis._save_to_redis") as mock_redis, \
         patch("cache.local_file._save_to_local") as mock_local:
        yield {"supabase": mock_supa, "redis": mock_redis, "local": mock_local}
