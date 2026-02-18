"""Pytest configuration and fixtures for backend tests."""

import os
import sys

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


def pytest_configure(config):
    """Configure pytest before test collection."""
    # Set environment variables BEFORE any imports of the app
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    os.environ.setdefault("SECRET_KEY", "test-secret-key-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    os.environ.setdefault("GEE_PROJECT", "test-gee-project")
    os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture
def test_settings():
    """Return test settings."""
    from app.core.config import settings
    return settings


