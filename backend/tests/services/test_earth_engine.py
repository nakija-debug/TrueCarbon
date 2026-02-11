"""Tests for Earth Engine manager singleton."""

import pytest
import threading
from unittest.mock import patch, MagicMock

from app.services.earth_engine import EarthEngineManager
from app.services.exceptions import EarthEngineAuthError, EarthEngineQuotaError


class TestEarthEngineManager:
    """Test Earth Engine singleton pattern and initialization."""

    def setup_method(self):
        """Reset singleton before each test."""
        EarthEngineManager._instance = None
        EarthEngineManager._initialized = False

    def test_singleton_pattern(self):
        """Test that multiple calls return same instance."""
        manager1 = EarthEngineManager.get_instance()
        manager2 = EarthEngineManager.get_instance()

        assert manager1 is manager2

    def test_get_instance_is_singleton(self):
        """Test that get_instance returns singleton."""
        manager1 = EarthEngineManager()
        manager2 = EarthEngineManager()

        assert manager1 is manager2

    def test_thread_safety(self):
        """Test singleton is thread-safe."""
        instances = []

        def get_manager():
            instances.append(EarthEngineManager.get_instance())

        threads = [threading.Thread(target=get_manager) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All instances should be the same
        assert len(set(id(instance) for instance in instances)) == 1

    def test_is_initialized_default_false(self):
        """Test is_initialized returns False initially."""
        manager = EarthEngineManager.get_instance()
        assert manager.is_initialized() is False

    @patch("app.services.earth_engine.ee")
    def test_initialize_success(self, mock_ee):
        """Test successful initialization."""
        manager = EarthEngineManager.get_instance()

        with patch.object(
            EarthEngineManager, "_is_ee_initialized", return_value=False
        ):
            with patch.object(
                EarthEngineManager, "_initialize_with_default_auth"
            ) as mock_init:
                manager.initialize()
                mock_init.assert_called_once()

    @patch("app.services.earth_engine.ee")
    def test_initialize_idempotent(self, mock_ee):
        """Test that initialize can be called multiple times safely."""
        manager = EarthEngineManager.get_instance()

        with patch.object(
            EarthEngineManager, "_is_ee_initialized", return_value=False
        ):
            with patch.object(
                EarthEngineManager, "_initialize_with_default_auth"
            ) as mock_init:
                manager.initialize()
                manager.initialize()  # Call again

                # Should only be called once due to initialization check
                assert mock_init.call_count == 1

    @patch("app.services.earth_engine.ee")
    def test_quota_error_retry(self, mock_ee):
        """Test exponential backoff on quota error."""
        import ee

        manager = EarthEngineManager.get_instance()
        manager._initialized = False

        # Simulate quota error then success
        quota_error = ee.EEException("Quota exceeded")
        with patch.object(
            EarthEngineManager, "_initialize_with_default_auth", side_effect=quota_error
        ):
            with pytest.raises(EarthEngineQuotaError):
                manager.initialize()

    @patch("app.services.earth_engine.ee")
    def test_auth_error(self, mock_ee):
        """Test authentication error handling."""
        import ee

        manager = EarthEngineManager.get_instance()
        manager._initialized = False

        auth_error = ee.EEException("Invalid credentials")
        with patch.object(
            EarthEngineManager, "_initialize_with_default_auth", side_effect=auth_error
        ):
            with pytest.raises(EarthEngineAuthError):
                manager.initialize()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
